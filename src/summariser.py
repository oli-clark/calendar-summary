"""
Claude API client for generating intelligent calendar summaries.

This module uses Claude API to analyze calendar events and generate
conversational, insightful summaries for weekly and monthly views.
"""

import json
from typing import List, Dict, Any
from datetime import datetime

import anthropic
from config import Config


class CalendarSummariser:
    """
    Client for generating intelligent calendar summaries using Claude API.

    Loads a customizable prompt template and processes calendar events to
    create helpful, conversational summaries.
    """

    def __init__(self):
        """Initialize the Claude API client."""
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.prompt_template = self._load_prompt_template()

        if Config.VERBOSE:
            print("✓ Claude API client initialized")

    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from the prompts directory.

        Returns:
            The prompt template as a string

        Raises:
            FileNotFoundError: If the prompt template file doesn't exist
        """
        try:
            with open(Config.PROMPT_TEMPLATE_PATH, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Provide a default prompt if file doesn't exist
            print(f"Warning: Prompt template not found at {Config.PROMPT_TEMPLATE_PATH}")
            print("Using default prompt template.")
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """
        Provide a default prompt template if the file doesn't exist.

        Returns:
            Default prompt template string
        """
        return """You are a helpful personal assistant analyzing a calendar for the week ahead.

Your task is to:
1. Summarize the upcoming week in a conversational, concise tone
2. Group related meetings meaningfully
3. Highlight any scheduling issues or conflicts (back-to-back meetings, etc.)
4. Suggest preparation needs for important events
5. For monthly look-ahead items: surface genuinely important items like deadlines, reminders, birthdays, or special occasions

Keep the tone helpful and conversational - like a smart assistant who knows the schedule well.
Avoid being robotic or overly formal. Be concise but insightful."""

    def _format_events_for_claude(
        self,
        weekly_events: List[Dict[str, Any]],
        monthly_events: List[Dict[str, Any]] = None
    ) -> str:
        """
        Format calendar events into a readable string for Claude.

        Args:
            weekly_events: Events for the next 7 days
            monthly_events: Events for the next 30 days (optional)

        Returns:
            Formatted string representation of events
        """
        output = "=== WEEKLY EVENTS (Next 7 Days) ===\n\n"

        if not weekly_events:
            output += "No events scheduled for the next week.\n"
        else:
            for event in weekly_events:
                output += self._format_single_event(event)
                output += "\n"

        # Add monthly look-ahead if provided
        if monthly_events:
            # Filter to only events beyond the weekly range
            weekly_end = None
            if weekly_events:
                weekly_end = datetime.fromisoformat(
                    weekly_events[-1]['start'].replace('Z', '+00:00')
                )

            future_events = []
            for event in monthly_events:
                event_start = datetime.fromisoformat(
                    event['start'].replace('Z', '+00:00')
                )
                if weekly_end and event_start > weekly_end:
                    future_events.append(event)

            if future_events:
                output += "\n=== MONTHLY LOOK-AHEAD (Important Items Beyond This Week) ===\n\n"
                for event in future_events:
                    output += self._format_single_event(event)
                    output += "\n"

        return output

    def _format_single_event(self, event: Dict[str, Any]) -> str:
        """
        Format a single event into a readable string.

        Args:
            event: Event dictionary

        Returns:
            Formatted event string
        """
        summary = event.get('summary', 'No Title')
        start = event.get('start', '')
        end = event.get('end', '')
        is_all_day = event.get('is_all_day', False)
        description = event.get('description', '')
        location = event.get('location', '')
        attendees = event.get('attendees', [])

        # Format date/time
        if is_all_day:
            date_str = start.split('T')[0] if 'T' in start else start
            time_str = f"{date_str} (All Day)"
        else:
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                time_str = f"{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}"
            except:
                time_str = f"{start} - {end}"

        # Build event string
        event_str = f"• {summary}\n"
        event_str += f"  Time: {time_str}\n"

        if location:
            event_str += f"  Location: {location}\n"

        if description:
            # Truncate long descriptions
            desc_preview = description[:200] + "..." if len(description) > 200 else description
            event_str += f"  Description: {desc_preview}\n"

        if attendees:
            attendee_count = len(attendees)
            event_str += f"  Attendees: {attendee_count} people\n"

        return event_str

    def generate_summary(
        self,
        weekly_events: List[Dict[str, Any]],
        monthly_events: List[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an intelligent summary of calendar events using Claude API.

        Args:
            weekly_events: Events for the next 7 days
            monthly_events: Events for the next 30 days (optional)

        Returns:
            Generated summary as a string
        """
        # Format events for Claude
        events_text = self._format_events_for_claude(weekly_events, monthly_events)

        # Prepare the prompt
        user_message = f"{self.prompt_template}\n\n{events_text}"

        if Config.VERBOSE:
            print("Generating summary with Claude API...")
            print(f"Processing {len(weekly_events)} weekly events", end="")
            if monthly_events:
                print(f" and {len(monthly_events)} monthly events")
            else:
                print()

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 Sonnet
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Extract the summary from the response
            summary = message.content[0].text

            if Config.VERBOSE:
                print(f"✓ Summary generated successfully ({len(summary)} characters)")

            return summary

        except Exception as e:
            error_msg = f"Error generating summary with Claude API: {e}"
            print(error_msg)
            return f"Failed to generate summary: {str(e)}"
