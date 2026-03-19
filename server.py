from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import threading
import os

app = Flask(__name__)
CORS(app)

# ---------------------------
# SCRIPT PATHS
# ---------------------------
SCRIPTS = {
    "arab": "scrapers/arab_scraper.py",
    "us": "scrapers/us_ca_scraper.py",
    "global": "scrapers/global_scraper.py"
}

# ---------------------------
# SHARED OUTPUT FILE
# ---------------------------
CSV_FILE = "users1.csv"

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


# ---------------------------
# DOWNLOAD CSV (ALL SCRIPTS)
# ---------------------------
@app.route("/download", methods=["GET"])
def download():

    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "file not ready"}), 404

    return send_file(
        CSV_FILE,
        as_attachment=True,
        download_name="users.csv"
    )


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