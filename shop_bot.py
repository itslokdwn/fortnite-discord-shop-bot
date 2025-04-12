import requests
import time
import os

# Discord webhook and API key stored in GitHub secrets
webhook_url = os.environ.get("DISCORD_WEBHOOK")
api_key = os.environ.get("FORTNITE_API_KEY")  # Add this to your GitHub secrets

# Correct endpoint for shop data
api_url = "https://fortnite-api.com/v2/cosmetics"

def send_shop_items():
    # Add API key to headers
    headers = {
        "Authorization": api_key
    }
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch shop data: {response.status_code}")
        print(response.text)
        return
    
    shop_data = response.json()
    
    # Check if the featured section exists
    if "featured" not in shop_data["data"]:
        print("No featured items found in the shop data")
        return
        
    featured_items = shop_data["data"]["featured"]["entries"]
    for entry in featured_items:
        # Some entries might have multiple items
        for item in entry["items"]:
            name = item["name"]
            # Use the proper image URL path
            image_url = item["images"]["icon"]
            
            embed = {
                "title": f"Item Shop: {name}",
                "image": {"url": image_url},
                "color": 16753920,
                "footer": {"text": "Fortnite Item Shop • Powered by fortnite-api.com"}
            }
            
            webhook_response = requests.post(webhook_url, json={"embeds": [embed]})
            if webhook_response.status_code != 204:
                print(f"Failed to send webhook: {webhook_response.status_code}")
            
            # Add a delay to avoid rate limiting
            time.sleep(1)

send_shop_items()
