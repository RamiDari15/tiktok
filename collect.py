import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import re
import datetime
import time
import random
from curl_cffi import requests

# ---------------------------
# FIREBASE SETUP
# ---------------------------

cred = credentials.Certificate("service.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------------------
# CONFIG
# ---------------------------

TIKTOK_COOKIE = "sessionid=b707553e5b1a67c5ed797fb74cdf1aa4"
CSV_FILE = "scrapers/users4.csv"

REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# safer delays
MIN_DELAY = 4
MAX_DELAY = 8

FAIL_DELAY = 10


# ---------------------------
# FIRESTORE SAFE DOC ID
# ---------------------------

def safe_doc_id(username):
    if username.startswith("__") and username.endswith("__"):
        return f"user_{username}"
    return username


# ---------------------------
# RANDOM HUMAN DELAY
# ---------------------------

def human_delay():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Sleeping {round(delay,2)}s")
    time.sleep(delay)


# ---------------------------
# REQUEST WITH RETRY
# ---------------------------

def fetch_with_retry(url, headers):

    for attempt in range(MAX_RETRIES):

        try:

            response = requests.get(
                url,
                headers=headers,
                impersonate="chrome110",
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                return response

        except Exception:
            pass

        print("Retrying request...")
        time.sleep(3)

    return None


# ---------------------------
# EXTRACT USER DATA
# ---------------------------

def extract_user_data(html):

    if "captcha" in html.lower():
        return None

    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>',
        html,
        re.DOTALL
    )

    if not match:
        match = re.search(
            r'<script id="SIGI_STATE" type="application/json">(.+?)</script>',
            html,
            re.DOTALL
        )

    if not match:
        return None

    try:
        data = json.loads(match.group(1))
    except:
        return None

    user_info = None
    stats = None

    if "__DEFAULT_SCOPE__" in data:

        user_detail = data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail")

        if user_detail and "userInfo" in user_detail:

            user_info = user_detail["userInfo"].get("user")
            stats = user_detail["userInfo"].get("stats")

    elif "UserModule" in data:

        users_dict = data.get("UserModule", {}).get("users", {})
        stats_dict = data.get("UserModule", {}).get("stats", {})

        if users_dict:

            user_id = list(users_dict.keys())[0]

            user_info = users_dict.get(user_id)
            stats = stats_dict.get(user_id)

    if not user_info or not stats:
        return None

    return {
        "username": user_info.get("uniqueId"),
        "nickname": user_info.get("nickname"),
        "region": user_info.get("region"),
        "language": user_info.get("language"),
        "bio": user_info.get("signature"),
        "avatar": user_info.get("avatarLarger"),
        "followers": stats.get("followerCount"),
        "following": stats.get("followingCount"),
        "hearts": stats.get("heartCount"),
        "videos": stats.get("videoCount"),
        "scraped_at": datetime.datetime.now(datetime.UTC)
    }


# ---------------------------
# FETCH PROFILE
# ---------------------------

def fetch_tiktok_profile(username):

    url = f"https://www.tiktok.com/@{username}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.tiktok.com/",
        "Cookie": TIKTOK_COOKIE
    }

    response = fetch_with_retry(url, headers)

    if not response:
        return None

    return extract_user_data(response.text)


# ---------------------------
# LOAD USERNAMES
# ---------------------------

df = pd.read_csv(CSV_FILE)
usernames = df["username"].dropna().tolist()

print(f"Found {len(usernames)} usernames in CSV")


# ---------------------------
# SCRAPE LOOP
# ---------------------------

success = 0
failed = 0
fail_streak = 0

for username in usernames:

    print(f"\nScraping @{username}")

    profile = fetch_tiktok_profile(username)

    if not profile:

        print("Failed to parse profile")

        failed += 1
        fail_streak += 1

        print(f"Sleeping {FAIL_DELAY}s after failure")
        time.sleep(FAIL_DELAY)

        # slow down if TikTok starts blocking
        if fail_streak >= 5:
            print("Multiple failures detected, cooling down 60 seconds...")
            time.sleep(60)
            fail_streak = 0

        continue

    fail_streak = 0

    try:

        doc_id = safe_doc_id(profile["username"])

        db.collection("users").document(doc_id).set(profile)

        print("Stored in Firebase")

        success += 1

    except Exception as e:

        print(f"Firestore error: {e}")
        failed += 1

    human_delay()


# ---------------------------
# SUMMARY
# ---------------------------

print("")
print("Scraping complete")
print("Success:", success)
print("Failed:", failed)