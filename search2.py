import asyncio
from tikapi import TikAPI, ValidationException, ResponseException
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent

# ---- CONFIG ----
API_KEY = "Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av"
ACCOUNT_KEY = "a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"


api = TikAPI(API_KEY)
User = api.user(accountKey=ACCOUNT_KEY)

def fetch_live_usernames(limit=10):
    try:
        response = User.live.search(query="live")
        data = response.json()

        users = []

        for item in data["data"][:limit]:
            username = item["live_info"]["owner"]["display_id"]
            users.append(username)

        print("\n✅ Extracted Usernames:")
        for u in users:
            print(u)

        return users

    except ValidationException as e:
        print("Validation Error:", e, e.field)

    except ResponseException as e:
        print("Response Error:", e, e.response.status_code)

    except Exception as e:
        print("General Error:", e)

    return []


if __name__ == "__main__":
    fetch_live_usernames()

