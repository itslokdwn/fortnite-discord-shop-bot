import requests
import time
import os
from datetime import datetime, timezone
from collections import defaultdict

# Discord webhook and API key stored in GitHub secrets
webhook_url = os.environ.get("DISCORD_WEBHOOK")
api_key = os.environ.get("FORTNITE_API_KEY")

# Correct endpoint for shop data.  Using the "br" endpoint is more reliable.
api_url = "https://fortnite-api.com/v2/cosmetics/br"

def send_shop_items():
    """
    Fetches Fortnite shop items and sends embeds to a Discord webhook.
    Bundles images from the same set into a single embed.
    Handles errors robustly and includes more detailed logging.
    """
    if not webhook_url or not api_key:
        print("Error: Discord Webhook URL or Fortnite API key is missing.  Ensure they are set as environment variables.")
        return

    # Add API key to headers
    headers = {
        "Authorization": api_key
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        shop_data = response.json()

        # Check if the data key exists
        if "data" not in shop_data:
            print("Error: 'data' key not found in API response.")
            print(f"Full response: {shop_data}")
            return

        # Use defaultdict to group items by set name
        items_by_set = defaultdict(list)
        for item in shop_data["data"]:
            name = item.get("name", "Unknown Item")
            image_url = item.get("images", {}).get("icon", None)
            set_name = item.get("set", {}).get("value", "No Set")  # Get set name, default to "No Set"

            if not image_url:
                print(f"Warning: No image URL found for item: {name}. Skipping.")
                continue

            items_by_set[set_name].append({
                "name": name,
                "image_url": image_url,
            })

        # Iterate through the grouped items and send embeds
        for set_name, items in items_by_set.items():
            if set_name == "No Set":
                for item in items:
                    embed = {
                        "title": f"Item Shop: {item['name']}",
                        "image": {"url": item['image_url']},
                        "color": 16753920,
                        "footer": {"text": "Fortnite Item Shop • Powered by fortnite-api.com"},
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    send_webhook_message(embed, item['name'])
            else:
                # Create a single embed for the set
                item_names = [item["name"] for item in items]
                image_urls = [item["image_url"] for item in items]

                # Construct description with item names
                description = "\n".join(f"- {name}" for name in item_names)

                # Construct image URLs for the embed.  Discord limits to 10 images.
                images = [{"url": url} for url in image_urls[:10]] # Limit to first 10 images

                embed = {
                    "title": f"Item Set: {set_name}",
                    "description": description,
                    "color": 16753920,
                    "footer": {"text": "Fortnite Item Shop • Powered by fortnite-api.com"},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "images": images #add images to embed
                }
                send_webhook_message(embed, set_name)

def send_webhook_message(embed, item_name):
    """
    Sends a Discord webhook message with the given embed.
    Handles errors robustly.
    """
    try:
        webhook_response = requests.post(webhook_url, json={"embeds": [embed]})
        webhook_response.raise_for_status()
        if webhook_response.status_code != 204:
            print(f"Warning: Discord webhook returned status code: {webhook_response.status_code} for item/set: {item_name}")
            print(webhook_response.text)
        else:
            print(f"Successfully sent item/set: {item_name} to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook for item/set: {item_name}: {e}")
    time.sleep(1)

if __name__ == "__main__":
    send_shop_items()
