import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (only if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Count documents
docs = db.collection("gifts").stream()

count = 0
for _ in docs:
    count += 1

print(f"Total documents in 'gifts' collection: {count}")
