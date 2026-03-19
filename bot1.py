from tikapi import TikAPI
import json

# =========================
# CONFIG
# =========================

API_KEY = "LxcVXRgh5Asr59aQvc2GNHRbz4gTUh1IFLHZHuBjIqRMO8RK"
ACCOUNT_KEY = "yrpU9zKnAbOJ3jrYvH8WFQE5pBhDHHYJz8afEenzNp5WGJie"

api = TikAPI(API_KEY)
User = api.user(accountKey=ACCOUNT_KEY)


# =========================
# GET ALL CONVERSATIONS
# =========================

def get_all_conversations():

    conversations = []
    cursor = None

    while True:

        if cursor:
            response = User.conversations(next_cursor=cursor)
        else:
            response = User.conversations()

        data = response.json()

        conversations.extend(data.get("conversations", []))

        cursor = data.get("nextCursor")

        if not cursor:
            break

    print("Total conversations:", len(conversations))

    return conversations


# =========================
# GET ALL MESSAGES
# =========================

def get_all_messages(conversation_id):

    messages = []
    cursor = None

    short_id = conversation_id.split(":")[-1]

    while True:

        if cursor:
            response = User.messages(
                conversation_id=conversation_id,
                conversation_short_id=short_id,
                next_cursor=cursor
            )
        else:
            response = User.messages(
                conversation_id=conversation_id,
                conversation_short_id=short_id
            )

        data = response.json()

        msgs = data.get("messages", [])
        messages.extend(msgs)

        cursor = data.get("nextCursor")

        if not cursor:
            break

    return messages


# =========================
# BUILD DATABASE
# =========================

def build_database(conversations):

    database = []

    for convo in conversations:

        convo_id = convo.get("id")

        print("Processing:", convo_id)

        msgs = get_all_messages(convo_id)

        last_message = None
        last_sender = None

        if msgs:
            last_message = msgs[0].get("text")
            last_sender = msgs[0].get("senderUid")

        database.append({
            "conversation_id": convo_id,
            "message_count": len(msgs),
            "last_message": last_message,
            "last_sender": last_sender,
            "messages": msgs
        })

    return database


# =========================
# SAVE FILE
# =========================

def save_database(data):

    with open("tiktok_inbox_database.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Saved inbox database to tiktok_inbox_database.json")


# =========================
# MAIN
# =========================

def main():

    conversations = get_all_conversations()

    database = build_database(conversations)

    save_database(database)


if __name__ == "__main__":
    main()