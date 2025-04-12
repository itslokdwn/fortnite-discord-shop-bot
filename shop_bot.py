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


def send_bundled_new_cosmetics():
    """
    Fetches new Fortnite cosmetics and bundles items with the same name
    into a single, larger embed for each unique item name.
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

        bundled_items = {}
        for item in new_items["br"]:
            name = item.get("name")
            if name:
                if name not in bundled_items:
                    bundled_items[name] = []
                bundled_items[name].append(item)

        for name, items in bundled_items.items():
            if not items:
                continue

            # Use the data from the first item as the primary information for the embed
            first_item = items[0]
            description = first_item.get("description")
            image_url = first_item.get("images", {}).get("icon")

            if not image_url:
                print(f"Warning: No image URL found for item group: {name}. Skipping.")
                continue

            embed = {
                "title": f"New Cosmetics: {name}",
                "color": 5763719,  # Soft blue color
                "fields": [],
                "image": {"url": image_url},
                "footer": {"text": "Fortnite New Cosmetics • Powered by fortnite-api.com"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            if description:
                embed["description"] = description

            # Add details for each individual item with the same name
            for item in items:
                item_type_data = item.get("type", {})
                item_type = item_type_data.get("displayValue")
                rarity_data = item.get("rarity", {})
                rarity = rarity_data.get("displayValue")
                added_date = item.get("added")
                item_id = item.get("id")

                details = ""
                if item_type:
                    details += f"**Type:** {item_type}\n"
                if rarity:
                    details += f"**Rarity:** {rarity}\n"
                if added_date:
                    details += f"**Added:** {added_date}\n"
                if item_id:
                    details += f"**ID:** `{item_id}`\n"  # Added item ID for more detail

                if details:
                    # Truncate details if it gets too long to avoid embed limits
                    if len(details) > 1000:
                        details = details[:1000] + "...\n(Details truncated)"
                    embed["fields"].append({"name": "Variant Details", "value": details, "inline": False})

            webhook_response = requests.post(webhook_url, json={"embeds": [embed]})
            if webhook_response.status_code != 204:
                print(f"Failed to send webhook for {name}: {webhook_response.status_code}")
                print(webhook_response.text)

            time.sleep(1)  # Small delay

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Fortnite API: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response text: {response.text}")


if __name__ == "__main__":
    send_bundled_new_cosmetics()
