# Stockbit Hourly Report Automation

Automated system to fetch Stockbit reports, classify them by impact and sentiment using z.chat AI, store results in Google Sheets, and send Telegram notifications for critical/high impact reports.

## Features

- 📡 Fetches reports from Stockbit API (last 1 hour)
- 🤖 Classifies by impact (critical/high/medium/low) and sentiment (positive/negative/neutral) using z.chat GLM-4.7
- 💾 Stores all classified reports in Google Sheets
- 📱 Sends Telegram notifications for critical and high impact reports
- ⏰ Designed to run hourly via cron/scheduler

## Setup

### 1. Install Dependencies

```bash
cd monitor-notification
pip install -r requirements.txt
```

### 2. Create Google Sheet

1. Go to https://sheets.google.com
2. Create a new spreadsheet
3. Copy the spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
4. Share the sheet with: `idx-automation@gmail-mcp-server-481623.iam.gserviceaccount.com`
5. Give Editor permission

### 3. Configure Environment Variables

Copy the example file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:

```bash
# Stockbit API (get from your Stockbit account)
STOCKBIT_TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6IjU3MDc0NjI3LTg4MWItNDQzZC04OTcyLTdmMmMzOTNlMzYyOSIsInR5cCI6IkpXVCJ9...

# Google Sheets (your spreadsheet ID)
SPREADSHEET_ID=1AbCdEf123456789...

# Telegram (from @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
```

### 4. Run the Script

```bash
python main.py
```

## Scheduling

### Linux/macOS (Cron)

```bash
# Edit crontab
crontab -e

# Add entry to run every hour
0 * * * * cd /path/to/monitor-notification && /usr/bin/python3 main.py >> automation.log 2>&1
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 1 hour
4. Action: Start program
   - Program: `python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\monitor-notification`

## File Structure

```
monitor-notification/
├── main.py                      # Main workflow script
├── config.py                    # Configuration with credentials
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example environment variables
├── .gitignore                   # Ignore sensitive files
├── state.json                   # Local state storage (auto-created)
├── README.md                    # This file
└── utils/
    ├── __init__.py
    ├── stockbit_client.py      # Stockbit API integration
    ├── zchat_classifier.py     # z.chat API integration
    ├── sheets_client.py        # Google Sheets API
    └── telegram_notifier.py    # Telegram bot
```

## Classification Criteria

### Impact Levels (Based on Expected Stock Price Movement)

- **Critical**: MAJOR price movement expected (>10-15%)
  - Bankruptcy, M&A, massive earnings surprise
  - Regulatory shutdown, delisting, major fraud investigation

- **High**: SIGNIFICANT price movement expected (5-10%)
  - Earnings beats/misses, major guidance changes
  - Large contract wins/losses, dividend cuts/suspension, executive scandals

- **Medium**: MODERATE price movement expected (2-5%)
  - Routine earnings, normal business updates
  - Moderate guidance, minor contracts, regular dividends

- **Low**: MINIMAL price movement expected (<2%)
  - Administrative filings, minor corporate actions
  - Routine disclosures, ownership reports

### Sentiment Levels

- **Positive**: Revenue growth, expansion, positive guidance, dividend, stock split
- **Negative**: Losses, guidance cuts, investigations, debt issues, delisting risk
- **Neutral**: Factual announcements without clear sentiment

## Troubleshooting

### Stockbit API Errors

- Verify your bearer token is valid
- Check that the token hasn't expired
- Ensure you have access to the reports endpoint

### Google Sheets Errors

- Verify spreadsheet ID is correct
- Ensure service account email has Editor access
- Check that Sheets API is enabled

### Telegram Errors

- Verify bot token is correct
- Check chat ID is correct (can get from @userinfobot)
- Ensure bot is added to the group (if using group chat)

### LLM Classification Errors

- Check z.chat API key is valid
- Verify API endpoint is accessible
- Check rate limits (if any)

## Output

### Google Sheets

Each report creates a row with:
- Timestamp
- Stream ID
- Title
- Stock symbol(s)
- Report Type
- Impact level
- Sentiment
- Reasoning
- Keywords
- Source

### Telegram Notifications

**Critical Impact** - Individual messages for each report:
```
🚨 *CRITICAL IMPACT*

*Title*: [Report title]
*Stock*: [Symbol]
*Report Type*: [Type]

*Sentiment*: [Positive/Negative/Neutral]
*Reasoning*: [Explanation]

📅 [Timestamp]
🔗 [Link]
```

**High Impact** - Summary of all high-impact reports:
```
📊 *High Impact Reports Summary* (N reports)

1. [Symbol] - [Title]
   Sentiment: [Sentiment]

...
```

## License

MIT
