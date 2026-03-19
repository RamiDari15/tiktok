from tikapi import TikAPI, ValidationException, ResponseException
from curl_cffi import requests
import json
import re
import time
import datetime
from curl_cffi import requests  



TIKAPI_KEY = "Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av"
ACCOUNT_KEY = "a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS"
TIKTOK_COOKIE = "sessionid=b707553e5b1a67c5ed797fb74cdf1aa4"
MAX_USERS = 500
ALLOWED_REGIONS = {"US", "CA"}

api = TikAPI(TIKAPI_KEY)
User = api.user(accountKey=ACCOUNT_KEY)

# ==============================
# HTML PROFILE FALLBACK
# ==============================

def extract_user_data(html):
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>',
        html,
        re.DOTALL,
    )

    if not match:
        return None

    json_data = json.loads(match.group(1))
    user_detail = json_data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail")

    if not user_detail:
        return None

    user_info = user_detail.get("userInfo", {}).get("user")
    stats = user_detail.get("userInfo", {}).get("stats")

    if not user_info:
        return None

    return {
        "username": user_info.get("uniqueId"),
        "nickname": user_info.get("nickname"),
        "region": user_info.get("region"),
        "followers": stats.get("followerCount") if stats else 0,
        "userId": user_info.get("id"),
    }


def fetch_html_profile(username):
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": TIKTOK_COOKIE,
    }

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return extract_user_data(response.text)

    return None


# ==============================
# TIKAPI FETCH
# ==============================

def fetch_user_from_api(username):
    try:
        response = User.info(unique_id=username)
        data = response.json()

        user = data.get("userInfo", {}).get("user", {})
        stats = data.get("userInfo", {}).get("stats", {})

        return {
            "username": user.get("uniqueId"),
            "nickname": user.get("nickname"),
            "region": user.get("region"),
            "followers": stats.get("followerCount", 0),
            "userId": user.get("id"),
        }

    except Exception:
        return None


# ==============================
# MAIN LOGIC
# ==============================

def collect_users(usernames):
    collected = []

    for username in usernames:
        if len(collected) >= MAX_USERS:
            break

        print(f"Checking @{username}")

        data = fetch_user_from_api(username)

        if not data:
            data = fetch_html_profile(username)

        if not data:
            continue

        region = (data.get("region") or "").upper()

        if region in ALLOWED_REGIONS:
            print(f"✅ Added @{username} ({region})")
            collected.append(data)

        time.sleep(1)  # basic rate safety

    return collected


# ==============================
# RUN
# ==============================

if __name__ == "__main__":

    usernames_input = input("Enter usernames separated by commas: ")
    usernames = [u.strip().lstrip("@") for u in usernames_input.split(",")]

    results = collect_users(usernames)

    with open("us_canada_users.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved {len(results)} users to us_canada_users.json")
