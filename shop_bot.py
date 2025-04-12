import requests
import time
import os

# Discord webhook stored in GitHub secret
webhook_url = os.environ.get("DISCORD_WEBHOOK")
api_url = "https://fortnite-api.com/v2/shop/br"

def send_shop_items():
    response = requests.get(api_url)
    if response.status_code != 200:
        print("Failed to fetch shop data")
        return
    
    shop_data = response.json()
    featured_items = shop_data["data"]["featured"]["entries"]

    for entry in featured_items:
        for item in entry["items"]:
            name = item["name"]
            image_url = item["images"]["icon"]

            embed = {
                "title": f"Item Shop: {name}",
                "image": {"url": image_url},
                "color": 16753920,
                "footer": {"text": "Fortnite Item Shop • Powered by fortnite-api.com"}
            }

            requests.post(webhook_url, json={"embeds": [embed]})
            time.sleep(1)

send_shop_items()
