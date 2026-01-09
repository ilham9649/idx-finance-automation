import urllib.request
import urllib.error
import json
from datetime import datetime, timedelta
from typing import List, Dict


class StockbitClient:
    API_URL = "https://exodus.stockbit.com/stream/v3"

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def fetch_reports(self, limit=20):
        """Fetch latest reports using urllib (standard library)"""
        params = f"?category=STREAM_CATEGORY_REPORTS&last_stream_id=0&limit={limit}&report_type=REPORT_TYPE_ALL"
        full_url = self.API_URL + params

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Origin': 'https://stockbit.com',
            'Referer': 'https://stockbit.com/'
        }

        req = urllib.request.Request(full_url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                print(f"   Status Code: {response.status}")

                return data.get('data', {}).get('stream', [])

        except urllib.error.HTTPError as e:
            print(f"   HTTP Error: {e.code}")
            try:
                error_body = e.read().decode('utf-8')
                print(f"   Response body: {error_body[:500]}")
            except:
                pass
            raise Exception(f"HTTP {e.code}: {error_body if 'error_body' in locals() else 'Unknown error'}")
        except urllib.error.URLError as e:
            if isinstance(e.reason, timeout):
                raise Exception("Request timed out. Please check your internet connection.")
            raise Exception(f"URL Error: {e.reason}")

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
