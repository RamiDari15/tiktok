from tikapi import TikAPI, ValidationException, ResponseException

API_KEY = "LxcVXRgh5Asr59aQvc2GNHRbz4gTUh1IFLHZHuBjIqRMO8RK"
ACCOUNT_KEY = "yrpU9zKnAbOJ3jrYvH8WFQE5pBhDHHYJz8afEenzNp5WGJie"
QUERY = "usa"

api = TikAPI(API_KEY)

User = api.user(accountKey=ACCOUNT_KEY)
cursor = 0
max_pages = 10

try:
    for page in range(max_pages):

        print(f"\n--- PAGE {page + 1} ---")

        response = User.live.search(
            query=QUERY,
            cursor=cursor
        )

        data = response.json()
        lives = data.get("data", [])


        for live in lives:
            username = live["live_info"]["owner"]["display_id"]
            if username:
                print(username)

        # Update cursor for next request
        cursor = data.get("cursor")

        if not cursor:
            print("No more results.")
            break

except ValidationException as e:
    print("Validation Error:", e, e.field)

except ResponseException as e:
    print("Response Error:", e, e.response.status_code)