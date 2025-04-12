import requests
import time
import os
from datetime import datetime, timezone
import json

# Discord webhook and API key stored in GitHub secrets
webhook_url = os.environ.get("DISCORD_WEBHOOK")
api_key = os.environ.get("FORTNITE_API_KEY")

# Correct endpoint for new cosmetics data
api_url = "https://fortnite-api.com/v2/cosmetics/new"


def send_new_cosmetics():
    """
    Fetches new Fortnite cosmetics and sends an embed to a Discord webhook
    with the information provided in the JSON data.
    Skips adding fields to the embed if the corresponding data is null or missing.
    Handles errors robustly and includes detailed logging.
    """
    if not webhook_url or not api_key:
        print("Error: Discord Webhook URL or Fortnite API key is missing. Ensure they are set as environment variables.")
        return

    headers = {
        "Authorization": api_key
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        cosmetics_data = response.json()

        if "data" not in cosmetics_data:
            print("Error: 'data' key not found in API response.")
            print(f"Full response: {cosmetics_data}")
            return

        new_items = cosmetics_data["data"].get("items", [])

        if not new_items:
            print("No new items found in the API response.")
            return

        for item in new_items["br"]:  # Assuming 'br' key contains the relevant items
            name = item.get("name", "Unknown Item")
            description = item.get("description")
            item_type_data = item.get("type", {})
            item_type = item_type_data.get("displayValue")
            rarity_data = item.get("rarity", {})
            rarity = rarity_data.get("displayValue")
            image_url = item.get("images", {}).get("icon")
            added_date = item.get("added")

            if not image_url:
                print(f"Warning: No image URL found for item: {name}. Skipping.")
                continue

            embed = {
                "title": f"New Cosmetic: {name}",
                "color": 5763719,  # Soft blue color
                "fields": [],
                "image": {"url": image_url},
                "footer": {"text": "Fortnite New Cosmetics • Powered by fortnite-api.com"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            if description:
                embed["description"] = description

            if item_type:
                embed["fields"].append({"name": "Type", "value": item_type, "inline": True})

            if rarity:
                embed["fields"].append({"name": "Rarity", "value": rarity, "inline": True})

            if added_date:
                embed["fields"].append({"name": "Added", "value": added_date, "inline": False})

            webhook_response = requests.post(webhook_url, json={"embeds": [embed]})
            if webhook_response.status_code != 204:
                print(f"Failed to send webhook for {name}: {webhook_response.status_code}")
                print(webhook_response.text)

            time.sleep(1)  # Small delay to avoid rate limiting

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Fortnite API: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response text: {response.text}")


if __name__ == "__main__":
    send_new_cosmetics()
