import requests
import time
import os

# Discord webhook and API key stored in GitHub secrets
webhook_url = os.environ.get("DISCORD_WEBHOOK")
api_key = os.environ.get("FORTNITE_API_KEY")

# Correct endpoint for shop data
api_url = "https://fortnite-api.com/v2/cosmetics/new"

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
        
    featured_entries = shop_data["data"]["featured"]["entries"]
    
    for entry in featured_entries:
        items = entry.get("items", [])
        for item in items:
            name = item.get("name", "Unknown Item")
            image_url = item.get("images", {}).get("icon", None)
            
            if not image_url:
                continue
                
            embed = {
                "title": f"Item Shop: {name}",
                "image": {"url": image_url},
                "color": 16753920,  # Orange color
                "footer": {"text": "Fortnite Item Shop • Powered by fortnite-api.com"}
            }
            
            webhook_response = requests.post(webhook_url, json={"embeds": [embed]})
            if webhook_response.status_code != 204:
                print(f"Failed to send webhook: {webhook_response.status_code}")
                print(webhook_response.text)
            
            # Add a delay to avoid rate limiting
            time.sleep(1)

send_shop_items()
