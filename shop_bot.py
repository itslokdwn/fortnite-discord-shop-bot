import requests
import time
import os
from datetime import datetime, timezone

# Discord webhook and API key stored in GitHub secrets
webhook_url = os.environ.get("DISCORD_WEBHOOK")
api_key = os.environ.get("FORTNITE_API_KEY")

# Correct endpoint for shop data.  
api_url = "https://fortnite-api.com/v2/cosmetics/new"

def send_shop_items():
    """
    Fetches Fortnite shop items and sends embeds to a Discord webhook.
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

        # Iterate through all items in the data list.  The /br endpoint returns a list.
        for item in shop_data["data"]:
            name = item.get("name", "Unknown Item")
            # Use a more robust way to get the image URL, handling potential nested None values.
            image_url = item.get("images", {}).get("icon", None)

            if not image_url:
                print(f"Warning: No image URL found for item: {name}. Skipping.")
                continue

            embed = {
                "title": f"Item Shop: {name}",
                "image": {"url": image_url},
                "color": 16753920,  # Orange color
                "footer": {"text": "Fortnite Item Shop • Powered by fortnite-api.com"},
                "timestamp": datetime.now(timezone.utc).isoformat() # Add timestamp
            }

            try:
                webhook_response = requests.post(webhook_url, json={"embeds": [embed]})
                webhook_response.raise_for_status() # Raise exception for bad status
                if webhook_response.status_code != 204:
                    print(f"Warning: Discord webhook returned status code: {webhook_response.status_code} for item: {name}")
                    print(webhook_response.text) #print the error
                else:
                    print(f"Successfully sent item: {name} to Discord.") # Added success message
            except requests.exceptions.RequestException as e:
                print(f"Error sending webhook for item: {name}: {e}")

            # Add a delay to avoid rate limiting, and make it configurable
            time.sleep(1) # 1 second delay

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Fortnite API: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response text: {response.text}")  # Print the response text to help debug JSON issues


if __name__ == "__main__":
    send_shop_items()
