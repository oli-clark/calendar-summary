"""
Google Calendar API client for fetching calendar events.

This module handles authentication with Google Calendar API and fetching events
for specified date ranges. It filters out declined meetings and handles OAuth2
authentication flow.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

from config import Config


# If modifying these scopes, delete the token.json file.
# This scope allows read-only access to calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarClient:
    """
    Client for interacting with Google Calendar API.

    Handles authentication, token management, and fetching calendar events
    with various filtering options.
    """

    def __init__(self):
        """Initialize the calendar client and authenticate."""
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with Google Calendar API using OAuth2.

        The first time this runs, it will open a browser window for authorization.
        Subsequent runs will use the saved token from token.json.
        """
        # Check if we have a saved token from previous authentication
        if os.path.exists(Config.GOOGLE_CALENDAR_TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(
                Config.GOOGLE_CALENDAR_TOKEN_PATH,
                SCOPES
            )

        # If there are no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Token expired but can be refreshed
                if Config.VERBOSE:
                    print("Refreshing expired Google Calendar credentials...")
                self.creds.refresh(Request())
            else:
                # Need to do full OAuth flow (opens browser)
                if Config.VERBOSE:
                    print("Starting Google Calendar OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CALENDAR_CREDENTIALS_PATH,
                    SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(Config.GOOGLE_CALENDAR_TOKEN_PATH, 'w') as token:
                token.write(self.creds.to_json())

        # Build the Calendar API service
        self.service = build('calendar', 'v3', credentials=self.creds)
        if Config.VERBOSE:
            print("✓ Google Calendar API authenticated successfully")

    def get_events(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        days_ahead: int = 7,
        calendar_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events for a specified date range.

        Args:
            start_date: Start date for fetching events (defaults to now)
            end_date: End date for fetching events (calculated from days_ahead if not provided)
            days_ahead: Number of days to look ahead (default: 7)
            calendar_id: Calendar ID to fetch from (defaults to Config.CALENDAR_ID)

        Returns:
            List of event dictionaries with relevant information

        The returned events include:
        - summary (event title)
        - start/end times
        - description
        - attendees and response status
        - location
        - event type (all-day vs timed)
        """
        if calendar_id is None:
            calendar_id = Config.CALENDAR_ID

        # Set default date range if not provided
        if start_date is None:
            start_date = datetime.now(pytz.UTC)
        if end_date is None:
            end_date = start_date + timedelta(days=days_ahead)

        # Convert to RFC3339 format required by Google Calendar API
        time_min = start_date.isoformat()
        time_max = end_date.isoformat()

        if Config.VERBOSE:
            print(f"Fetching events from {start_date.date()} to {end_date.date()}...")

        try:
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,  # Expand recurring events into individual instances
                orderBy='startTime'  # Sort by start time
            ).execute()

            events = events_result.get('items', [])

            # Filter out declined meetings and process events
            filtered_events = []
            for event in events:
                # Check if user has declined this event
                if self._is_declined(event):
                    if Config.VERBOSE:
                        print(f"  Skipping declined event: {event.get('summary', 'No title')}")
                    continue

                # Process and add to filtered list
                filtered_events.append(self._process_event(event))

            if Config.VERBOSE:
                print(f"✓ Fetched {len(filtered_events)} events (filtered out declined)")

            return filtered_events

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def _is_declined(self, event: Dict[str, Any]) -> bool:
        """
        Check if the authenticated user has declined this event.

        Args:
            event: Event dictionary from Google Calendar API

        Returns:
            True if user declined, False otherwise
        """
        attendees = event.get('attendees', [])
        for attendee in attendees:
            # Check if this is the authenticated user and they declined
            if attendee.get('self', False) and attendee.get('responseStatus') == 'declined':
                return True
        return False

    def _process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a raw event from Google Calendar API into a cleaner format.

        Args:
            event: Raw event dictionary from API

        Returns:
            Processed event dictionary with standardized fields
        """
        # Extract start and end times
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        # Determine if this is an all-day event
        is_all_day = 'date' in event['start']

        # Get attendees (excluding the user)
        attendees = []
        for attendee in event.get('attendees', []):
            if not attendee.get('self', False):
                attendees.append({
                    'email': attendee.get('email'),
                    'name': attendee.get('displayName', attendee.get('email')),
                    'status': attendee.get('responseStatus')
                })

        return {
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'start': start,
            'end': end,
            'is_all_day': is_all_day,
            'location': event.get('location', ''),
            'attendees': attendees,
            'organizer': event.get('organizer', {}).get('displayName', 'Unknown'),
            'html_link': event.get('htmlLink', '')
        }

    def get_weekly_events(self) -> List[Dict[str, Any]]:
        """
        Get events for the next 7 days (detailed weekly summary).

        Returns:
            List of events for the upcoming week
        """
        return self.get_events(days_ahead=7)

    def get_monthly_events(self) -> List[Dict[str, Any]]:
        """
        Get events for the next 30 days (for monthly look-ahead).

        Returns:
            List of events for the upcoming month
        """
        return self.get_events(days_ahead=30)
