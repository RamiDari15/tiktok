
from tikapi import TikAPI
import random
import string
import csv
import time
import json
import re
import datetime
from curl_cffi import requests  
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- FIREBASE ----------------

cred = credentials.Certificate("service.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
# ---------------- CONFIG ----------------


TIKTOK_COOKIE = "sessionid=b707553e5b1a67c5ed797fb74cdf1aa4"

def fetch_tiktok_profile(username):
    tiktok_url = f"https://www.tiktok.com/@{username}"
    base_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.tiktok.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
    }

    try:
        response = fetch_with_retry(tiktok_url, base_headers, 1, use_cookie=True)
        return extract_user_data(response.text)
    except Exception as e:
        return None

def fetch_with_retry(url, base_headers, max_retries=3, use_cookie=False):
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(0.2 * attempt)

            current_headers = base_headers.copy()
            current_headers["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            current_headers["Accept-Language"] = "en-US,en;q=0.9"

            if use_cookie and TIKTOK_COOKIE:
                current_headers["Cookie"] = TIKTOK_COOKIE

            response = requests.get(url, headers=current_headers, impersonate="chrome110", timeout=10)
            
            if response.status_code == 404:
                raise requests.exceptions.HTTPError("404 Not Found", response=response)
                
            response.raise_for_status()
            return response

        except Exception as e:
            if attempt == max_retries - 1:
                raise e

    raise Exception("Failed to fetch from TikTok after multiple attempts.")


def extract_user_data(html):

    match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.+?)</script>', html, re.DOTALL)
    
    if not match:
        match = re.search(r'<script id="SIGI_STATE" type="application/json">(.+?)</script>', html, re.DOTALL)

    if not match or not match.group(1):
        raise ValueError("Data script not found (Possible Captcha).")

    json_data = json.loads(match.group(1))
    
    user_info = None
    stats = None

    if "__DEFAULT_SCOPE__" in json_data:
        user_detail = json_data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail")
        if user_detail:
            user_info = user_detail.get("userInfo", {}).get("user")
            stats = user_detail.get("userInfo", {}).get("stats") or user_detail.get("userInfo", {}).get("statsV2")

    elif "UserModule" in json_data:
        users_dict = json_data["UserModule"]["users"]
        stats_dict = json_data["UserModule"]["stats"]
        if users_dict:
            user_id = list(users_dict.keys())[0]
            user_info = users_dict[user_id]
            stats = stats_dict.get(user_id)

    if not user_info:
        raise ValueError("User info missing.")

    # Safe 
    def safe_parse_int(val):
        try:
            return int(val) if val is not None else 0
        except:
            return 0
            
    final_stats = {
        "followers": f"{safe_parse_int(stats.get('followerCount')):,}",
        "following": f"{safe_parse_int(stats.get('followingCount')):,}",
        "hearts": f"{safe_parse_int(stats.get('heartCount')):,}",
        "videos": f"{safe_parse_int(stats.get('videoCount')):,}",
        "friends": f"{safe_parse_int(stats.get('friendCount')):,}"
    }
    
    region = user_info.get("region")
    if not region: 
        region = user_info.get("location") 
    if not region:
        region = "N/A" 

    bio_link = user_info.get("bioLink", {}).get("link", "") if isinstance(user_info.get("bioLink"), dict) else ""
    
    create_time = "N/A"
    if user_info.get("createTime"):
        create_time = datetime.datetime.fromtimestamp(user_info["createTime"]).strftime('%Y-%m-%d %H:%M:%S')

    return {
        "nickname": user_info.get("nickname") or user_info.get("uniqueId"),
        "username": user_info.get("uniqueId"),
        "region": region,
        "language": user_info.get("language", "N/A"),
        "about": user_info.get("signature", "User has no about"),
        "userId": user_info.get("id"),
        "secUid": user_info.get("secUid", "N/A"),
        "bioLink": bio_link,
        "accountCreated": create_time,
        "nicknameModified": "N/A", 
        "uniqueIdModifyTime": "N/A", 
        "avatar": user_info.get("avatarLarger", ""),
        "stats": final_stats
    }




# Read CSV
df = pd.read_csv("scrapers/ME_users.csv")

# Convert column to array
usernames = df["username"].dropna().astype(str).str.strip().tolist()

for username in usernames:
    print(username)
    try:
        profile = fetch_tiktok_profile(username)

        doc_id = username  # matches your DB structure

        db.collection("users").document(doc_id).set({
            **profile,  # all fetched TikTok data
            "initial_name": True,
            "source": "live_scraper",
            "added_at": datetime.datetime.now(datetime.UTC)
        }, merge=True)

        print(f"✅ Saved: {username}")

        time.sleep(1)  # avoid rate limits

    except Exception as e:
        print(f"❌ Failed: {username} -> {e}")
