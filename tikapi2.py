from tikapi import TikAPI, ValidationException, ResponseException

# 🔑 YOUR KEYS
API_KEY = "Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av"
ACCOUNT_KEY = "a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"


api = TikAPI(API_KEY)
User = api.user(accountKey=ACCOUNT_KEY)

try:
    print("🔎 Testing region filter: US\n")

    response = User.live.search(
        query="gaming",
        count=20,
        region="US"   # 👈 REGION FILTER
    )

    data = response.json()

    lives = data.get("data", [])

    print(f"Returned {len(lives)} live results\n")

    for item in lives:
        try:
            owner = item["live_info"]["owner"]
            username = owner.get("display_id")
            region = owner.get("region")

            print(f"Username: {username}")
            print(f"Region field: {region}")
            print("-" * 40)

        except Exception:
            continue

    # 🔍 Check if region filter was respected
    non_us = [
        item for item in lives
        if item.get("live_info", {})
              .get("owner", {})
              .get("region") not in ("US", None)
    ]

    if non_us:
        print("\n⚠️ Region filter may NOT be working.")
    else:
        print("\n✅ Region filter appears to be working (or region hidden).")

except ValidationException as e:
    print("Validation Error:", e, e.field)

except ResponseException as e:
    print("Response Error:", e, e.response.status_code)
