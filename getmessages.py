import json

def extract_users(data):

    users = {}

    for convo in data["conversations"]:
        convo_id = convo["id"]

        for msg in convo["messages"]:
            content = msg.get("content", {})

            username = content.get("desc")
            uid = content.get("uid")
            secuid = content.get("secUID")

            if username and uid:
                users[uid] = {
                    "username": username,
                    "uid": uid,
                    "secUID": secuid,
                    "conversation_id": convo_id
                }

    return list(users.values())


# Example: load JSON file
with open("messages.json") as f:
    data = json.load(f)

users = extract_users(data)

print(json.dumps(users, indent=4))