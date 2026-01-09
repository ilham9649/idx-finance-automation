import requests
import json
import time


class ZChatClassifier:
    API_URL = "https://api.z.ai/api/paas/v4/chat/completions"

    def __init__(self, api_key):
        self.api_key = api_key
        self.last_request_time = 0
        self.min_delay = 5  # Minimum delay between requests in seconds (z.chat has strict rate limits)

    def classify(self, title, report_type, topics):
        # Add rate limiting delay
        self._wait_for_rate_limit()

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

        # Retry with exponential backoff for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "glm-4-plus",
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

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        # Exponential backoff: 2^attempt seconds
                        wait_time = 2 ** attempt
                        print(f"   ⏳ Rate limited, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Final attempt failed, return default
                        print(f"   ⚠️  Rate limit exceeded after retries")
                        return {
                            "impact": "medium",
                            "sentiment": "neutral",
                            "reasoning": "API rate limit exceeded",
                            "keywords": []
                        }
                else:
                    # Other HTTP errors, return default
                    print(f"   ⚠️  HTTP error: {e.response.status_code}")
                    return {
                        "impact": "medium",
                        "sentiment": "neutral",
                        "reasoning": f"API error: {e.response.status_code}",
                        "keywords": []
                    }

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"   ⏳ Timeout, retrying...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    print(f"   ⚠️  Request timed out")
                    return {
                        "impact": "medium",
                        "sentiment": "neutral",
                        "reasoning": "Request timeout",
                        "keywords": []
                    }

            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                return {
                    "impact": "medium",
                    "sentiment": "neutral",
                    "reasoning": f"Error: {str(e)}",
                    "keywords": []
                }

    def _wait_for_rate_limit(self):
        """Wait to ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_delay:
            wait_time = self.min_delay - time_since_last_request
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def classify_batch(self, reports, batch_size=5):
        """
        Classify multiple reports in batches to reduce API calls.

        Args:
            reports: List of report dictionaries with 'title', 'report_type', 'stock'
            batch_size: Number of reports to classify per API call

        Returns:
            List of classification results
        """
        results = []

        # Process in batches
        for i in range(0, len(reports), batch_size):
            batch = reports[i:i + batch_size]

            # Create batch prompt
            batch_prompt = "Classify these Indonesian stock reports by impact and sentiment:\n\n"

            for idx, report in enumerate(batch, 1):
                batch_prompt += f"""Report {idx}:
Title: {report['title']}
Report Type: {report['report_type']}
Stock: {report.get('stock', 'N/A')}

"""

            batch_prompt += """For each report, respond in this JSON format:
{
    "report_1": {"impact": "critical|high|medium|low", "sentiment": "positive|negative|neutral", "reasoning": "brief"},
    "report_2": {"impact": "critical|high|medium|low", "sentiment": "positive|negative|neutral", "reasoning": "brief"},
    ...
}

Impact Criteria (based on expected stock price impact):
- Critical (>10-15%): bankruptcy, M&A, massive earnings surprise, regulatory shutdown
- High (5-10%): earnings beats/misses, major guidance changes, large contracts
- Medium (2-5%): routine earnings, normal business updates, moderate guidance
- Low (<2%): administrative filings, minor corporate actions

Sentiment Criteria:
- Positive: Revenue growth, expansion, positive guidance, dividend
- Negative: Losses, guidance cuts, investigations, debt issues
- Neutral: Factual announcements without clear sentiment
"""

            # Wait for rate limit
            self._wait_for_rate_limit()

            # Try batch classification
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.API_URL,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "glm-4-plus",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a stock market analyst assistant. Classify each report and respond with JSON only."
                                },
                                {
                                    "role": "user",
                                    "content": batch_prompt
                                }
                            ],
                            "temperature": 0.3,
                            "stream": False
                        },
                        timeout=60  # Longer timeout for batch
                    )

                    response.raise_for_status()
                    result = response.json()
                    content = result['choices'][0]['message']['content']

                    # Parse batch response
                    try:
                        classifications = json.loads(content)
                        # Add to results
                        for idx, report in enumerate(batch):
                            report_key = f"report_{idx + 1}"
                            if report_key in classifications:
                                results.append({
                                    **report,
                                    **classifications[report_key]
                                })
                            else:
                                # Fallback to default
                                results.append({
                                    **report,
                                    "impact": "medium",
                                    "sentiment": "neutral",
                                    "reasoning": "Not found in batch response",
                                    "keywords": []
                                })
                        break  # Success, exit retry loop

                    except json.JSONDecodeError:
                        if attempt < max_retries - 1:
                            print(f"   ⏳ Batch {i//batch_size + 1}: Failed to parse, retrying...")
                            time.sleep(2 ** attempt)
                            continue
                        else:
                            # All retries failed, classify individually
                            print(f"   ⚠️  Batch {i//batch_size + 1}: Failed, classifying individually...")
                            for report in batch:
                                classification = self.classify(
                                    report['title'],
                                    report['report_type'],
                                    report.get('stock', '').split(', ')
                                )
                                results.append({**report, **classification})
                            break

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        if attempt < max_retries - 1:
                            wait_time = 5 + (2 ** attempt)  # Longer wait for rate limit
                            print(f"   ⏳ Batch {i//batch_size + 1}: Rate limited, waiting {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # Rate limit exceeded, classify individually
                            print(f"   ⚠️  Batch {i//batch_size + 1}: Rate limit exceeded, classifying individually...")
                            for report in batch:
                                classification = self.classify(
                                    report['title'],
                                    report['report_type'],
                                    report.get('stock', '').split(', ')
                                )
                                results.append({**report, **classification})
                            break
                    else:
                        # Other error, classify individually
                        print(f"   ⚠️  Batch {i//batch_size + 1}: Error {e.response.status_code}, classifying individually...")
                        for report in batch:
                            classification = self.classify(
                                report['title'],
                                report['report_type'],
                                report.get('stock', '').split(', ')
                            )
                            results.append({**report, **classification})
                        break

                except Exception as e:
                    print(f"   ⚠️  Batch {i//batch_size + 1}: Error, classifying individually: {e}")
                    for report in batch:
                        classification = self.classify(
                            report['title'],
                            report['report_type'],
                            report.get('stock', '').split(', ')
                        )
                        results.append({**report, **classification})
                    break

        return results
