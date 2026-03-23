import os
import json
from flask import Blueprint, request, jsonify
from services.linkedin_scrap import overall_scrap
from services.x_scrap import scrape_x_profile
from services.rag_service import invalidate_cache

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['POST'])
def receive_profile_urls():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
        linkedin_url = data.get('linkedin_url')
        x_url = data.get('x_url')
        
        # LinkedIn URL is mandatory according to requirements
        if not linkedin_url:
            return jsonify({"status": "error", "message": "LinkedIn URL is mandatory"}), 400
            
        # Execute scrapers
        scraped_data = {}
        
        try:
            print(f"Scraping LinkedIn for {linkedin_url}...")
            linkedin_data = overall_scrap(linkedin_url)
            scraped_data["linkedin"] = linkedin_data
        except Exception as e:
            print(f"LinkedIn scraping failed: {e}")
            scraped_data["linkedin"] = {"error": str(e)}
            
        if x_url:
            try:
                print(f"Scraping X for {x_url}...")
                x_data = scrape_x_profile(x_url)
                scraped_data["x"] = x_data
            except Exception as e:
                print(f"X scraping failed: {e}")
                scraped_data["x"] = {"error": str(e)}
                
        # Extract a clean username from LinkedIn URL for the filename
        username = linkedin_url.rstrip('/').split('/')[-1]
        
        # Bust the in-memory RAG cache so next chat uses fresh embeddings
        invalidate_cache(username)
        
        # Save the data to a local file for RAG consumption later
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        
        data_file_path = os.path.join(data_dir, f"{username}_profile.json")
        with open(data_file_path, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=4)
            
        print(f"Saved profile data to {data_file_path}")
        
        return jsonify({
            "status": "success",
            "message": "Profile data scraped and saved successfully",
            "data": scraped_data
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
