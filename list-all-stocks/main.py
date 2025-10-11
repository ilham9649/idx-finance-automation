import json
import urllib.request
from typing import Any, Dict, List, Optional

LINK = "https://idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType=s&start=0&length=9999"

# Use browser-like headers to avoid being blocked by basic bot protection
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Referer": "https://idx.co.id/",
}

def fetch_company_profiles() -> Dict[str, Any]:
    request = urllib.request.Request(LINK, headers=HEADERS, method="GET")
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8"))

def get_stock_codes(suffix: str = ".JK") -> List[str]:
    payload = fetch_company_profiles()
    companies = payload.get("data", [])
    stock_codes: List[str] = []
    for company in companies:
        code = company.get("KodeEmiten")
        if not code:
            continue
        stock_codes.append(f"{code}{suffix}")
    return stock_codes

def handler(event: Optional[Dict[str, Any]] = None, context: Any = None) -> List[str]:
    return get_stock_codes()

if __name__ == "__main__":
    print(json.dumps(get_stock_codes(), ensure_ascii=False))
