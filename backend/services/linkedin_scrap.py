import requests
import json
from dotenv import load_dotenv

load_dotenv()


def linkedin_posts_scrap(url):

    
    headers = {
        "Authorization": "Bearer ec5eb0f3-0803-4381-93b3-ca29274803ec",
        "Content-Type": "application/json",
    }

    data = json.dumps({
        "input": [{"url":url}],
    })

    response = requests.post(
        "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lyy3tktm25m4avu764&notify=false&include_errors=true&type=discover_new&discover_by=profile_url",
        headers=headers,
        data=data
    )
    print(response.text)
    try:
        data = response.json()
        if not isinstance(data, list):
            data = [data]
    except json.JSONDecodeError:
        data = [json.loads(line) for line in response.text.strip().split('\n') if line.strip()]

    print("\n"*2 , "-----------------------------Posts Data----------------------------------" , "\n"*2)
    return data




def linkedin_profile_scrap(url):

    
    headers = {
        "Authorization": "Bearer ec5eb0f3-0803-4381-93b3-ca29274803ec",
        "Content-Type": "application/json",
    }

    data = json.dumps({
        "input": [{"url":url}],
    })

    response = requests.post(
        "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l1viktl72bvl7bjuj0&notify=false&include_errors=true",
        headers=headers,
        data=data
    )

    print(response.text)
    try:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
    except json.JSONDecodeError:
        items = [json.loads(line) for line in response.text.strip().split('\n') if line.strip()]
        data = items[0] if items else {}

    print("\n"*2 , "-----------------------------Profile Data----------------------------------" , "\n"*2)
    print(data)
    return data

def overall_scrap(url):
    posts_data = linkedin_posts_scrap(url)
    profile_data = linkedin_profile_scrap(url)
    return {
        "posts": posts_data,
        "profile": profile_data
    }
