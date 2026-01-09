import os
import json
from datetime import datetime
from dotenv import load_dotenv

from config import Config
from utils.stockbit_client import StockbitClient
from utils.zchat_classifier import ZChatClassifier
from utils.sheets_client import SheetsClient
from utils.telegram_notifier import TelegramNotifier


def load_state():
    """Load last_stream_id from local state file"""
    try:
        with open('state.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'last_stream_id': 0, 'last_run': None}


def save_state(state):
    """Save state to local file"""
    with open('state.json', 'w') as f:
        json.dump(state, f, indent=2)


def main():
    print("=" * 60)
    print("Stockbit Report Automation - Starting")
    print("=" * 60)

    # Load config
    load_dotenv()
    config = Config()

    # Validate configuration
    if not config.STOCKBIT_TOKEN:
        print("ERROR: STOCKBIT_TOKEN not configured in .env file")
        return

    if not config.SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID not configured in .env file")
        return

    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID not configured in .env file")
        return

    # Initialize clients
    stockbit = StockbitClient(config.STOCKBIT_TOKEN)
    classifier = ZChatClassifier(config.ZCHAT_API_KEY)
    sheets = SheetsClient(config.GOOGLE_CREDENTIALS, config.SPREADSHEET_ID)
    telegram = TelegramNotifier(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)

    # Fetch reports
    print("\n📡 Fetching reports from Stockbit...")
    try:
        all_reports = stockbit.fetch_reports(limit=50)
        print(f"   Fetched {len(all_reports)} reports")
    except Exception as e:
        print(f"   ERROR: Failed to fetch reports: {e}")
        return

    # Filter last 1 hour
    print("\n⏰ Filtering reports from last 1 hour...")
    recent_reports = stockbit.filter_last_hour(all_reports)
    print(f"   Found {len(recent_reports)} recent reports")

    if not recent_reports:
        print("\n✓ No new reports in last hour")
        return

    # Classify each report
    print("\n🤖 Classifying reports with z.chat...")
    classified_reports = []

    for i, report in enumerate(recent_reports, 1):
        try:
            classification = classifier.classify(
                title=report['title'],
                report_type=report['report_type'],
                topics=report.get('stock', '').split(', ')
            )

            classified_report = {
                **report,
                **classification
            }
            classified_reports.append(classified_report)

            print(f"   [{i}/{len(recent_reports)}] {report['stock']} - {classification['impact']} / {classification['sentiment']}")

        except Exception as e:
            print(f"   [{i}/{len(recent_reports)}] ERROR: {e}")
            # Add default classification
            classified_reports.append({
                **report,
                'impact': 'medium',
                'sentiment': 'neutral',
                'reasoning': f'Classification failed: {str(e)}',
                'keywords': []
            })

    # Store in Google Sheets
    print("\n💾 Storing reports in Google Sheets...")
    try:
        sheets.append_reports(classified_reports)
    except Exception as e:
        print(f"   ERROR: Failed to save to Sheets: {e}")

    # Send notifications for critical/high
    print("\n📱 Sending notifications...")
    critical = [r for r in classified_reports if r['impact'] == 'critical']
    high = [r for r in classified_reports if r['impact'] == 'high']

    for report in critical:
        try:
            telegram.send_critical(report)
            print(f"   ✓ Sent critical: {report.get('stock', 'N/A')}")
        except Exception as e:
            print(f"   ERROR: Failed to send notification: {e}")

    if high:
        try:
            telegram.send_high_summary(high)
            print(f"   ✓ Sent high summary: {len(high)} reports")
        except Exception as e:
            print(f"   ERROR: Failed to send summary: {e}")

    # Update state
    state = {
        'last_stream_id': max(r['stream_id'] for r in all_reports),
        'last_run': datetime.now().isoformat()
    }
    save_state(state)

    print("\n" + "=" * 60)
    print(f"✓ Completed: {len(classified_reports)} reports processed")
    print(f"  - Critical: {len(critical)}")
    print(f"  - High: {len(high)}")
    print(f"  - Medium: {len([r for r in classified_reports if r['impact'] == 'medium'])}")
    print(f"  - Low: {len([r for r in classified_reports if r['impact'] == 'low'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
