# Quick Start Guide

## Immediate Next Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or create a virtual environment first (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 3. Get API Credentials

You need three sets of credentials:

#### A. Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Calendar API
3. Create OAuth 2.0 Desktop credentials
4. Download as `credentials.json` in project root

#### B. Claude API
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Get an API key
3. Add to `.env` as `ANTHROPIC_API_KEY`

#### C. Twilio WhatsApp
1. Sign up at [twilio.com](https://www.twilio.com/try-twilio)
2. Get Account SID and Auth Token
3. Join WhatsApp sandbox (send join code to sandbox number)
4. Add credentials to `.env`

See [README.md](README.md) for detailed setup instructions.

### 4. Test It

```bash
cd src
python main.py --dry-run --verbose
```

This will:
- Authenticate with Google Calendar (opens browser first time)
- Fetch your calendar events
- Generate a summary with Claude
- Display the result WITHOUT sending to WhatsApp

### 5. Send for Real

Once you're happy with the dry run:

```bash
python main.py --verbose
```

## Project Status: ✅ COMPLETE

All components are implemented:
- ✅ Google Calendar integration
- ✅ Claude AI summarization
- ✅ WhatsApp delivery via Twilio
- ✅ Configurable via environment variables
- ✅ Dry-run testing mode
- ✅ GitHub Actions workflow
- ✅ Comprehensive documentation

## File Structure

```
calendar-summary/
├── README.md              ← Full documentation
├── QUICKSTART.md          ← This file
├── requirements.txt       ← Install these
├── .env.example          ← Copy to .env
├── .gitignore            ← Protects credentials
├── src/
│   ├── main.py           ← Run this
│   ├── config.py
│   ├── calendar_client.py
│   ├── summariser.py
│   └── whatsapp_client.py
├── prompts/
│   └── summary_prompt.txt ← Customize Claude's tone
└── .github/workflows/
    └── weekly-summary.yml ← Auto-schedule on GitHub
```

## Troubleshooting

**Import errors?**
→ Run `pip install -r requirements.txt`

**"Credentials file not found"?**
→ Download `credentials.json` from Google Cloud Console

**"Missing required environment variables"?**
→ Copy `.env.example` to `.env` and fill in your API keys

**Need help?**
→ See the comprehensive [README.md](README.md) with step-by-step setup guides

## Deployment Options

- **GitHub Actions** (recommended): Free scheduled runs, see README
- **Local cron**: Set up a cron job on your machine
- **Cloud platforms**: Railway, Render, Heroku, AWS Lambda

## Customization

Edit `prompts/summary_prompt.txt` to change:
- Tone (formal/casual)
- Level of detail
- Focus areas
- Summary structure

No code changes needed!
