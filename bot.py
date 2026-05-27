import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "messages.txt")

if not TOKEN or not CHANNEL_ID:
    raise SystemExit("Error: DISCORD_TOKEN and CHANNEL_ID must be set in .env")

HEADERS = {"Authorization": TOKEN}
API = "https://discord.com/api/v10"


def fetch_messages(channel_id):
    messages = []
    before = None

    print("Fetching messages...")
    while True:
        params = {"limit": 100}
        if before:
            params["before"] = before

        r = requests.get(f"{API}/channels/{channel_id}/messages", headers=HEADERS, params=params)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            break

        batch = r.json()
        if not batch:
            break

        messages.extend(batch)
        before = batch[-1]["id"]
        print(f"  {len(messages)} messages fetched...", end="\r")
        time.sleep(0.5)

    messages.reverse()
    print(f"\nDone. {len(messages)} messages total.")
    return messages


def format_message(msg):
    ts = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
    timestamp = ts.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    author = msg["author"].get("global_name") or msg["author"]["username"]
    content = msg.get("content", "")

    for attachment in msg.get("attachments", []):
        content += f" [attachment: {attachment['url']}]"
    for embed in msg.get("embeds", []):
        if embed.get("url"):
            content += f" [embed: {embed['url']}]"

    return f"[{timestamp}] {author}: {content}"


def save(messages, path):
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            f.write(format_message(msg) + "\n")
    print(f"Saved to {path}")


if __name__ == "__main__":
    msgs = fetch_messages(CHANNEL_ID)
    save(msgs, OUTPUT_FILE)

    print("\n--- Preview (last 5) ---")
    for msg in msgs[-5:]:
        print(format_message(msg))
