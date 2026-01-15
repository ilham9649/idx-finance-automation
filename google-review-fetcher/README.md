# Google Review Checker

Fetch ALL Google Place reviews (not just 5) using SerpApi and save to CSV.

## Setup

1. Get SerpApi Key:
    - Go to [SerpApi](https://serpapi.com/)
    - Sign up for free account (250 searches/month free)
    - Get your API key from dashboard

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set environment variable:
    ```bash
    export SERPAPI_KEY=your_api_key_here
    # or
    cp .env.example .env
    # edit .env with your key
    ```

## Usage

```bash
python fetch_reviews.py
```

Enter:
- Google Maps URL, Place ID, or place name
- Start date (YYYY-MM-DD, optional)
- End date (YYYY-MM-DD, optional)
- Max pages to fetch (optional, no limit by default)

## Input Methods

1. **Google Maps URL** - Extracts CID (data_id) automatically
   - Most accurate - gets exact place from URL
   - No additional API calls needed
   - Works with: `google.com/maps/place/...` URLs

2. **Place ID** - Direct SerpApi place_id
   - Format: `ChIJlaZhyIAWei4R9jMN_ZJEBbI`

3. **Place Name** - Searches and gets first result
   - Less accurate if multiple locations exist
   - Use only if URL or Place ID not available

## Features

- **Fetch ALL reviews** (not limited to 5)
- **Uses CID directly** - more accurate than place name search
- **Incremental saving** - saves to CSV after each page (won't lose data if script fails)
- **Retry logic** - automatically retries failed requests (3 attempts with exponential backoff)
- **Rate limiting protection** - adds delays between requests
- Pagination support (up to 20 reviews per page)
- Date range filtering
- Sort by: newestFirst, ratingHigh, ratingLow, qualityScore
- Complete CSV with 58+ fields

## Output

Reviews saved to `reviews.csv` with all available fields:
- **Incremental saves**: Each page is saved immediately (page 1, 2, 3...)
- **Basic**: review_id, author_title, author_id, rating, review_text
- **Dates**: review_timestamp, review_datetime_utc, year, month_year
- **Author**: author_link, author_image, author_reviews_count
- **Images**: review_img_url, review_img_urls
- **Responses**: owner_answer, owner_answer_timestamp
- And 40+ more fields (empty if not available)

## Error Handling

- **Connection errors**: Auto-retries up to 3 times with exponential backoff (2s, 4s, 6s)
- **Connection reset by peer**: Automatically retried
- **Data safety**: Reviews are saved incrementally, so you won't lose data even if the script fails

## API Pricing

- Free: 250 searches/month
- Starter: $25/month (1,000 searches)
- Each page fetch = 1 search credit
- ~10 pages = ~200 reviews = 10 credits

## Notes

- **Google Maps URL is most accurate** - uses exact place ID from URL
- Initial page returns 8 reviews
- Subsequent pages return up to 20 reviews
- Use `max_pages` to limit API usage
- Filter by date to save credits
- Only SERPAPI_KEY required (no Google Places API needed)
- Reviews are saved after **each page** (not at the end) for data safety
