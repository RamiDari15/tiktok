import csv
from collections import Counter

FILE_1 = "users15.csv"
FILE_2 = "users13.csv"
OUTPUT_FILE = "ME_users.csv"

seen = set()
combined_rows = []

def process_file(filename):
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row["username"].strip().lower()

            if username not in seen:
                seen.add(username)
                combined_rows.append(row)

process_file(FILE_1)
process_file(FILE_2)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=combined_rows[0].keys())
    writer.writeheader()
    writer.writerows(combined_rows)

print(f"Saved {len(combined_rows)} unique users.")
