import requests
from datetime import datetime, timedelta
from typing import List, Dict


class StockbitClient:
    API_URL = "https://exodus.stockbit.com/stream/v3"

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def fetch_reports(self, limit=50):
        """Fetch latest reports"""
        params = {
            'category': 'STREAM_CATEGORY_REPORTS',
            'last_stream_id': 0,
            'limit': limit,
            'report_type': 'REPORT_TYPE_ALL'
        }

        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }

        response = requests.get(
            self.API_URL,
            headers=headers,
            params=params,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        return data.get('data', {}).get('stream', [])

    def filter_last_hour(self, reports: List[Dict]) -> List[Dict]:
        """Filter reports from last 1 hour"""
        cutoff = datetime.now() - timedelta(hours=1)

        filtered = []
        for report in reports:
            created_at = datetime.strptime(
                report['created_at'],
                '%Y-%m-%d %H:%M:%S'
            )
            if created_at >= cutoff:
                filtered.append({
                    'stream_id': report['stream_id'],
                    'title': report['title'],
                    'timestamp': report['created_at'],
                    'stock': ', '.join(report.get('topics', [])),
                    'report_type': report.get('reports', [{}])[0].get('type', 'Unknown'),
                    'url': f"https://stockbit.com/{report.get('title_url', '')}"
                })

        return filtered
