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
python fetch_reviews_serpapi.py
```

Enter:
- Place ID, Google Maps URL, or place name
- Start date (YYYY-MM-DD, optional)
- End date (YYYY-MM-DD, optional)
- Max pages to fetch (optional, no limit by default)

## Finding Place IDs

1. Search for place on Google Maps
2. Click "Share" > "Copy link"
3. The script will auto-extract Place ID from URL
4. Or use SerpApi search: `https://serpapi.com/search?engine=google_maps&q=Place+Name&api_key=YOUR_KEY`

## Features

- **Fetch ALL reviews** (not limited to 5)
- Pagination support (up to 20 reviews per page)
- Date range filtering
- Multiple input methods (Place ID, URL, or search)
- Sort by: newestFirst, ratingHigh, ratingLow, qualityScore
- Complete CSV with 62+ fields

## Output

Reviews saved to `reviews.csv` with all available fields:
- Basic: review_id, author_title, author_id, rating, review_text
- Dates: review_timestamp, review_datetime_utc, year, month_year
- Author: author_link, author_image, author_reviews_count
- Images: review_img_url, review_img_urls
- Responses: owner_answer, owner_answer_timestamp
- And 40+ more fields (N/A if not available)

## API Pricing

- Free: 250 searches/month
- Starter: $25/month (1,000 searches)
- Each page fetch = 1 search credit
- ~10 pages = ~200 reviews = 10 credits

## Notes

- Initial page returns 8 reviews
- Subsequent pages return up to 20 reviews
- Use `max_pages` to limit API usage
- Filter by date to save credits
