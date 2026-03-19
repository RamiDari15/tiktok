import os
import csv
import re
import smtplib
import random
from email.message import EmailMessage
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

# Creator username (normally known from TikTok)
username = "creator_username_here"

system_prompt = """
You are a real human recruiter texting TikTok LIVE creators for Uprise Agency.

How you should talk:
- Casual
- Friendly
- Very short replies
- Sound like a normal person texting

Never sound like a script.
"""

conversation = [{"role": "system", "content": system_prompt}]


# -------- RANDOM INTRO MESSAGES --------

intro_messages = [

"Hey quick question are you growing your TikTok LIVE solo or working with an agency?",

"I saw your LIVE earlier  are you building solo or with an agency right now?",

"Are you running your TikTok LIVE solo or with an agency?",

"Hey I caught a bit of your LIVE earlier. Are you building solo or with an agency?",

"Hey I came across your LIVE earlier. Are you solo or with an agency?"
]


# -------- PHONE DETECTOR --------

def extract_phone(text):
    phone_pattern = r'(\+?\d[\d\-\(\) ]{8,}\d)'
    match = re.search(phone_pattern, text)
    if match:
        return match.group()
    return None


# -------- EMAIL ALERT --------

def send_email_alert(phone, username):

    msg = EmailMessage()

    msg["Subject"] = "New Uprise Lead"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ALERT_EMAIL

    msg.set_content(f"""
New TikTok lead captured

Username: {username}
Phone: {phone}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Email notification sent.")


# -------- SAVE LEAD --------

def save_lead(username, phone):

    file_exists = os.path.isfile("uprise_leads.csv")

    with open("uprise_leads.csv", "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Username", "Phone"])

        writer.writerow([username, phone])


# -------- START BOT --------

print("\nUprise Agency DM Simulation\n")

opening_message = random.choice(intro_messages)

print(f"Bot: {opening_message}\n")

conversation.append({"role": "assistant", "content": opening_message})


while True:

    user_input = input("User: ").lower()

    # -------- PHONE DETECTION --------

    phone = extract_phone(user_input)

    if phone:

        print("\nBot: Perfect — appreciate it. One of our managers will reach out soon.\n")

        save_lead(username, phone)
        send_email_alert(phone, username)

        print("Lead saved to CSV.")

        break


    # -------- USER HAS AN AGENCY → END CONVO --------

    agency_keywords = ["agency", "signed", "with one", "i have an agency"]

    if any(word in user_input for word in agency_keywords):

        responses = [
            "Nice that's great. Sounds like you're in good hands.",
            "Gotcha that's awesome. Wishing you the best with your streams.",
            "Nice that's great to hear. Keep crushing your LIVE."
        ]

        print(f"\nBot: {random.choice(responses)}\n")

        break


    # -------- USER IS SOLO → ASK FOR PHONE --------

    solo_keywords = ["solo", "myself", "just me", "independent"]

    if any(word in user_input for word in solo_keywords):

        agency_line = random.choice([
            "Nice. I actually help run a small LIVE agency that helps creators grow their streams.",
            "Gotcha. I work with a small agency helping creators grow their LIVE audience.",
            "Nice. I help run a LIVE agency that supports creators with growth strategies."
        ])

        phone_request = random.choice([
            "If you're open to chatting more, what's the best number to reach you?",
            "If you're interested, I could connect you with one of our managers. What's the best number?",
            "If you'd like to hear more, what's the best number to reach you?"
        ])

        print(f"\nBot: {agency_line}")
        print(f"\nBot: {phone_request}\n")

        continue


    # -------- USER NOT INTERESTED --------

    if any(word in user_input for word in ["not interested", "no thanks", "nope"]):

        print("\nBot: No worries at all. Keep crushing your lives.\n")

        break


    # -------- FALLBACK AI RESPONSE --------

    conversation.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.9
    )

    reply = response.choices[0].message.content.strip()

    print(f"\nBot: {reply}\n")

    conversation.append({"role": "assistant", "content": reply})