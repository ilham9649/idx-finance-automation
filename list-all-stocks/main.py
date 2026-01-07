"""Fetch listed companies from IDX and print basic data.

This script replaces the previous Selenium-based approach with a simple
HTTP request to the public endpoint and prints each company's JSON on a
separate line. It's lightweight and doesn't require a browser binary.
"""

import json
import sys
from typing import List, Dict
from urllib.request import urlopen, Request

LINK = "https://idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType=s&start=0&length=9999"


def fetch_companies() -> List[Dict]:
	try:
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
			"Accept": "application/json, text/javascript, */*; q=0.01",
			"Accept-Language": "en-US,en;q=0.9",
			"X-Requested-With": "XMLHttpRequest",
			"Referer": "https://idx.co.id/",
			"Origin": "https://idx.co.id",
		}
		req = Request(LINK, headers=headers)
		with urlopen(req, timeout=15) as resp:
			raw = resp.read()
			text = raw.decode("utf-8", errors="replace")
	except Exception as e:
		print(f"Failed to fetch data: {e}", file=sys.stderr)
		return []

	try:
		data = json.loads(text)
	except Exception as e:
		print(f"Failed to parse JSON: {e}", file=sys.stderr)
		return []

	return data.get("data", []) if isinstance(data, dict) else []


def main():
	companies = fetch_companies()
	print(f"Found {len(companies)} companies")
	for c in companies:
		# show code with .JK suffix and the full JSON for flexibility
		code = c.get("KodeEmiten")
		if code:
			print(code + ".JK", json.dumps(c, ensure_ascii=False))
		else:
			print(json.dumps(c, ensure_ascii=False))


if __name__ == "__main__":
	main()
