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
import os
from flask import send_file

# ---------------- CONFIG ----------------


TIKTOK_COOKIE = "sessionid=b707553e5b1a67c5ed797fb74cdf1aa4"
TIKAPI_KEY = "LxcVXRgh5Asr59aQvc2GNHRbz4gTUh1IFLHZHuBjIqRMO8RK"
ACCOUNT_KEY = "yrpU9zKnAbOJ3jrYvH8WFQE5pBhDHHYJz8afEenzNp5WGJie"

cred = credentials.Certificate("service.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

CSV_FILE = "server/scrapers/users4.csv"
def load_usernames_from_csv(file_path):
    try:
        usernames = []

        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                username = row.get("username")

                if username:
                    usernames.append(str(username).strip())

        # remove duplicates
        usernames = list(set(usernames))

        return usernames

    except Exception as e:
        print("Error loading usernames from CSV:", e)
        return []
    

INITIAL_NAMES  = load_usernames_from_csv("server/scrapers/users4.csv")




TARGET_COUNT = 100

api = TikAPI(TIKAPI_KEY)
User = api.user(accountKey=ACCOUNT_KEY)




POPULAR_QUERIES = [

# ========================
# HARD UK SIGNAL
# ========================
"uk","uktiktok","uklive","ukcreator",
"britishtiktok","britishlive",
"madeinuk","ukfyp","fypuk",
"englandlive","scotlandlive",
"waleslive","northernirelandlive",

# ========================
# UK NATIONS
# ========================
"england","scotland","wales","northernireland",

# ========================
# ENGLISH REGIONS
# ========================
"greaterlondon","westmidlands","eastmidlands",
"northwestengland","northeastengland",
"southwestengland","southeastengland",
"eastofengland","yorkshire","themidlands",

# ========================
# UK COUNTIES (EXPANDED)
# ========================
"kent","essex","surrey","sussex",
"lancashire","derbyshire","nottinghamshire",
"staffordshire","warwickshire","devon",
"cornwall","cumbria","hampshire",
"leicestershire","lincolnshire",
"buckinghamshire","bedfordshire",
"hertfordshire","gloucestershire",
"oxfordshire","northamptonshire",
"worcestershire","cheshire","norfolk",
"suffolk","somerset","wiltshire",

# ========================
# MAJOR UK CITIES
# ========================
"london","londonuk","londonlive",
"manchester","manc","manchesterlive",
"birmingham","brum",
"glasgow","glasgowlive",
"edinburgh","edinburghlive",
"liverpool","liverpoollive",
"leeds","newcastle","cardiff",
"belfast","brighton","sheffield",
"nottingham","leicester","coventry",
"derby","southampton","oxford",
"cambridge","hull","portsmouth",
"plymouth","reading","luton",
"miltonkeynes","bradford","stokeontrent",
"sunderland","wolverhampton","aberdeen",
"dundee","swansea","newport",

# ========================
# FOOTBALL (HIGHEST TRAFFIC)
# ========================
"premierleague","epl","facup",
"carabaocup","championship",
"leagueone","leaguetwo",
"manutd","mancity","arsenal",
"chelsea","liverpoolfc","tottenham",
"newcastlefc","westham","astonvilla",
"everton","wolves","leedsunited",
"burnley","sheffieldunited",
"celticfc","rangersfc",
"englandfc","three_lions",
"matchday","footballbanter",

# ========================
# UK SPORTS (BEYOND FOOTBALL)
# ========================
"wimbledon","sixnations",
"englandrugby","scotlandrugby",
"boxinguk","tysonfury",
"anthonyjoshua","dartsuk",
"premiershiprugby","countycricket",
"ashes","cheltenhamfestival",
"f1uk","silverstone",

# ========================
# UK MUSIC / DRILL / GRIME
# ========================
"ukrap","ukdrill","grime",
"londonrap","manchesterrap",
"ukfreestyle","ukartist",
"centralcee","stormzy",
"daveuk","skepta",
"headieone","arrdee",
"wirelessfestival","glastonbury",
"readingfestival","britawards",
"bbc1xtra",

# ========================
# UK UNIVERSITIES (STRONG LIVE)
# ========================
"oxforduni","cambridgeuni",
"ucl","kingscollege",
"manchesteruni","leedsuni",
"birminghamuni","edinburghuni",
"glasgowuni","bristoluni",
"nottinghamuni","sheffielduni",
"durhamuni","warwickuni",
"exeteruni","loughboroughuni",
"cardiffuni","newcastleuni",

# ========================
# UK LIFESTYLE
# ========================
"ukgym","britishgym","ukfitness",
"gymtokuk","ukfashion",
"londonfashion","ukstreetwear",
"ukcars","carmeetuk",
"londoncars","modifieduk",
"bmwuk","audiuk",
"fordfocusst","fiestast",
"fishandchips","nandos",
"greggs","pubculture",
"ukfood","uknightlife",

# ========================
# UK EVENTS / SEASONAL
# ========================
"halloweenuk","bonfirenight",
"guyfawkes","christmasuk",
"boxingday","summeruk",
"bankholiday","ukfestival",
"creamfields","downloadfestival",
"leedsfestival","wirelessfest",

# ========================
# UK GAMING (LIVE GOLDMINE)
# ========================
"gaminguk","ukstreamer",
"fortniteuk","warzoneuk",
"valorantuk","fifauk",
"gtaonlineuk","coduk",
"playstationuk","xboxuk",
"fc24uk","ukgamers"
]

api = TikAPI(TIKAPI_KEY)
User = api.user(accountKey=ACCOUNT_KEY)

# ---------------- HELPERS ----------------
def extract_username_from_input(input_str):
    if not input_str or not isinstance(input_str, str):
        return ""
    clean_input = input_str.strip().lstrip('@')
    url_match = re.search(r"(?:https?://)?(?:www\.)?tiktok\.com/@([a-zA-Z0-9_.]+)(?:[/?]|$)", clean_input)
    return url_match.group(1) if url_match else clean_input

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
usernames = set()
recent_queries = []

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
def random_query():
    return ''.join(random.choices(string.ascii_lowercase, k=2))

def get_query():
    # 70% random, 30% popular
    if random.random() > 0.95:
        return random_query()
    else:
        return random.choice(POPULAR_QUERIES)

def append_to_csv(username):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # write header only if file doesn't exist
        if not file_exists:
            writer.writerow(["username"])

        writer.writerow([
            username
        ])

print(f"\nStarting collection. Target: {TARGET_COUNT} unique live users\n")
cursor = 0
has_more = True
rate_limited = False
index = 0
while len(usernames) < TARGET_COUNT:
    try:
            query = POPULAR_QUERIES[index]
            index =  (index + 1) % len(POPULAR_QUERIES)

            print(f"\nSearching with query: {query}")

            try:
                response = User.live.search(
                query=query,
                count=200,
            )
                

                data = response.json()
                lives = data.get("data", [])
                has_more = bool(lives)


                if not lives:
                    time.sleep(1)
                    continue

                for item in lives:
                    try:
                        username = item["live_info"]["owner"]["display_id"]
                        username = extract_username_from_input(username)
                        try:
                            data = fetch_tiktok_profile(username)
                    
                        except Exception as e:
                            print(f"\n[-] Error: {e}\n")

                        if username not in usernames and username not in INITIAL_NAMES  and ( data.get('region').upper() == "GB" or data.get('region').upper() == "GB"   ):
                            usernames.add(username)
                            profile = fetch_tiktok_profile(username)
                            doc_id = username  # matches your DB structure

                            append_to_csv(username)

                            # 🔥 MERGE FULL PROFILE + EXTRA FIELDS
                            db.collection("users").document(doc_id).set({
                                **profile,  # 👈 ALL USER DATA (followers, bio, avatar, etc.)
                                "initial_name": True,
                                "source": "live_scraper",
                                "added_at": datetime.datetime.now(datetime.UTC)
                            }, merge=True)
                            print(f"Collected: {len(usernames)} → @{username}")

                        if len(usernames) >= TARGET_COUNT:
                            break

                    except KeyError:
                        continue

                time.sleep(1)

            except Exception as e:
                print("Search error:", e)

                if "Too many attempts." in str(e):
                    print("Rate limited. Stopping loop.")
                    break   # exits the while loop cleanly
                time.sleep(.1)

    except KeyboardInterrupt:
        print("\nStopped manually.")
    

    finally:
        print("\nSaving usernames before exit...")
        filename = "users1.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username"])
            for username in usernames:
                writer.writerow([username])

    

        print(f"\n✅ Saved {len(usernames)} usernames to {filename}")

    # ---------------- SAVE ----------------

filename = "users.csv"

with open(filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["username"])

    for username in usernames:
        writer.writerow([username])

print(f"\n✅ Saved {len(usernames)} usernames to {filename}")
