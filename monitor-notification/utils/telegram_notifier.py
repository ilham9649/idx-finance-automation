import requests


class TelegramNotifier:
    API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_critical(self, report):
        """Send individual critical report"""
        message = f"""🚨 *CRITICAL IMPACT*

*Title*: {report['title']}
*Stock*: {report.get('stock', 'N/A')}
*Report Type*: {report.get('report_type', 'N/A')}

*Sentiment*: {report['sentiment']}
*Reasoning*: {report['reasoning']}

📅 {report['timestamp']}
🔗 {report.get('url', '')}"""

        self._send_message(message)

    def send_high_summary(self, reports):
        """Send summary of high-impact reports"""
        message = f"📊 *High Impact Reports Summary* ({len(reports)} reports)\n\n"

        for i, r in enumerate(reports[:5], 1):
            message += f"{i}. *{r.get('stock', 'N/A')}* - {r['title'][:60]}...\n"
            message += f"   Sentiment: {r['sentiment']}\n\n"

        if len(reports) > 5:
            message += f"... and {len(reports) - 5} more"

        self._send_message(message)

    def _send_message(self, text):
        url = self.API_URL.format(token=self.bot_token, method='sendMessage')

        requests.post(
            url,
            json={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            },
            timeout=10
        )
