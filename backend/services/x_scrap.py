import requests
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def scrape_x_profile(profile_url):
    try:
        print(f"\n--- Starting X Scraping (Bright Data) for {profile_url} ---")
        
        key = os.getenv("BRIGHT_DATA_KEY") #put your key here
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

        data = json.dumps({
            "input": [{"url": profile_url, "max_number_of_posts": 10}],
        })

        response = requests.post(
            "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lwxmeb2u1cniijd7t4&notify=false&include_errors=true",
            headers=headers,
            data=data
        )

        print(f"Response Status Code: {response.status_code}")
        obj = response.json()

        # Bright Data returns a single profile dict directly
        # Extract posts: each post has a 'description' field
        posts = obj.get("posts") or []
        recent_tweets = [p.get("description", "") for p in posts if p.get("description")]

        mapped_data = {
            "profile_name": obj.get("profile_name"),
            "description": obj.get("biography", ""),
            "location": obj.get("location"),
            "is_verified": obj.get("is_verified"),
            "external_link": obj.get("external_link"),
            "public_metrics": {
                "followers_count": obj.get("followers", 0),
                "following_count": obj.get("following", 0),
                "posts_count": obj.get("posts_count", 0),
            },
            "recent_tweets": recent_tweets
        }

        print(f"Successfully scraped {len(recent_tweets)} X posts!")
        return {"data": mapped_data}

    except Exception as e:
        print(f"Error scraping X via Bright Data: {e}")
        return None
