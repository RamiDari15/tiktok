from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import threading
import os
import csv
import tempfile
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
CORS(app)


firebase_key = json.loads(os.environ["FIREBASE_KEY"])

cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------------------
# SCRIPT PATHS
# ---------------------------
SCRIPTS = {
    "arab": "server/scrapers/arab_scraper.py",
    "us": "server/scrapers/us_ca_scraper.py",
    "global": "server/scrapers/global_scraper.py"
}



# ---------------------------
# RUN SCRAPER (WITH LOGS)
# ---------------------------
def run_scraper(script_path):

    print(f"🚀 Starting scraper: {script_path}")

    try:
        process = subprocess.Popen(
            ["python3", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(f"[SCRAPER] {line.strip()}")

        process.wait()

        print(f"✅ Finished scraper: {script_path}")

    except Exception as e:
        print(f"❌ ERROR running scraper: {e}")


# ---------------------------
# START SCRAPER
# ---------------------------
@app.route("/collect", methods=["POST"])
def collect():

    data = request.json
    script = data.get("script")

    if script not in SCRIPTS:
        return jsonify({"error": "invalid script"}), 400

    script_path = SCRIPTS[script]

    print(f"🔥 Collect endpoint triggered | Script: {script}")

    threading.Thread(
        target=run_scraper,
        args=(script_path,),
        daemon=True
    ).start()

    return jsonify({
        "status": "started",
        "script": script
    })


@app.route("/download", methods=["GET"])
def download():

    try:
        print("📥 Fetching new_batch from Firestore...")

        docs = db.collection("new_batch").stream()

        data = []
        for doc in docs:
            d = doc.to_dict()
            data.append({
                "username": d.get("username", doc.id),
                "added_at": str(d.get("added_at", ""))
            })

        if not data:
            return jsonify({"error": "no data in new_batch"}), 404

        # 🔥 Create temp CSV
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        csv_path = temp_file.name

        with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["username", "added_at"])
            writer.writeheader()
            writer.writerows(data)

        print(f"✅ CSV generated: {csv_path}")

        return send_file(
            csv_path,
            as_attachment=True,
            download_name="new_batch.csv"
        )

    except Exception as e:
        print("❌ Download error:", e)
        return jsonify({"error": str(e)}), 500


# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.route("/")
def home():
    return "✅ Scraper API Running"


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)