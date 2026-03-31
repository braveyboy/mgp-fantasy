from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import requests, os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

FPL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

@app.route("/api/bootstrap")
def bootstrap():
    r = requests.get(f"{FPL}/bootstrap-static/", headers=HEADERS, timeout=10)
    return jsonify(r.json())

@app.route("/api/live/<int:gw>")
def live(gw):
    r = requests.get(f"{FPL}/event/{gw}/live/", headers=HEADERS, timeout=10)
    return jsonify(r.json())

@app.route("/api/fixtures/<int:gw>")
def fixtures(gw):
    r = requests.get(f"{FPL}/fixtures/?event={gw}", headers=HEADERS, timeout=10)
    return jsonify(r.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
