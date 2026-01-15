# list-all-stocks

Simple Python script to fetch listed companies from Indonesia Stock Exchange (IDX) using their public API endpoint.

## Usage

Run the script directly:

```bash
python3 main.py
```

## Output

The script prints one line per company: the IDX ticker symbol with `.JK` suffix followed by the company's JSON data.

Example output:
```
Found 700 companies
BBCA.JK {"KodeEmiten":"BBCA","NamaEmiten":"Bank Central Asia Tbk",...}
TLKM.JK {"KodeEmiten":"TLKM","NamaEmiten":"Telkom Indonesia (Persero) Tbk",...}
...
```

## Requirements

Python 3.6+ (uses only standard library: `json`, `sys`, `urllib.request`)

No external dependencies required.
