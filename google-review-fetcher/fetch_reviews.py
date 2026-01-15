import requests
import csv
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SerpApiReviewFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def extract_place_id_from_url(self, url: str) -> Optional[str]:
        """Extract place_id from Google Maps URL"""
        # Add https://www. if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://www.' + url
        
        # Extract CID (format: 0x[hex]:0x[hex])
        match = re.search(r'!1s(0x[0-9a-f]+:0x[0-9a-f]+)', url)
        if match:
            cid = match.group(1)
            print(f"Extracted CID: {cid}")
            result = self.get_place_id_from_cid(cid)
            if not result:
                # If CID conversion fails, try extracting search query from URL
                query_match = re.search(r'!1s([^:]+)', url)
                if query_match:
                    query = query_match.group(1)
                    if not query.startswith('0x'):
                        # This is a search query, not a CID
                        query = query.replace('+', ' ')
                        print(f"Searching by query: {query}")
                        result = self.get_place_id_from_name(query)
                else:
                    # Fallback to place name from URL
                    name_match = re.search(r'/place/([^/@]+)', url)
                    if name_match:
                        place_name = name_match.group(1).replace('+', ' ')
                        print(f"Searching by place name instead: {place_name}")
                        result = self.get_place_id_from_name(place_name)
            return result
        
        # Try to extract from /g/ format
        match = re.search(r'/g/([^/?]+)', url)
        if match:
            g_id = match.group(1)
            print(f"Extracted G ID: {g_id}")
            return None
        
        return None
    
    def get_place_id_from_cid(self, cid: str) -> Optional[str]:
        """Get place_id using Google Places API with CID"""
        params = {
            "cid": cid,
            "fields": "place_id,name",
            "key": os.getenv("GOOGLE_PLACES_API_KEY", "")
        }
        
        try:
            response = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params=params, timeout=10)
            data = response.json()
            if data.get("status") == "OK":
                place_id = data["result"].get("place_id")
                place_name = data["result"].get("name", "")
                print(f"Found Place ID: {place_id} for {place_name}")
                return place_id
            else:
                print(f"Google Places API error: {data.get('status', 'Unknown')}")
        except Exception as e:
            print(f"Error getting place_id from CID: {e}")
        return None
    
    def get_place_id_from_name(self, name: str) -> Optional[str]:
        """Get place_id from place name using SerpApi"""
        params = {
            "engine": "google_maps",
            "q": name,
            "api_key": self.api_key,
            "type": "search"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "local_results" in data and data["local_results"]:
                return data["local_results"][0].get("place_id")
            elif "place_results" in data and data["place_results"]:
                return data["place_results"][0].get("place_id")
        except Exception as e:
            print(f"Error searching for place: {e}")
        
        return None
    
    def fetch_reviews_page(self, place_id: str, next_page_token: Optional[str] = None, num: int = 20) -> Dict:
        """Fetch a single page of reviews by place_id"""
        params = {
            "engine": "google_maps_reviews",
            "place_id": place_id,
            "api_key": self.api_key
        }
        
        if next_page_token:
            params["next_page_token"] = next_page_token
            params["num"] = str(num)
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_reviews_page_by_data_id(self, data_id: str, next_page_token: Optional[str] = None, num: int = 20) -> Dict:
        """Fetch a single page of reviews by data_id (CID)"""
        params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "api_key": self.api_key
        }
        
        if next_page_token:
            params["next_page_token"] = next_page_token
            params["num"] = str(num)
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_all_reviews(self, place_id: str = None, data_id: str = None, sort_by: str = "newestFirst", max_pages: Optional[int] = None) -> List[Dict]:
        """Fetch all reviews with pagination"""
        all_reviews = []
        next_page_token = None
        page = 0
        
        print(f"Fetching reviews (sort: {sort_by})...")
        
        while True:
            if max_pages and page >= max_pages:
                print(f"Reached max pages limit: {max_pages}")
                break
            
            print(f"Fetching page {page + 1}...", end=" ")
            
            data = self.fetch_reviews_page(place_id, next_page_token)
            
            if "reviews" not in data:
                print("No reviews found")
                break
            
            page_reviews = data["reviews"]
            all_reviews.extend(page_reviews)
            print(f"Got {len(page_reviews)} reviews")
            
            next_page_token = data.get("serpapi_pagination", {}).get("next_page_token")
            if not next_page_token:
                print("No more pages")
                break
            
            page += 1
        
        print(f"\nTotal reviews fetched: {len(all_reviews)}")
        return all_reviews
    
    def format_review(self, review: Dict, place_id: str) -> Dict:
        """Format review to match CSV schema"""
        iso_date = review.get("iso_date", "")
        review_date = None
        
        if iso_date:
            try:
                review_date = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
            except:
                pass
        
        images = review.get("images", [])
        image_urls = images if isinstance(images, list) else []
        
        owner_answer = review.get("owner_answer", {})
        
        user = review.get("user", {})
        
        return {
            "query": "",
            "name": "",
            "google_id": "",
            "place_id": place_id,
            "location_link": "",
            "reviews_link": "",
            "reviews": "",
            "rating": review.get("rating"),
            "review_id": review.get("review_id", ""),
            "review_pagination_id": "",
            "author_link": user.get("link", ""),
            "author_title": user.get("name", ""),
            "author_id": user.get("contributor_id", ""),
            "author_image": user.get("thumbnail", ""),
            "author_reviews_count": user.get("reviews", ""),
            "author_ratings_count": "",
            "review_text": review.get("snippet", ""),
            "review_img_urls": "|".join(image_urls),
            "review_img_url": image_urls[0] if image_urls else "",
            "review_photo_ids": "",
            "owner_answer": owner_answer.get("answer", "") if owner_answer else "",
            "owner_answer_timestamp": owner_answer.get("time", "") if owner_answer else "",
            "owner_answer_timestamp_datetime_utc": datetime.fromtimestamp(owner_answer.get("time", 0)).isoformat() if owner_answer and owner_answer.get("time") else "",
            "review_link": review.get("link", ""),
            "review_rating": review.get("rating"),
            "review_timestamp": review.get("iso_date", ""),
            "review_datetime_utc": review_date.isoformat() if review_date else "",
            "months": "",
            "year": review_date.year if review_date else "",
            "month_year": review_date.strftime("%Y-%m") if review_date else "",
            "review_likes": review.get("likes", ""),
            "reviews_id": "",
            "reviews_per_score_1": "",
            "reviews_per_score_2": "",
            "reviews_per_score_3": "",
            "reviews_per_score_4": "",
            "reviews_per_score_5": "",
            "review_questions_Service": "",
            "review_questions_Meal type": "",
            "review_questions_Food": "",
            "review_questions_Atmosphere": "",
            "review_questions_Price per person": "",
            "review_questions_Recommended dishes": "",
            "review_questions": "",
            "review_questions_Noise level": "",
            "review_questions_Wait time": "",
            "review_questions_Group size": "",
            "review_questions_Special offers": "",
            "review_questions_Parking space": "",
            "review_questions_Parking options": "",
            "review_questions_None": "",
            "review_questions_Dietary restrictions": "",
            "review_questions_Vegetarian options": "",
            "review_questions_Parking": "",
            "review_questions_Kid-friendliness": "",
            "review_questions_Wheelchair accessibility": "",
            "review_questions_Reservation": "",
            "review_questions_Seating type": ""
        }
    
    def save_to_csv(self, reviews: List[Dict], filename: str = "reviews.csv"):
        """Save reviews to CSV file"""
        if not reviews:
            print("No reviews to save")
            return
        
        fieldnames = ["query", "name", "google_id", "place_id", "location_link", "reviews_link", "reviews", "rating", "review_id", "review_pagination_id", "author_link", "author_title", "author_id", "author_image", "author_reviews_count", "author_ratings_count", "review_text", "review_img_urls", "review_img_url", "review_photo_ids", "owner_answer", "owner_answer_timestamp", "owner_answer_timestamp_datetime_utc", "review_link", "review_rating", "review_timestamp", "review_datetime_utc", "months", "year", "month_year", "review_likes", "reviews_id", "reviews_per_score_1", "reviews_per_score_2", "reviews_per_score_3", "reviews_per_score_4", "reviews_per_score_5", "review_questions_Service", "review_questions_Meal type", "review_questions_Food", "review_questions_Atmosphere", "review_questions_Price per person", "review_questions_Recommended dishes", "review_questions", "review_questions_Noise level", "review_questions_Wait time", "review_questions_Group size", "review_questions_Special offers", "review_questions_Parking space", "review_questions_Parking options", "review_questions_None", "review_questions_Dietary restrictions", "review_questions_Vegetarian options", "review_questions_Parking", "review_questions_Kid-friendliness", "review_questions_Wheelchair accessibility", "review_questions_Reservation", "review_questions_Seating type"]
        
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reviews)
        
        print(f"Saved {len(reviews)} reviews to {filename}")
    
    def filter_by_date(self, reviews: List[Dict], start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Filter reviews by date range"""
        if not start_date and not end_date:
            return reviews
        
        filtered = []
        for review in reviews:
            date_str = review.get("review_datetime_utc", "")
            if not date_str:
                continue
            
            try:
                review_date = datetime.fromisoformat(date_str)
                # Remove timezone for comparison
                review_date = review_date.replace(tzinfo=None)
            except:
                continue
            
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                if review_date < start_dt:
                    continue
            
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                if review_date > end_dt:
                    continue
            
            filtered.append(review)
        
        return filtered

def main():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("Please set SERPAPI_KEY environment variable")
        return
    
    input_str = input("Enter Place ID, Google Maps URL, or place name: ").strip()
    start_date = input("Start date (YYYY-MM-DD, or press Enter to skip): ").strip() or None
    end_date = input("End date (YYYY-MM-DD, or press Enter to skip): ").strip() or None
    max_pages_input = input("Max pages to fetch (or press Enter for all): ").strip() or None
    max_pages = int(max_pages_input) if max_pages_input else None
    
    fetcher = SerpApiReviewFetcher(api_key)
    place_id = None
    
    try:
        if "maps.google.com" in input_str or "goo.gl/maps" in input_str:
            place_id = fetcher.extract_place_id_from_url(input_str)
        elif not input_str.startswith("ChIJ"):
            place_id = fetcher.get_place_id_from_name(input_str)
        else:
            place_id = input_str
        
        if not place_id:
            print("Could not find Place ID")
            return
        
        print(f"Place ID: {place_id}")
        
        reviews_data = fetcher.fetch_all_reviews(place_id, sort_by="newestFirst", max_pages=max_pages)
        
        formatted_reviews = [fetcher.format_review(r, place_id) for r in reviews_data]
        
        if start_date or end_date:
            original_count = len(formatted_reviews)
            formatted_reviews = fetcher.filter_by_date(formatted_reviews, start_date, end_date)
            print(f"Filtered from {original_count} to {len(formatted_reviews)} reviews")
        
        fetcher.save_to_csv(formatted_reviews)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
