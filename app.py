from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import requests, os, sqlite3, json

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

FPL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DB_PATH = os.environ.get("DB_PATH", "mgp.db")

# ── DATABASE SETUP ─────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS squads (
                team_id INTEGER NOT NULL,
                position TEXT NOT NULL,  -- 'gk1','gk2','def1'...'def7','mid1'...'mid7','fwd1'...'fwd4'
                player_id INTEGER,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (team_id, position)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gk_clubs (
                team_id INTEGER NOT NULL,
                slot INTEGER NOT NULL,   -- 1 or 2
                club_name TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (team_id, slot)
            )
        """)
        conn.commit()

init_db()

# ── FPL PROXY ──────────────────────────────────────────────────────────────────
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

# ── SQUAD API ──────────────────────────────────────────────────────────────────
@app.route("/api/squads", methods=["GET"])
def get_squads():
    """Return all saved squad overrides as {team_id: {position: player_id}}"""
    with get_db() as conn:
        rows = conn.execute("SELECT team_id, position, player_id FROM squads").fetchall()
        gk_rows = conn.execute("SELECT team_id, slot, club_name FROM gk_clubs").fetchall()

    squads = {}
    for row in rows:
        tid = str(row["team_id"])
        if tid not in squads:
            squads[tid] = {}
        squads[tid][row["position"]] = row["player_id"]

    gks = {}
    for row in gk_rows:
        tid = str(row["team_id"])
        if tid not in gks:
            gks[tid] = {}
        gks[tid][str(row["slot"])] = row["club_name"]

    return jsonify({"squads": squads, "gk_clubs": gks})

@app.route("/api/squads/<int:team_id>", methods=["POST"])
def update_squad(team_id):
    """Update a single player slot for a team"""
    data = request.get_json()
    position = data.get("position")   # e.g. "def3"
    player_id = data.get("player_id") # FPL player ID (int)

    if not position or player_id is None:
        return jsonify({"error": "Missing position or player_id"}), 400

    with get_db() as conn:
        conn.execute("""
            INSERT INTO squads (team_id, position, player_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(team_id, position) DO UPDATE SET
                player_id=excluded.player_id,
                updated_at=excluded.updated_at
        """, (team_id, position, player_id))
        conn.commit()

    return jsonify({"ok": True, "team_id": team_id, "position": position, "player_id": player_id})

@app.route("/api/squads/<int:team_id>/gk", methods=["POST"])
def update_gk_club(team_id):
    """Update a GK club slot (slot 1 or 2)"""
    data = request.get_json()
    slot = data.get("slot")         # 1 or 2
    club_name = data.get("club_name")

    if not slot or not club_name:
        return jsonify({"error": "Missing slot or club_name"}), 400

    with get_db() as conn:
        conn.execute("""
            INSERT INTO gk_clubs (team_id, slot, club_name, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(team_id, slot) DO UPDATE SET
                club_name=excluded.club_name,
                updated_at=excluded.updated_at
        """, (team_id, slot, club_name))
        conn.commit()

    return jsonify({"ok": True, "team_id": team_id, "slot": slot, "club_name": club_name})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
