from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import requests, os, sqlite3, json
from datetime import datetime, timezone

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

FPL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DB_PATH = os.environ.get("DB_PATH", "mgp.db")

# ── DATABASE ───────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Current squad overrides (only affects future/unlocked GWs)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS squads (
                team_id   INTEGER NOT NULL,
                position  TEXT NOT NULL,
                player_id INTEGER,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (team_id, position)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gk_clubs (
                team_id  INTEGER NOT NULL,
                slot     INTEGER NOT NULL,
                club_name TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (team_id, slot)
            )
        """)
        # Locked GW snapshots — squad + scores frozen at deadline
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gw_snapshots (
                gw        INTEGER NOT NULL,
                team_id   INTEGER NOT NULL,
                squad_json TEXT NOT NULL,   -- full squad at lock time
                best_xi_score INTEGER NOT NULL,
                locked_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (gw, team_id)
            )
        """)
        # Admin score overrides for locked GWs
        conn.execute("""
            CREATE TABLE IF NOT EXISTS score_overrides (
                gw      INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                score   INTEGER NOT NULL,
                note    TEXT,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (gw, team_id)
            )
        """)
        # Track which GWs have been snapshotted
        conn.execute("""
            CREATE TABLE IF NOT EXISTS locked_gws (
                gw INTEGER PRIMARY KEY,
                locked_at TEXT DEFAULT (datetime('now'))
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
    with get_db() as conn:
        rows    = conn.execute("SELECT team_id, position, player_id FROM squads").fetchall()
        gk_rows = conn.execute("SELECT team_id, slot, club_name FROM gk_clubs").fetchall()
        locked  = conn.execute("SELECT gw FROM locked_gws").fetchall()
        snaps   = conn.execute("SELECT gw, team_id, squad_json, best_xi_score FROM gw_snapshots").fetchall()
        overrides = conn.execute("SELECT gw, team_id, score FROM score_overrides").fetchall()

    squads = {}
    for row in rows:
        tid = str(row["team_id"])
        squads.setdefault(tid, {})[row["position"]] = row["player_id"]

    gks = {}
    for row in gk_rows:
        tid = str(row["team_id"])
        gks.setdefault(tid, {})[str(row["slot"])] = row["club_name"]

    locked_gws = [r["gw"] for r in locked]

    snapshots = {}
    for row in snaps:
        gw = str(row["gw"])
        snapshots.setdefault(gw, {})[str(row["team_id"])] = {
            "squad": json.loads(row["squad_json"]),
            "score": row["best_xi_score"]
        }

    ovr = {}
    for row in overrides:
        ovr.setdefault(str(row["gw"]), {})[str(row["team_id"])] = row["score"]

    return jsonify({
        "squads": squads,
        "gk_clubs": gks,
        "locked_gws": locked_gws,
        "snapshots": snapshots,
        "overrides": ovr,
    })

@app.route("/api/squads/<int:team_id>", methods=["POST"])
def update_squad(team_id):
    data = request.get_json()
    position  = data.get("position")
    player_id = data.get("player_id")
    if not position or player_id is None:
        return jsonify({"error": "Missing fields"}), 400
    with get_db() as conn:
        conn.execute("""
            INSERT INTO squads (team_id, position, player_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(team_id, position) DO UPDATE SET
                player_id=excluded.player_id, updated_at=excluded.updated_at
        """, (team_id, position, player_id))
        conn.commit()
    return jsonify({"ok": True})

@app.route("/api/squads/<int:team_id>/gk", methods=["POST"])
def update_gk_club(team_id):
    data = request.get_json()
    slot      = data.get("slot")
    club_name = data.get("club_name")
    if not slot or not club_name:
        return jsonify({"error": "Missing fields"}), 400
    with get_db() as conn:
        conn.execute("""
            INSERT INTO gk_clubs (team_id, slot, club_name, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(team_id, slot) DO UPDATE SET
                club_name=excluded.club_name, updated_at=excluded.updated_at
        """, (team_id, slot, club_name))
        conn.commit()
    return jsonify({"ok": True})

# ── SNAPSHOT / LOCK API ────────────────────────────────────────────────────────
@app.route("/api/snapshot", methods=["POST"])
def save_snapshot():
    """
    Called by the frontend when it detects a GW has become locked
    (next GW deadline has passed). Saves squad + score for each team.
    Body: { gw, teams: [{team_id, squad_json, best_xi_score}] }
    """
    data = request.get_json()
    gw = data.get("gw")
    teams = data.get("teams", [])

    if not gw or not teams:
        return jsonify({"error": "Missing gw or teams"}), 400

    with get_db() as conn:
        # Check if already locked
        existing = conn.execute("SELECT gw FROM locked_gws WHERE gw=?", (gw,)).fetchone()
        if existing:
            return jsonify({"ok": True, "already_locked": True})

        for t in teams:
            conn.execute("""
                INSERT OR REPLACE INTO gw_snapshots (gw, team_id, squad_json, best_xi_score)
                VALUES (?, ?, ?, ?)
            """, (gw, t["team_id"], json.dumps(t["squad"]), t["best_xi_score"]))

        conn.execute("INSERT OR IGNORE INTO locked_gws (gw) VALUES (?)", (gw,))
        conn.commit()

    return jsonify({"ok": True, "gw": gw, "locked": True})

@app.route("/api/override", methods=["POST"])
def save_override():
    """Admin score override for a locked GW"""
    data = request.get_json()
    gw, team_id, score = data.get("gw"), data.get("team_id"), data.get("score")
    note = data.get("note", "")
    if gw is None or team_id is None or score is None:
        return jsonify({"error": "Missing fields"}), 400
    with get_db() as conn:
        conn.execute("""
            INSERT INTO score_overrides (gw, team_id, score, note, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(gw, team_id) DO UPDATE SET
                score=excluded.score, note=excluded.note, updated_at=excluded.updated_at
        """, (gw, team_id, score, note))
        conn.commit()
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
