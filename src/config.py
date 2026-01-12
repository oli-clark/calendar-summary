"""
Configuration module for managing environment variables and application settings.

This module loads environment variables from a .env file (for local development)
or from system environment variables (for production/GitHub Actions).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This is useful for local development
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """
    Central configuration class that provides access to all environment variables.

    All credentials and settings are loaded from environment variables to keep
    sensitive information out of the codebase.
    """

    # Google Calendar Configuration
    GOOGLE_CALENDAR_CREDENTIALS_PATH = os.getenv(
        'GOOGLE_CALENDAR_CREDENTIALS_PATH',
        './credentials.json'
    )
    GOOGLE_CALENDAR_TOKEN_PATH = os.getenv(
        'GOOGLE_CALENDAR_TOKEN_PATH',
        './token.json'
    )
    CALENDAR_ID = os.getenv('CALENDAR_ID', 'primary')

    # Claude API Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_FROM = os.getenv(
        'TWILIO_WHATSAPP_FROM',
        'whatsapp:+14155238886'  # Default Twilio sandbox number
    )
    TWILIO_WHATSAPP_TO = os.getenv('TWILIO_WHATSAPP_TO')

    # Optional Configuration
    DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
    VERBOSE = os.getenv('VERBOSE', 'false').lower() == 'true'

    # Prompt template path
    PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / 'prompts' / 'summary_prompt.txt'

    @classmethod
    def validate(cls):
        """
        Validates that all required environment variables are set.

        Raises:
            ValueError: If any required configuration is missing
        """
        missing = []

        if not cls.ANTHROPIC_API_KEY:
            missing.append('ANTHROPIC_API_KEY')

        if not cls.TWILIO_ACCOUNT_SID:
            missing.append('TWILIO_ACCOUNT_SID')

        if not cls.TWILIO_AUTH_TOKEN:
            missing.append('TWILIO_AUTH_TOKEN')

        if not cls.TWILIO_WHATSAPP_TO:
            missing.append('TWILIO_WHATSAPP_TO')

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file or environment configuration."
            )

        # Check if Google Calendar credentials file exists
        if not os.path.exists(cls.GOOGLE_CALENDAR_CREDENTIALS_PATH):
            raise ValueError(
                f"Google Calendar credentials file not found at: "
                f"{cls.GOOGLE_CALENDAR_CREDENTIALS_PATH}\n"
                f"Please download credentials.json from Google Cloud Console."
            )

        if cls.VERBOSE:
            print("✓ Configuration validated successfully")
