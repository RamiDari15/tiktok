

import asyncio
import time
from datetime import datetime
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent, DisconnectEvent
from TikTokLive.client.errors import SignatureRateLimitError
from tikapi import TikAPI
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- FIREBASE ----------------

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- CONFIG ----------------



TIKAPI_KEY = "Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av"
ACCOUNT_KEY = "a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"

api = TikAPI(TIKAPI_KEY)

MAX_CONCURRENT =    5  # reduced to avoid rate limits
CONNECTION_DELAY = 20  # seconds between new connections
REPLACEMENT_DELAY = 60  # wait before replacing offline user

active_users = {}
connection_semaphore = asyncio.Semaphore(1)  # only 1 signature request at a time


# ---------------- LIVE TRACKER ----------------

class LiveTracker:

    def __init__(self, username):
        self.username = username
        self.client = TikTokLiveClient(unique_id=username)
        self.diamond_counter = 0
        self.start_time = datetime.utcnow()
        self.live_id = str(int(time.time()))
        self.register_events()

    def register_events(self):

        @self.client.on(ConnectEvent)
        async def on_connect(event):
            print(f"✅ Connected: {self.username}")

        @self.client.on(GiftEvent)
        async def on_gift(event):

            diamonds = event.gift.diamond_count or 0

            if event.gift.streakable and not event.streaking:
                diamonds *= event.repeat_count

            self.diamond_counter += diamonds

            print(f"{self.username} +{diamonds} | Total: {self.diamond_counter}")

        @self.client.on(DisconnectEvent)
        async def on_disconnect(event):
            print(f"❌ Disconnected: {self.username}")
            await self.handle_live_end()

    async def handle_live_end(self):

        end_time = datetime.utcnow()
        user_ref = db.collection("users").document(self.username)

        doc = user_ref.get()

        lifetime = 0
        total_lives = 0

        if doc.exists:
            data = doc.to_dict()
            lifetime = data.get("lifetimeDiamonds", 0)
            total_lives = data.get("totalLives", 0)

        lifetime += self.diamond_counter
        total_lives += 1

        user_ref.set({
            "lifetimeDiamonds": lifetime,
            "lastLiveDiamonds": self.diamond_counter,
            "totalLives": total_lives,
            "lastUpdated": firestore.SERVER_TIMESTAMP
        }, merge=True)

        user_ref.collection("lives").document(self.live_id).set({
            "diamonds": self.diamond_counter,
            "startTime": self.start_time,
            "endTime": end_time
        })

        active_users.pop(self.username, None)

        print(f"📦 Stored stats for {self.username}")

        await asyncio.sleep(REPLACEMENT_DELAY)
        await add_new_live_user()

    async def start(self):

        async with connection_semaphore:
            await asyncio.sleep(CONNECTION_DELAY)

            try:
                await self.client.start()
            except SignatureRateLimitError:
                print("⚠️ Signature rate limit hit. Cooling down...")
                await asyncio.sleep(600)  # 10 minute cooldown
            except Exception as e:
                print(f"Error connecting {self.username}: {e}")


# ---------------- GET LIVE USER ----------------

def get_live_user():

    User = api.user(accountKey=ACCOUNT_KEY)
    response = User.live.search(query="gaming")
    data = response.json()

    for item in data.get("data", []):
        username = item["live_info"]["owner"]["display_id"]
        if username not in active_users:
            return username

    return None


# ---------------- ADD NEW USER ----------------

async def add_new_live_user():

    if len(active_users) >= MAX_CONCURRENT:
        return

    username = get_live_user()
    if not username:
        return

    tracker = LiveTracker(username)
    active_users[username] = tracker

    asyncio.create_task(tracker.start())


# ---------------- MANAGER LOOP ----------------

async def manager():

    # Initial fill
    for _ in range(MAX_CONCURRENT):
        await add_new_live_user()

    while True:
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(manager())
