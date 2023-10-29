# send_ngrok_url_to_discord.py
import requests
import time
from discord_webhook import DiscordWebhook

def get_ngrok_url():
    while True:
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            response_data = response.json()
            public_url = response_data["tunnels"][0]["public_url"]
            return public_url
        except (requests.exceptions.RequestException, IndexError, KeyError):
            print("Waiting for ngrok to initialize...")
            time.sleep(2)  # wait for 2 seconds before retrying

def send_to_discord(url):
    webhook_url = 'https://discord.com/api/webhooks/1168139684690542594/gOYUZPOgg8LHbuA8ypiLvQpidR-MoilVd39cOvLw91POQTE5gyB0SPOP8va_PMpUQimR'
    webhook = DiscordWebhook(url=webhook_url, content=f'ngrok public URL: {url}')
    webhook.execute()

if __name__ == "__main__":
    ngrok_url = get_ngrok_url()
    print(ngrok_url)
    send_to_discord(ngrok_url)
