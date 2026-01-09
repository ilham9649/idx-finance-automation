from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class SheetsClient:
    def __init__(self, credentials_dict, spreadsheet_id):
        # Parse credentials
        self.credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = spreadsheet_id

    def append_reports(self, reports):
        """Append reports to sheet"""
        values = [
            [
                r['timestamp'],
                r['stream_id'],
                r['title'],
                r.get('stock', ''),
                r.get('report_type', ''),
                r['impact'],
                r['sentiment'],
                r['reasoning'],
                ', '.join(r.get('keywords', [])),
                'Stockbit'
            ]
            for r in reports
        ]

        # Check if headers exist
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range='Sheet1!A1:J1'
        ).execute()

        if not result.get('values'):
            # Add headers
            headers = [
                'Timestamp', 'Stream ID', 'Title', 'Stock',
                'Report Type', 'Impact', 'Sentiment', 'Reasoning',
                'Keywords', 'Source'
            ]
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()

        # Append data
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='Sheet1!A2',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()

        print(f"✓ Saved {len(reports)} reports to Google Sheets")
