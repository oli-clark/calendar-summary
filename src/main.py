#!/usr/bin/env python3
"""
Weekly Calendar Summary WhatsApp Bot - Main Entry Point

This script orchestrates the weekly calendar summary process:
1. Fetches events from Google Calendar
2. Generates an intelligent summary using Claude API
3. Sends the summary via WhatsApp using Twilio

Can be run manually or scheduled via GitHub Actions.
"""

import argparse
import sys
from datetime import datetime

from config import Config
from calendar_client import CalendarClient
from summariser import CalendarSummariser
from whatsapp_client import WhatsAppClient


def print_banner():
    """Print a friendly banner when starting the script."""
    print("\n" + "="*60)
    print("   📅 Weekly Calendar Summary WhatsApp Bot")
    print("="*60 + "\n")


def main():
    """
    Main orchestration function.

    This function coordinates all the pieces:
    - Validates configuration
    - Fetches calendar events
    - Generates summary with Claude
    - Sends via WhatsApp
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate and send weekly calendar summary via WhatsApp'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate summary but do not send WhatsApp message'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--weekly-only',
        action='store_true',
        help='Only include weekly events, skip monthly look-ahead'
    )
    args = parser.parse_args()

    # Override config with command line arguments
    if args.dry_run:
        Config.DRY_RUN = True
    if args.verbose:
        Config.VERBOSE = True

    print_banner()

    # Step 1: Validate configuration
    if Config.VERBOSE:
        print("Step 1: Validating configuration...")
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error:\n{e}\n")
        sys.exit(1)

    if Config.DRY_RUN:
        print("🔍 Running in DRY RUN mode (no WhatsApp message will be sent)\n")

    # Step 2: Initialize clients
    if Config.VERBOSE:
        print("\nStep 2: Initializing API clients...")

    try:
        calendar_client = CalendarClient()
        summariser = CalendarSummariser()
        whatsapp_client = WhatsAppClient()
    except Exception as e:
        print(f"\n❌ Error initializing clients: {e}\n")
        sys.exit(1)

    # Step 3: Fetch calendar events
    if Config.VERBOSE:
        print("\nStep 3: Fetching calendar events...")

    try:
        # Get weekly events (next 7 days)
        weekly_events = calendar_client.get_weekly_events()

        # Get monthly events (next 30 days) unless weekly-only flag is set
        monthly_events = None
        if not args.weekly_only:
            monthly_events = calendar_client.get_monthly_events()

        print(f"✓ Fetched {len(weekly_events)} events for the week ahead")
        if monthly_events is not None:
            print(f"✓ Fetched {len(monthly_events)} events for the month ahead")

    except Exception as e:
        print(f"\n❌ Error fetching calendar events: {e}\n")
        sys.exit(1)

    # Check if there are any events
    if not weekly_events and not monthly_events:
        print("\nℹ️  No events found in calendar. Nothing to summarize.")
        sys.exit(0)

    # Step 4: Generate summary with Claude
    if Config.VERBOSE:
        print("\nStep 4: Generating intelligent summary with Claude...")

    try:
        summary = summariser.generate_summary(weekly_events, monthly_events)
        print("✓ Summary generated successfully")

        if Config.VERBOSE:
            print("\n" + "-"*60)
            print("Generated Summary:")
            print("-"*60)
            print(summary)
            print("-"*60)

    except Exception as e:
        print(f"\n❌ Error generating summary: {e}\n")
        sys.exit(1)

    # Step 5: Send via WhatsApp
    if Config.VERBOSE:
        print("\nStep 5: Sending summary via WhatsApp...")

    try:
        success = whatsapp_client.send_summary(summary)

        if success:
            if Config.DRY_RUN:
                print("\n✓ Dry run completed successfully!")
            else:
                print("\n✓ Calendar summary sent successfully to WhatsApp!")
        else:
            print("\n❌ Failed to send WhatsApp message")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error sending WhatsApp message: {e}\n")
        sys.exit(1)

    # Success!
    if Config.VERBOSE:
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n" + "="*60)
    print("   ✅ All done!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
