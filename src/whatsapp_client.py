"""
Twilio WhatsApp client for sending calendar summaries.

This module handles sending messages via WhatsApp using Twilio's API.
Supports both sandbox (for testing) and production WhatsApp numbers.
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import Config


class WhatsAppClient:
    """
    Client for sending WhatsApp messages via Twilio.

    Handles message sending and error handling for WhatsApp delivery.
    """

    def __init__(self):
        """Initialize the Twilio client."""
        self.client = Client(
            Config.TWILIO_ACCOUNT_SID,
            Config.TWILIO_AUTH_TOKEN
        )
        self.from_number = Config.TWILIO_WHATSAPP_FROM
        self.to_number = Config.TWILIO_WHATSAPP_TO

        if Config.VERBOSE:
            print(f"✓ Twilio WhatsApp client initialized")
            print(f"  From: {self.from_number}")
            print(f"  To: {self.to_number}")

    def send_message(self, message: str) -> bool:
        """
        Send a WhatsApp message using Twilio.

        Args:
            message: The message text to send

        Returns:
            True if message sent successfully, False otherwise

        Note:
            If using Twilio sandbox, ensure your recipient number has joined
            the sandbox by sending the join code to the sandbox number.
            Sandbox sessions expire after 72 hours of inactivity.
        """
        if Config.DRY_RUN:
            print("\n" + "="*50)
            print("DRY RUN MODE - Message not sent")
            print("="*50)
            print(f"\nFrom: {self.from_number}")
            print(f"To: {self.to_number}")
            print(f"\nMessage content:\n")
            print(message)
            print("\n" + "="*50)
            return True

        try:
            if Config.VERBOSE:
                print(f"Sending WhatsApp message ({len(message)} characters)...")

            # Send the message via Twilio
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )

            if Config.VERBOSE:
                print(f"✓ Message sent successfully!")
                print(f"  Message SID: {twilio_message.sid}")
                print(f"  Status: {twilio_message.status}")

            return True

        except TwilioRestException as e:
            print(f"Error sending WhatsApp message: {e}")

            # Provide helpful error messages for common issues
            if "not a valid WhatsApp recipient" in str(e):
                print("\nTip: Make sure your recipient number has joined the Twilio sandbox.")
                print("Send the join code to the sandbox WhatsApp number.")
            elif "Authentication Error" in str(e):
                print("\nTip: Check your TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
            elif "unverified" in str(e).lower():
                print("\nTip: You may need to verify the recipient number in Twilio console.")

            return False

        except Exception as e:
            print(f"Unexpected error sending message: {e}")
            return False

    def send_summary(self, summary: str, subject: str = "📅 Weekly Calendar Summary") -> bool:
        """
        Send a formatted calendar summary via WhatsApp.

        Args:
            summary: The calendar summary text
            subject: Optional subject line (default: "📅 Weekly Calendar Summary")

        Returns:
            True if sent successfully, False otherwise
        """
        # Format the message with a nice header
        formatted_message = f"{subject}\n\n{summary}"

        # WhatsApp messages via Twilio have a 1600 character limit
        # Truncate if necessary
        if len(formatted_message) > 1600:
            if Config.VERBOSE:
                print(f"Warning: Message exceeds 1600 chars ({len(formatted_message)}), truncating...")

            truncated = formatted_message[:1550]
            formatted_message = truncated + "\n\n... (message truncated)"

        return self.send_message(formatted_message)
