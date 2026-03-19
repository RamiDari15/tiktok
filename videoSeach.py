from tikapi import TikAPI, ValidationException, ResponseException
import time

API_KEY = "LxcVXRgh5Asr59aQvc2GNHRbz4gTUh1IFLHZHuBjIqRMO8RK"
ACCOUNT_KEY = "yrpU9zKnAbOJ3jrYvH8WFQE5pBhDHHYJz8afEenzNp5WGJie"

QUERY = "usa"   # change this to whatever you want

api = TikAPI(API_KEY)

User = api.user(
    accountKey=ACCOUNT_KEY
)

cursor = 0
page = 1

try:
    while True:

        print(f"\n--- PAGE {page} | CURSOR {cursor} ---")

        response = User.live.search(
            query=QUERY,
            cursor=cursor
        )

        data = response.json()

        lives = data.get("lives", [])

        print(f"Found {len(lives)} live results")

        for live in lives:
            try:
                username = live["author"]["unique_id"]
                viewers = live.get("viewer_count", "N/A")

                print(f"{username} | viewers: {viewers}")

            except:
                pass

        # update cursor for next request
        new_cursor = data.get("cursor")

        if new_cursor is None or new_cursor == cursor:
            print("\nNo more pages.")
            break

        cursor = new_cursor
        page += 1

        time.sleep(1)

except ValidationException as e:
    print("Validation error:", e, e.field)

except ResponseException as e:
    print("Response error:", e, e.response.status_code)