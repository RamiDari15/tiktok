import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent, DisconnectEvent

USERNAME = "yoitsmadijo"


async def run_client():
    client = TikTokLiveClient(unique_id=USERNAME)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"Connected to @{USERNAME}'s live!")

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        if event.gift.streakable and not event.streaking:
            print(f"{event.user.unique_id} sent {event.repeat_count}x \"{event.gift.name}\"")

        elif not event.gift.streakable:
            print(f"{event.user.unique_id} sent \"{event.gift.name}\"")

    @client.on(DisconnectEvent)
    async def on_disconnect(event: DisconnectEvent):
        print("Live ended or disconnected.")

    await client.start()


async def monitor_live():
    while True:
        try:
            print("Waiting for live...")
            await run_client()
        except Exception as e:
            print(f"Error: {e}")

        print("Rechecking in 15 seconds...\n")
        await asyncio.sleep(15)


if __name__ == "__main__":
    asyncio.run(monitor_live())
