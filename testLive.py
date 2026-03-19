import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent, DisconnectEvent

USERNAME = "hayley.streams"


async def run_client():

    while True:  # ← this keeps it always alive

        try:
            print(f"\n🔄 Attempting to connect to @{USERNAME}...")

            client = TikTokLiveClient(unique_id=USERNAME)

            @client.on(ConnectEvent)
            async def on_connect(event):
                print(f"✅ Connected to @{USERNAME}")

            @client.on(GiftEvent)
            async def on_gift(event):
                print("🎁 GIFT EVENT")
                print("Gift:", event.gift.name)
                print("Diamond Count:", getattr(event.gift, "diamond_count", "N/A"))

            @client.on(DisconnectEvent)
            async def on_disconnect(event):
                print("❌ Disconnected — Live ended")

            await client.start()

        except Exception as e:
            print("⚠️ Error:", e)

        print("⏳ Rechecking in 10 seconds...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run_client())
