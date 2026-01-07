++---
# list-all-stocks

Simple script to fetch listed companies from IDX using their public endpoint.

Usage

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Run the script:

```bash
python3 main.py
```

The script prints one line per company: the IDX code with `.JK` suffix followed by the company's JSON.

If you prefer the previous Selenium approach, ensure `chromedriver` and a headless chromium binary are available and update the old code accordingly.
