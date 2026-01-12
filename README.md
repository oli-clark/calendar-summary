# 📅 Weekly Calendar Summary WhatsApp Bot

An intelligent Python script that runs weekly to generate a smart summary of your upcoming calendar events and sends it to you via WhatsApp. Uses Google Calendar API, Claude AI for intelligent summarization, and Twilio for WhatsApp delivery.

## 🎯 Features

- **Google Calendar Integration**: Automatically fetches events from your Google Calendar
- **Intelligent Summarization**: Uses Claude AI to create conversational, insightful summaries
- **WhatsApp Delivery**: Sends summaries via Twilio WhatsApp
- **Smart Filtering**: Automatically filters out declined meetings
- **Dual Time Horizons**:
  - Detailed weekly view (next 7 days)
  - Monthly look-ahead for important items (next 30 days)
- **Flexible Scheduling**: Runs on GitHub Actions (free) or any cron-compatible system
- **Testing Modes**: Dry-run and verbose modes for development
- **Easily Customizable**: Edit the Claude prompt without touching code

## 🏗️ Architecture

```
┌─────────────────┐
│ Google Calendar │
└────────┬────────┘
         │ Events
         ▼
┌─────────────────┐
│  calendar_client│ Fetches events
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   summariser    │ Claude API
└────────┬────────┘ Generates summary
         │
         ▼
┌─────────────────┐
│ whatsapp_client │ Twilio API
└─────────────────┘ Sends WhatsApp
```

### Project Structure

```
calendar-summary/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Prevents credential commits
├── src/
│   ├── main.py                  # Main orchestrator
│   ├── config.py                # Configuration management
│   ├── calendar_client.py       # Google Calendar integration
│   ├── summariser.py            # Claude API integration
│   └── whatsapp_client.py       # Twilio WhatsApp client
├── prompts/
│   └── summary_prompt.txt       # Editable Claude prompt
└── .github/
    └── workflows/
        └── weekly-summary.yml   # GitHub Actions schedule
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google account with Calendar access
- Claude API key (from console.anthropic.com)
- Twilio account (free tier works)

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd calendar-summary
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials (see Setup sections below)
```

### 3. Run Locally (Test Mode)

```bash
cd src
python main.py --dry-run --verbose
```

## 📋 Detailed Setup Guide

### 1. Google Calendar API Setup

#### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Name it something like "Calendar Summary Bot"

#### Step 2: Enable Google Calendar API

1. In your project, navigate to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

#### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (unless you have Google Workspace)
   - App name: "Calendar Summary Bot"
   - User support email: Your email
   - Add your email as a test user
4. Choose **Application type**: **Desktop app**
5. Name it "Calendar Bot Desktop"
6. Click **Create**

#### Step 4: Download Credentials

1. Click the download icon (⬇️) next to your newly created OAuth 2.0 Client ID
2. Save the file as `credentials.json` in your project root
3. **Important**: This file is in `.gitignore` - never commit it!

#### Step 5: First Authentication

1. Run the script locally: `python src/main.py --dry-run`
2. A browser window will open asking you to authorize the app
3. Sign in with your Google account
4. Grant calendar read permissions
5. The script will save `token.json` for future use

**Note**: You'll need to repeat OAuth setup if adding a second calendar later.

### 2. Claude API Setup

#### Step 1: Get API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-`)

#### Step 2: Add to Environment

```bash
# In your .env file
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Cost Estimate**: With Claude 3.5 Sonnet, weekly summaries cost approximately $0.01-0.02 per run (a few pennies per month).

**Note**: This is separate from your Claude.ai subscription. You need to add credits to your API account.

### 3. Twilio WhatsApp Sandbox Setup

#### Step 1: Create Twilio Account

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free account
3. Verify your email and phone number

#### Step 2: Access WhatsApp Sandbox

1. In Twilio Console, navigate to **Messaging** > **Try it out** > **Send a WhatsApp message**
2. You'll see a sandbox number (e.g., `+1 415 523 8886`)
3. You'll also see a join code (e.g., "join abc-def")

#### Step 3: Join the Sandbox

1. Open WhatsApp on your phone
2. Send the join code (e.g., "join abc-def") to the sandbox number
3. You should receive a confirmation message

**Important**: Sandbox sessions expire after 72 hours of inactivity. You'll need to rejoin by sending the code again.

#### Step 4: Get Credentials

1. In Twilio Console, go to **Account** > **Keys & Credentials**
2. Copy your **Account SID** (starts with `AC`)
3. Copy your **Auth Token** (click to reveal)

#### Step 5: Add to Environment

```bash
# In your .env file
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Sandbox number
TWILIO_WHATSAPP_TO=whatsapp:+44XXXXXXXXXX   # Your phone number
```

**Note**: For production use beyond the sandbox, you'll need to request WhatsApp Business API access through Twilio.

### 4. Complete .env Configuration

Your final `.env` should look like:

```bash
# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=./token.json
CALENDAR_ID=primary

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+44XXXXXXXXXX

# Optional
DRY_RUN=false
VERBOSE=false
```

## 🎮 Usage

### Running Locally

```bash
cd src

# Dry run (doesn't send WhatsApp)
python main.py --dry-run --verbose

# Send for real
python main.py --verbose

# Weekly events only (skip monthly look-ahead)
python main.py --weekly-only
```

### Command Line Options

- `--dry-run`: Generate summary but don't send WhatsApp message
- `--verbose`: Print detailed logs of what's happening
- `--weekly-only`: Skip the monthly look-ahead, only summarize the week

## 🤖 Deployment

### Option 1: GitHub Actions (Recommended)

#### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

#### Step 2: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** and add each:

```
GOOGLE_CREDENTIALS_BASE64
GOOGLE_TOKEN_BASE64 (after first local run)
CALENDAR_ID
ANTHROPIC_API_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_FROM
TWILIO_WHATSAPP_TO
```

#### Step 3: Encode Credentials

```bash
# Encode credentials.json
cat credentials.json | base64 > credentials.txt
# Copy the contents of credentials.txt and add as GOOGLE_CREDENTIALS_BASE64

# After first successful local run, encode token.json
cat token.json | base64 > token.txt
# Copy the contents and add as GOOGLE_TOKEN_BASE64
```

#### Step 4: Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will run every Sunday at 6 PM UTC (adjust in `.github/workflows/weekly-summary.yml`)

#### Step 5: Manual Test

1. Go to **Actions** tab
2. Select "Weekly Calendar Summary" workflow
3. Click **Run workflow** to test immediately

### Option 2: Local Cron Job

```bash
# Edit your crontab
crontab -e

# Add this line (runs every Sunday at 6 PM)
0 18 * * 0 cd /path/to/calendar-summary/src && /usr/bin/python3 main.py

# Or use the full path to your virtual environment Python
0 18 * * 0 cd /path/to/calendar-summary/src && /path/to/venv/bin/python main.py
```

### Option 3: Cloud Platforms

The script can also run on:
- **Railway**: Add as a cron job project
- **Render**: Use cron jobs feature
- **Heroku**: Use Heroku Scheduler add-on
- **AWS Lambda**: Use EventBridge for scheduling

## ✏️ Customizing the Summary

### Edit the Claude Prompt

The easiest way to customize summaries is to edit `prompts/summary_prompt.txt`:

```bash
# Open in your editor
nano prompts/summary_prompt.txt
```

**Things you can customize:**
- Tone (more formal/casual)
- Level of detail (verbose/concise)
- Focus areas (highlight certain types of meetings)
- Summary structure (how events are grouped)

**Example customizations:**

```txt
# More casual tone
You are my personal calendar buddy...

# Focus on preparation
Emphasize what I need to prepare for each important meeting...

# More formal tone
Provide a professional summary of scheduled engagements...
```

### Advanced Customization

For deeper changes, edit these files:

- `src/calendar_client.py`: Change what calendar data is fetched
- `src/summariser.py`: Modify how events are formatted for Claude
- `src/whatsapp_client.py`: Change message formatting
- `src/main.py`: Add new command-line options

## 🔮 Future Extensions

The codebase is designed for easy extension:

### Add a Second Calendar (Personal)

1. Repeat Google OAuth setup for second account
2. Save as `credentials_personal.json` and `token_personal.json`
3. Modify `calendar_client.py` to support multiple calendars
4. Merge events before sending to Claude

### Add Task Sources

1. Create new client (e.g., `linear_client.py`, `trello_client.py`)
2. Fetch tasks in similar format to calendar events
3. Pass to `summariser.py` alongside calendar events

### Multiple Recipients

1. Add more phone numbers to `.env`
2. Modify `whatsapp_client.py` to loop through recipients
3. Optionally customize summary per recipient

### Different Frequencies

1. Duplicate GitHub Actions workflow for daily/monthly
2. Adjust date ranges in `main.py`
3. Create separate prompt templates for each frequency

## 🐛 Troubleshooting

### Google Calendar Issues

**"Credentials file not found"**
- Ensure `credentials.json` is in project root
- Check `GOOGLE_CALENDAR_CREDENTIALS_PATH` in `.env`

**"Token has been expired or revoked"**
- Delete `token.json` and re-run to re-authenticate
- Check if you revoked access in Google account settings

**"No events found"**
- Verify you're using the correct calendar ID (`primary` is usually correct)
- Check date ranges are correct

### Claude API Issues

**"Authentication error"**
- Verify your API key is correct and has credits
- Check at [console.anthropic.com](https://console.anthropic.com/)

**"Rate limit exceeded"**
- You're making too many requests
- Wait a few minutes and try again

### Twilio WhatsApp Issues

**"Not a valid WhatsApp recipient"**
- Ensure you've joined the Twilio sandbox
- Resend the join code if 72 hours have passed

**"Authentication Error"**
- Double-check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
- Verify credentials in Twilio Console

**"Message truncated"**
- WhatsApp messages via Twilio are limited to 1600 characters
- Consider shortening your Claude prompt or using `--weekly-only`

### GitHub Actions Issues

**"Secrets not found"**
- Verify all secrets are added in repository settings
- Check secret names match exactly (case-sensitive)

**"Workflow not running"**
- Check if Actions are enabled in repository settings
- Verify cron schedule syntax in `weekly-summary.yml`

## 📚 Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Twilio WhatsApp API Documentation](https://www.twilio.com/docs/whatsapp)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## ⚠️ Security Notes

- Never commit `credentials.json`, `token.json`, or `.env`
- Use GitHub Secrets for sensitive data in Actions
- Rotate credentials regularly
- Use environment variables for all secrets

## 💡 Tips

1. **Test first**: Always run with `--dry-run` before sending for real
2. **Schedule wisely**: Sunday evening is great, but adjust to your preference
3. **Customize the prompt**: The default is a starting point - make it yours!
4. **Monitor costs**: Check Claude API usage in console.anthropic.com
5. **Sandbox expiry**: Remember to rejoin Twilio sandbox every 72 hours

---

**Made with ❤️ for better calendar management**