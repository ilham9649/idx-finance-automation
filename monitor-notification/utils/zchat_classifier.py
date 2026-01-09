import requests
import json


class ZChatClassifier:
    API_URL = "https://api.z.ai/api/paas/v4/chat/completions"

    def __init__(self, api_key):
        self.api_key = api_key

    def classify(self, title, report_type, topics):
        prompt = f"""Classify this Indonesian stock report by impact and sentiment:

Title: {title}
Report Type: {report_type}
Stock: {topics[0] if topics else 'N/A'}

Respond in JSON format:
{{
    "impact": "critical|high|medium|low",
    "sentiment": "positive|negative|neutral",
    "reasoning": "brief explanation",
    "keywords": ["keyword1", "keyword2"]
}}

Impact Criteria (based on expected stock price impact):
- Critical: MAJOR price movement expected (>10-15%) - bankruptcy, M&A, massive earnings surprise, regulatory shutdown, delisting, major fraud investigation
- High: SIGNIFICANT price movement expected (5-10%) - earnings beats/misses, major guidance changes, large contract wins/losses, dividend cuts/suspension, executive scandals
- Medium: MODERATE price movement expected (2-5%) - routine earnings, normal business updates, moderate guidance, minor contracts, regular dividends
- Low: MINIMAL price movement expected (<2%) - administrative filings, minor corporate actions, routine disclosures, ownership reports

Sentiment Criteria:
- Positive: Revenue growth, expansion, positive guidance, dividend, stock split
- Negative: Losses, guidance cuts, investigations, debt issues, delisting risk
- Neutral: Factual announcements without clear sentiment
"""

        response = requests.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "glm-4.7",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a stock market analyst assistant that classifies Indonesian stock reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "stream": False
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        # Extract JSON from response
        content = result['choices'][0]['message']['content']

        # Try to parse JSON, handling potential markdown code blocks
        try:
            # First try direct parsing
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                return json.loads(content[json_start:json_end].strip())
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                return json.loads(content[json_start:json_end].strip())
            else:
                # If all else fails, return default classification
                return {
                    "impact": "medium",
                    "sentiment": "neutral",
                    "reasoning": "Could not parse LLM response",
                    "keywords": []
                }
