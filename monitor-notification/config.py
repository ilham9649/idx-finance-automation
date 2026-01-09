import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Stockbit
    STOCKBIT_TOKEN = os.getenv('STOCKBIT_TOKEN')

    # z.chat
    ZCHAT_API_KEY = os.getenv('ZCHAT_API_KEY')

    # Google Sheets
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

    # Load Google credentials from base64 encoded JSON string
    @staticmethod
    def _load_google_credentials():
        creds_str = os.getenv('GOOGLE_CREDENTIALS')
        if creds_str:
            try:
                # Try base64 decoding first
                decoded = base64.b64decode(creds_str).decode('utf-8')
                return json.loads(decoded)
            except Exception:
                # If base64 fails, try direct JSON parsing
                try:
                    return json.loads(creds_str)
                except Exception:
                    # If both fail, return None
                    return None
        return None

    GOOGLE_CREDENTIALS = _load_google_credentials.__func__()

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Application
    DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
