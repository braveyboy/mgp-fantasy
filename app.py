from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import requests, os, json

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

FPL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ── DATABASE: PostgreSQL (persistent) or SQLite fallback ──────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")  # Set on Render PostgreSQL

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras
    def get_db():
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    DB_TYPE = "postgres"
else:
    import sqlite3
    DB_PATH = os.environ.get("DB_PATH", "mgp.db")
    def get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    DB_TYPE = "sqlite"

def init_db():
    if DB_TYPE == "postgres":
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS squads (
                        team_id INTEGER NOT NULL,
                        position TEXT NOT NULL,
                        player_id INTEGER,
                        updated_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (team_id, position)
                    )""")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS gk_clubs (
                        team_id INTEGER NOT NULL,
                        slot INTEGER NOT NULL,
                        club_name TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (team_id, slot)
                    )""")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS gw_snapshots (
                        gw INTEGER NOT NULL,
                        team_id INTEGER NOT NULL,
                        squad_json TEXT NOT NULL,
                        best_xi_score INTEGER NOT NULL,
                        locked_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (gw, team_id)
                    )""")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS score_overrides (
                        gw INTEGER NOT NULL,
                        team_id INTEGER NOT NULL,
                        score INTEGER NOT NULL,
                        note TEXT,
                        updated_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (gw, team_id)
                    )""")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS locked_gws (
                        gw INTEGER PRIMARY KEY,
                        locked_at TIMESTAMP DEFAULT NOW()
                    )""")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS draft_sessions (
                        id SERIAL PRIMARY KEY,
                        status TEXT NOT NULL DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT NOW(),
                        ended_at TIMESTAMP
                    )""")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS draft_picks (
                        id SERIAL PRIMARY KEY,
                        session_id INTEGER NOT NULL,
                        turn_number INTEGER NOT NULL,
                        team_id INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        kind TEXT,
                        position TEXT,
                        dropped_player_id INTEGER,
                        dropped_club_name TEXT,
                        added_player_id INTEGER,
                        added_club_name TEXT,
                        completed_at TIMESTAMP
                    )""")
            conn.commit()
    else:
        with get_db() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS squads (
                team_id INTEGER NOT NULL, position TEXT NOT NULL,
                player_id INTEGER, updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (team_id, position))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS gk_clubs (
                team_id INTEGER NOT NULL, slot INTEGER NOT NULL,
                club_name TEXT NOT NULL, updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (team_id, slot))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS gw_snapshots (
                gw INTEGER NOT NULL, team_id INTEGER NOT NULL,
                squad_json TEXT NOT NULL, best_xi_score INTEGER NOT NULL,
                locked_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (gw, team_id))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS score_overrides (
                gw INTEGER NOT NULL, team_id INTEGER NOT NULL, score INTEGER NOT NULL,
                note TEXT, updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (gw, team_id))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS locked_gws (
                gw INTEGER PRIMARY KEY, locked_at TEXT DEFAULT (datetime('now')))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS draft_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT DEFAULT (datetime('now')), ended_at TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS draft_picks (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
                turn_number INTEGER NOT NULL, team_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', kind TEXT, position TEXT,
                dropped_player_id INTEGER, dropped_club_name TEXT,
                added_player_id INTEGER, added_club_name TEXT, completed_at TEXT)""")
            conn.commit()

init_db()

def db_fetchall(query, params=()):
    with get_db() as conn:
        if DB_TYPE == "postgres":
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
        else:
            return conn.execute(query, params).fetchall()

def db_execute(query, params=()):
    if DB_TYPE == "postgres":
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()
    else:
        with get_db() as conn:
            conn.execute(query, params)
            conn.commit()

def db_fetchone(query, params=()):
    rows = db_fetchall(query, params)
    return rows[0] if rows else None

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

# ── SQUAD HELPERS ──────────────────────────────────────────────────────────────
def build_squads_response():
    rows      = db_fetchall("SELECT team_id, position, player_id FROM squads")
    gk_rows   = db_fetchall("SELECT team_id, slot, club_name FROM gk_clubs")
    locked    = db_fetchall("SELECT gw FROM locked_gws")
    snaps     = db_fetchall("SELECT gw, team_id, squad_json, best_xi_score FROM gw_snapshots")
    overrides = db_fetchall("SELECT gw, team_id, score FROM score_overrides")

    squads = {}
    for row in rows:
        tid = str(row["team_id"])
        squads.setdefault(tid, {})[row["position"]] = row["player_id"]

    gks = {}
    for row in gk_rows:
        tid = str(row["team_id"])
        gks.setdefault(tid, {})[str(row["slot"])] = row["club_name"]

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

    return {
        "squads": squads,
        "gk_clubs": gks,
        "locked_gws": [r["gw"] for r in locked],
        "snapshots": snapshots,
        "overrides": ovr,
    }

# ── SQUAD API ──────────────────────────────────────────────────────────────────
@app.route("/api/squads", methods=["GET"])
def get_squads():
    return jsonify(build_squads_response())

def _apply_squad_slot(team_id, position, player_id):
    if DB_TYPE == "postgres":
        db_execute("""
            INSERT INTO squads (team_id, position, player_id, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (team_id, position) DO UPDATE SET
                player_id = EXCLUDED.player_id, updated_at = NOW()
        """, (team_id, position, player_id))
    else:
        db_execute("""
            INSERT INTO squads (team_id, position, player_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(team_id, position) DO UPDATE SET
                player_id=excluded.player_id, updated_at=excluded.updated_at
        """, (team_id, position, player_id))

def _apply_gk_slot(team_id, slot, club_name):
    if DB_TYPE == "postgres":
        db_execute("""
            INSERT INTO gk_clubs (team_id, slot, club_name, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (team_id, slot) DO UPDATE SET
                club_name = EXCLUDED.club_name, updated_at = NOW()
        """, (team_id, slot, club_name))
    else:
        db_execute("""
            INSERT INTO gk_clubs (team_id, slot, club_name, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(team_id, slot) DO UPDATE SET
                club_name=excluded.club_name, updated_at=excluded.updated_at
        """, (team_id, slot, club_name))

@app.route("/api/squads/<int:team_id>", methods=["POST"])
def update_squad(team_id):
    data      = request.get_json()
    position  = data.get("position")
    player_id = data.get("player_id")
    if not position or player_id is None:
        return jsonify({"error": "Missing fields"}), 400
    _apply_squad_slot(team_id, position, player_id)
    return jsonify(build_squads_response())

@app.route("/api/squads/<int:team_id>/gk", methods=["POST"])
def update_gk_club(team_id):
    data      = request.get_json()
    slot      = data.get("slot")
    club_name = data.get("club_name")
    if not slot or not club_name:
        return jsonify({"error": "Missing fields"}), 400
    _apply_gk_slot(team_id, slot, club_name)
    return jsonify(build_squads_response())

@app.route("/api/snapshot", methods=["POST"])
def save_snapshot():
    data  = request.get_json()
    gw    = data.get("gw")
    teams = data.get("teams", [])
    if not gw or not teams:
        return jsonify({"error": "Missing gw or teams"}), 400

    existing = db_fetchone(
        "SELECT gw FROM locked_gws WHERE gw=%s" if DB_TYPE=="postgres" else "SELECT gw FROM locked_gws WHERE gw=?",
        (gw,))
    if existing:
        return jsonify({"ok": True, "already_locked": True})

    for t in teams:
        if DB_TYPE == "postgres":
            db_execute("""
                INSERT INTO gw_snapshots (gw, team_id, squad_json, best_xi_score)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (gw, team_id) DO UPDATE SET
                    squad_json=EXCLUDED.squad_json, best_xi_score=EXCLUDED.best_xi_score
            """, (gw, t["team_id"], json.dumps(t["squad"]), t["best_xi_score"]))
        else:
            db_execute("""
                INSERT OR REPLACE INTO gw_snapshots (gw, team_id, squad_json, best_xi_score)
                VALUES (?, ?, ?, ?)
            """, (gw, t["team_id"], json.dumps(t["squad"]), t["best_xi_score"]))

    if DB_TYPE == "postgres":
        db_execute("INSERT INTO locked_gws (gw) VALUES (%s) ON CONFLICT DO NOTHING", (gw,))
    else:
        db_execute("INSERT OR IGNORE INTO locked_gws (gw) VALUES (?)", (gw,))

    return jsonify({"ok": True, "gw": gw, "locked": True})

@app.route("/api/override", methods=["POST"])
def save_override():
    data    = request.get_json()
    gw      = data.get("gw")
    team_id = data.get("team_id")
    score   = data.get("score")
    note    = data.get("note", "")
    if gw is None or team_id is None or score is None:
        return jsonify({"error": "Missing fields"}), 400

    if DB_TYPE == "postgres":
        db_execute("""
            INSERT INTO score_overrides (gw, team_id, score, note, updated_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (gw, team_id) DO UPDATE SET
                score=EXCLUDED.score, note=EXCLUDED.note, updated_at=NOW()
        """, (gw, team_id, score, note))
    else:
        db_execute("""
            INSERT INTO score_overrides (gw, team_id, score, note, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(gw, team_id) DO UPDATE SET
                score=excluded.score, note=excluded.note, updated_at=excluded.updated_at
        """, (gw, team_id, score, note))

    return jsonify({"ok": True})


# ── MONTHLY DRAFT ────────────────────────────────────────────────────────────
# One shared commissioner PIN, set as a Render env var. Gates start/end/override
# only — making a pick on your own turn needs no PIN, same trust model as
# Team Admin. Only one draft can be active at a time.
DRAFT_PIN = os.environ.get("DRAFT_PIN", "mgp2026")

def _row(r):
    return dict(r) if r is not None else None

def _draft_session_payload(sess):
    picks = db_fetchall(
        "SELECT id, turn_number, team_id, status, kind, position, dropped_player_id, "
        "dropped_club_name, added_player_id, added_club_name, completed_at FROM draft_picks "
        "WHERE session_id=%s ORDER BY turn_number" if DB_TYPE == "postgres" else
        "SELECT id, turn_number, team_id, status, kind, position, dropped_player_id, "
        "dropped_club_name, added_player_id, added_club_name, completed_at FROM draft_picks "
        "WHERE session_id=? ORDER BY turn_number",
        (sess["id"],))
    return {
        "id": sess["id"],
        "status": sess["status"],
        "created_at": str(sess.get("created_at")) if sess.get("created_at") else None,
        "ended_at": str(sess.get("ended_at")) if sess.get("ended_at") else None,
        "order": [p["team_id"] for p in picks],
        "picks": [dict(p) for p in picks],
    }

def build_draft_response():
    active_row = _row(db_fetchone("SELECT id, status, created_at, ended_at FROM draft_sessions WHERE status='active' ORDER BY id DESC LIMIT 1"))
    active = _draft_session_payload(active_row) if active_row else None
    recent = None
    if not active:
        last_row = _row(db_fetchone("SELECT id, status, created_at, ended_at FROM draft_sessions WHERE status='completed' ORDER BY id DESC LIMIT 1"))
        if last_row:
            recent = _draft_session_payload(last_row)
    return {"active": active, "recent": recent}

@app.route("/api/draft", methods=["GET"])
def get_draft():
    return jsonify(build_draft_response())

@app.route("/api/draft/start", methods=["POST"])
def start_draft():
    data = request.get_json()
    if data.get("pin") != DRAFT_PIN:
        return jsonify({"error": "Incorrect PIN"}), 403
    team_ids = data.get("team_ids") or []
    if len(team_ids) < 2:
        return jsonify({"error": "Need at least 2 teams in the order"}), 400
    if db_fetchone("SELECT id FROM draft_sessions WHERE status='active'"):
        return jsonify({"error": "A draft is already active"}), 409

    db_execute("INSERT INTO draft_sessions (status) VALUES ('active')")
    sess = db_fetchone("SELECT id FROM draft_sessions ORDER BY id DESC LIMIT 1")
    session_id = sess["id"]
    for i, tid in enumerate(team_ids):
        status = "active" if i == 0 else "pending"
        if DB_TYPE == "postgres":
            db_execute("INSERT INTO draft_picks (session_id, turn_number, team_id, status) VALUES (%s,%s,%s,%s)",
                       (session_id, i + 1, tid, status))
        else:
            db_execute("INSERT INTO draft_picks (session_id, turn_number, team_id, status) VALUES (?,?,?,?)",
                       (session_id, i + 1, tid, status))
    return jsonify(build_draft_response())

@app.route("/api/draft/pick", methods=["POST"])
def draft_pick():
    data = request.get_json()
    pick_id = data.get("pick_id")
    action  = data.get("action")

    pick = _row(db_fetchone(
        "SELECT * FROM draft_picks WHERE id=%s" if DB_TYPE == "postgres" else "SELECT * FROM draft_picks WHERE id=?",
        (pick_id,)))
    if not pick:
        return jsonify({"error": "Pick not found"}), 404
    if pick["status"] != "active":
        return jsonify({"error": "This pick is not the current turn"}), 409

    if action == "pass":
        if DB_TYPE == "postgres":
            db_execute("UPDATE draft_picks SET status='passed', completed_at=NOW() WHERE id=%s", (pick_id,))
        else:
            db_execute("UPDATE draft_picks SET status='passed', completed_at=datetime('now') WHERE id=?", (pick_id,))
    elif action == "pick":
        kind = data.get("kind"); position = data.get("position")
        if not kind or not position:
            return jsonify({"error": "Missing pick details"}), 400
        args = (kind, position, data.get("dropped_player_id"), data.get("dropped_club_name"),
                data.get("added_player_id"), data.get("added_club_name"), pick_id)
        if DB_TYPE == "postgres":
            db_execute("""UPDATE draft_picks SET status='done', kind=%s, position=%s, dropped_player_id=%s,
                dropped_club_name=%s, added_player_id=%s, added_club_name=%s, completed_at=NOW() WHERE id=%s""", args)
        else:
            db_execute("""UPDATE draft_picks SET status='done', kind=?, position=?, dropped_player_id=?,
                dropped_club_name=?, added_player_id=?, added_club_name=?, completed_at=datetime('now') WHERE id=?""", args)
    else:
        return jsonify({"error": "Invalid action"}), 400

    next_pick = db_fetchone(
        "SELECT id FROM draft_picks WHERE session_id=%s AND turn_number=%s" if DB_TYPE == "postgres" else
        "SELECT id FROM draft_picks WHERE session_id=? AND turn_number=?",
        (pick["session_id"], pick["turn_number"] + 1))
    if next_pick:
        db_execute("UPDATE draft_picks SET status='active' WHERE id=%s" if DB_TYPE == "postgres" else
                   "UPDATE draft_picks SET status='active' WHERE id=?", (next_pick["id"],))

    return jsonify(build_draft_response())

@app.route("/api/draft/end", methods=["POST"])
def end_draft():
    data = request.get_json()
    if data.get("pin") != DRAFT_PIN:
        return jsonify({"error": "Incorrect PIN"}), 403
    if DB_TYPE == "postgres":
        db_execute("UPDATE draft_sessions SET status='completed', ended_at=NOW() WHERE status='active'")
    else:
        db_execute("UPDATE draft_sessions SET status='completed', ended_at=datetime('now') WHERE status='active'")
    return jsonify(build_draft_response())

@app.route("/api/draft/override", methods=["POST"])
def draft_override():
    data = request.get_json()
    if data.get("pin") != DRAFT_PIN:
        return jsonify({"error": "Incorrect PIN"}), 403
    pick_id = data.get("pick_id")
    pick = _row(db_fetchone(
        "SELECT * FROM draft_picks WHERE id=%s" if DB_TYPE == "postgres" else "SELECT * FROM draft_picks WHERE id=?",
        (pick_id,)))
    if not pick:
        return jsonify({"error": "Pick not found"}), 404

    kind = data.get("kind"); position = data.get("position")
    dropped_player_id = data.get("dropped_player_id"); dropped_club_name = data.get("dropped_club_name")
    added_player_id   = data.get("added_player_id");   added_club_name   = data.get("added_club_name")
    args = (kind, position, dropped_player_id, dropped_club_name, added_player_id, added_club_name, pick_id)
    if DB_TYPE == "postgres":
        db_execute("""UPDATE draft_picks SET status='done', kind=%s, position=%s, dropped_player_id=%s,
            dropped_club_name=%s, added_player_id=%s, added_club_name=%s WHERE id=%s""", args)
    else:
        db_execute("""UPDATE draft_picks SET status='done', kind=?, position=?, dropped_player_id=?,
            dropped_club_name=?, added_player_id=?, added_club_name=? WHERE id=?""", args)

    # Re-apply the corrected slot to the real squad too, so the fix isn't just cosmetic in the log
    if kind == "gk" and position and added_club_name:
        slot = int(position.replace("gk", ""))
        _apply_gk_slot(pick["team_id"], slot, added_club_name)
    elif position and added_player_id is not None:
        _apply_squad_slot(pick["team_id"], position, added_player_id)

    return jsonify(build_draft_response())

@app.route("/api/health")
def health():
    count = db_fetchone("SELECT COUNT(*) as c FROM squads")
    return jsonify({"ok": True, "db_type": DB_TYPE, "squad_rows": count["c"] if count else 0})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
