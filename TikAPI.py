import os
import requests
import time
from datetime import datetime

# ==========================
# CONFIG
# ==========================

API_KEY = "Z2Ac2bxjAlawM0mp9B1ScgQkF1meGvE2AHUhr1P7WzKhn3av"

HEADERS = {
   "X-ACCOUNT-KEY": "a1s74klyIWUxc6gUQ0CLrKgEPEbP22kX3aDiLkZuZCXMhEWS",
   "X-API-KEY": API_KEY
}

USERS = [
    "jiinaa777",
    "zena_hassan7",
    "__fxria"
]

REQUEST_DELAY = 1  # seconds between requests

BASE_URL = "https://api.tikapi.io"

# ==========================
# TIKAPI FUNCTIONS
# ==========================

def get_user_info(username):
    url = f"{BASE_URL}/user/info"
    r = requests.get(url, headers=HEADERS, params={"username": username}, timeout=15)

    if r.status_code != 200:
        print(f"❌ User info error {r.status_code} for {username}: {r.text}")
        return None

    data = r.json()


    return data


def get_user_lives(username):
    url = f"{BASE_URL}/user/lives"
    r = requests.get(url, headers=HEADERS, params={"username": username}, timeout=15)

    if r.status_code != 200:
        print(f"❌ Lives error {r.status_code} for {username}: {r.text}")
        return None

    data = r.json()
    if "lives" not in data:
        return []

    return data["lives"]

# ==========================
# DIAMOND ESTIMATION
# ==========================

def get_creator_tier(followers):
    if followers < 50_000:
        return "small"
    elif followers < 300_000:
        return "mid"
    return "large"


def estimate_diamonds(live_views, duration_minutes, engagement_rate, tier):
    base = live_views * engagement_rate * 0.03

    if duration_minutes >= 120:
        base *= 1.25
    elif duration_minutes >= 60:
        base *= 1.10

    tier_multiplier = {
        "small": 0.8,
        "mid": 1.0,
        "large": 1.3
    }

    return int(base * tier_multiplier.get(tier, 1.0))

# ==========================
# MAIN PIPELINE
# ==========================

def main():
    results = []

    for username in USERS:
        print(f"\n▶ Processing {username}")

        user_info = get_user_info(username)
        if not user_info:
            continue

        stats = user_info["user"].get("stats", {})
        followers = stats.get("followerCount", 0)
        tier = get_creator_tier(followers)

        lives = get_user_lives(username)

        if not lives:
            print("ℹ️  No ended LIVE sessions found")
            continue

        for live in lives:
            views = live.get("viewCount", 0)
            likes = live.get("likeCount", 0)
            duration_sec = live.get("duration", 0)

            duration_min = max(duration_sec / 60, 1)
            engagement = likes / views if views else 0

            diamonds = estimate_diamonds(
                live_views=views,
                duration_minutes=duration_min,
                engagement_rate=engagement,
                tier=tier
            )

            record = {
                "username": username,
                "date": datetime.fromtimestamp(live.get("createTime", 0)).isoformat(),
                "followers": followers,
                "tier": tier,
                "live_views": views,
                "live_likes": likes,
                "duration_minutes": round(duration_min, 1),
                "engagement_rate": round(engagement, 4),
                "estimated_diamonds": diamonds,
                "estimated_usd": round(diamonds * 0.005, 2)
            }

            print(record)
            results.append(record)

        time.sleep(REQUEST_DELAY)

    return results


if __name__ == "__main__":
    main()
