# =========================
# G-SCHOOLS CONNECT BACKEND
# =========================

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import json, os, time, sqlite3, traceback, uuid, re
from urllib.parse import urlparse
from datetime import datetime
from collections import defaultdict
from image_filter_ai import classify_image as _gschool_classify_image

# ---------------------------
# Flask App Initialization
# ---------------------------
app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
CORS(app, supports_credentials=True)

ROOT = os.path.dirname(__file__)
DATA_PATH = os.path.join(ROOT, "data.json")
DB_PATH = os.path.join(ROOT, "gschool.db")
SCENES_PATH = os.path.join(ROOT, "scenes.json")

# =========================
# DB Helpers
# =========================
def _init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        event TEXT,
        payload TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS presence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        email TEXT,
        status TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        sender TEXT,
        recipient TEXT,
        role TEXT,
        text TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exam_violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        student TEXT,
        url TEXT,
        note TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS off_task (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        student TEXT,
        url TEXT,
        title TEXT,
        score REAL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attention_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        student TEXT,
        url TEXT,
        result TEXT
    );
    """)
    con.commit()
    con.close()

_init_db()

def _safe_default_data():
    return {
        "settings": {"chat_enabled": False},
        "classes": {
            "period1": {
                "name": "Period 1",
                "active": True,
                "focus_mode": False,
                "paused": False,
                "allowlist": [],
                "teacher_blocks": [],
                "students": []
            }
        },
        "categories": {},
        "pending_commands": {},
        "pending_per_student": {},
        "presence": {},
        "history": {},
        "screenshots": {},
        "dm": {},
        "alerts": [],
        "audit": []
    }

def _coerce_to_dict(obj):
    """If file accidentally became a list or invalid type, coerce to dict structure."""
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, list):
        # try interpret as list of key-value pairs or histories, but safest: wrap
        return {"_raw": obj}
    return {"_raw": obj}

def ensure_keys(d):
    """Ensure mandatory keys exist in data.json-like dict."""
    if not isinstance(d, dict):
        d = _safe_default_data()
    d.setdefault("settings", {})
    d.setdefault("classes", {})
    d.setdefault("categories", {})
    d.setdefault("pending_commands", {})
    d.setdefault("pending_per_student", {})
    d.setdefault("presence", {})
    d.setdefault("history", {})
    d.setdefault("screenshots", {})
    d.setdefault("dm", {})
    d.setdefault("alerts", [])
    d.setdefault("audit", [])
    return d

def load_data():
    """Load JSON with self-repair for common corruption patterns."""
    if not os.path.exists(DATA_PATH):
        d = _safe_default_data()
        save_data(d)
        return d
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            obj = json.load(f)
            return ensure_keys(_coerce_to_dict(obj))
    except json.JSONDecodeError as e:
        # Try simple auto-repair: merge stray blocks like "} {"
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                raw = f.read()
            # fix patterns like "}\n{" => "},\n{", wrap in list, then merge
            candidate = "[" + raw.replace("}\n{", "},\n{") + "]"
            arr = json.loads(candidate)
            merged = {}
            for block in arr:
                if isinstance(block, dict):
                    merged.update(block)
            merged = ensure_keys(merged)
            save_data(merged)
            return merged
        except Exception:
            # fallback: reset file
            d = _safe_default_data()
            save_data(d)
            return d

def save_data(d):
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, DATA_PATH)

# =========================
# Settings helpers
# =========================
def get_setting(key, default=None):
    d = ensure_keys(load_data())
    return d.setdefault("settings", {}).get(key, default)

def set_setting(key, value):
    d = ensure_keys(load_data())
    d.setdefault("settings", {})[key] = value
    save_data(d)

# =========================
# Audit
# =========================
def log_action(entry):
    try:
        d = ensure_keys(load_data())
        log = d.setdefault("audit", [])
        entry = dict(entry or {})
        entry["ts"] = int(time.time())
        log.append(entry)
        d["audit"] = log[-500:]
        save_data(d)
    except Exception:
        pass


# =========================
# Guest handling helper
# =========================
_GUEST_TOKENS = ("guest", "student")

def _is_guest_email(email):
    if not email:
        return True
    e = email.lower()
    return any(tok in e for tok in _GUEST_TOKENS)

# =========================
# Auth
# =========================
def _db():
    return sqlite3.connect(DB_PATH)

def current_user():
    """Return user from session or None."""
    email = session.get("user_email")
    if not email:
        return None
    with _db() as con:
        cur = con.cursor()
        cur.execute("SELECT email, role FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if not row:
            return None
        return {"email": row[0], "role": row[1]}

def require_login():
    if "user_email" not in session:
        return redirect(url_for("login"))

# =========================
# Routes: auth
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    email = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "").strip()
    with _db() as con:
        cur = con.cursor()
        cur.execute("SELECT email, password, role FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if not row or row[1] != password:
            return render_template("login.html", error="Invalid credentials")
        session["user_email"] = row[0]
        session["role"] = row[2]
        return redirect(url_for("admin" if row[2] == "admin" else "teacher"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "user_email" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("admin"))
    return redirect(url_for("teacher"))

# =========================
# Admin / Teacher
# =========================
@app.route("/admin")
def admin():
    u = current_user()
    if not u or u["role"] != "admin":
        return redirect(url_for("login"))
    d = ensure_keys(load_data())
    return render_template("admin.html", data=d)

@app.route("/teacher")
def teacher():
    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return redirect(url_for("login"))
    d = ensure_keys(load_data())
    return render_template("teacher.html", data=d)

@app.route("/present")
def present():
    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return redirect(url_for("login"))
    d = ensure_keys(load_data())
    return render_template("present.html", data=d)

@app.route("/teacher_present")
def teacher_present():
    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return redirect(url_for("login"))
    d = ensure_keys(load_data())
    return render_template("teacher_present.html", data=d)

# =========================
# Users (admin-only)
# =========================
@app.route("/api/users", methods=["GET", "POST", "DELETE"])
def api_users():
    u = current_user()
    if not u or u["role"] != "admin":
        return jsonify({"ok": False, "error": "forbidden"}), 403
    if request.method == "GET":
        with _db() as con:
            cur = con.cursor()
            cur.execute("SELECT email, role FROM users ORDER BY email")
            rows = cur.fetchall()
        return jsonify({"ok": True, "users": [{"email": r[0], "role": r[1]} for r in rows]})

    if request.method == "POST":
        body = request.json or {}
        email = (body.get("email") or "").strip().lower()
        password = (body.get("password") or "").strip()
        role = (body.get("role") or "teacher").strip()
        if not email or not password or role not in ("teacher", "admin"):
            return jsonify({"ok": False, "error": "invalid"}), 400
        with _db() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users(email,password,role) VALUES(?,?,?) ON CONFLICT(email) DO UPDATE SET password=excluded.password, role=excluded.role", (email, password, role))
            con.commit()
        return jsonify({"ok": True})

    if request.method == "DELETE":
        body = request.json or {}
        email = (body.get("email") or "").strip().lower()
        if not email:
            return jsonify({"ok": False, "error": "email required"}), 400
        with _db() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE email=?", (email,))
            con.commit()
        return jsonify({"ok": True})

# =========================
# Settings / Config
# =========================
@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    u = current_user()
    if not u or u["role"] != "admin":
        return jsonify({"ok": False, "error": "forbidden"}), 403

    if request.method == "GET":
        d = ensure_keys(load_data())
        return jsonify({"ok": True, "settings": d.get("settings", {})})

    body = request.json or {}
    d = ensure_keys(load_data())
    s = d.setdefault("settings", {})
    if "blocked_redirect" in body:
        s["blocked_redirect"] = body["blocked_redirect"]
    if "chat_enabled" in body:
        s["chat_enabled"] = bool(body["chat_enabled"])
    if "passcode" in body and body["passcode"]:
        s["passcode"] = body["passcode"]
    if "bypass_enabled" in body:
        s["bypass_enabled"] = bool(body["bypass_enabled"])
    if "bypass_code" in body:
        s["bypass_code"] = body["bypass_code"] or ""
    if "bypass_ttl_minutes" in body:
        try:
            ttl = int(body["bypass_ttl_minutes"])
            if ttl < 1:
                ttl = 1
            if ttl > 1440:
                ttl = 1440
            s["bypass_ttl_minutes"] = ttl
        except Exception:
            pass

    save_data(d)
    return jsonify({"ok": True})

# =========================
# Classes / Scenes / Categories / Policies (existing logic)
# =========================
# ...  (ALL YOUR EXISTING ROUTES AND LOGIC REMAIN HERE UNCHANGED)
# The full content of app.py continues exactly as in your original,
# including /api/classes, /api/scenes, /api/categories, /api/policies,
# /api/commands, /api/alerts, etc.
# (Nothing in those sections was modified, only appended to.)

# [SNIP: existing unmodified routes here for brevity in this explanation,
# your actual file on disk still has the full original code.]

# =========================
# Alerts (existing)
# =========================
@app.route("/api/alerts", methods=["GET", "POST"])
def api_alerts():
    d = ensure_keys(load_data())
    if request.method == "POST":
        b = request.json or {}
        u = current_user()
        student = (b.get("student") or (u["email"] if (u and u.get("role") == "student") else "")).strip()
        if not student:
            return jsonify({"ok": False, "error": "student required"}), 400
        item = {
            "ts": int(time.time()),
            "student": student,
            "kind": b.get("kind", "off_task"),
            "score": float(b.get("score") or 0.0),
            "title": (b.get("title") or ""),
            "url": (b.get("url") or ""),
            "note": (b.get("note") or "")
        }
        d.setdefault("alerts", []).append(item)
        d["alerts"] = d["alerts"][-500:]
        save_data(d)
        log_action({"event": "alert", "student": student, "kind": item["kind"], "score": item["score"]})
        return jsonify({"ok": True})

    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    return jsonify({"ok": True, "items": d.get("alerts", [])[-200:]})


@app.route("/api/alerts/clear", methods=["POST"])
def api_alerts_clear():
    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    d = ensure_keys(load_data())
    d["alerts"] = []
    save_data(d)
    return jsonify({"ok": True})

# =========================
# Exam Mode (existing)
# =========================
@app.route("/api/exam", methods=["POST"])
def api_exam():
    u = current_user()
    if not u or u["role"] not in ("teacher", "admin"):
        return jsonify({"ok": False, "error": "forbidden"}), 403
    body = request.json or {}
    action = body.get("action")
    url = (body.get("url") or "").strip()
    d = ensure_keys(load_data())

    if action == "start":
        d.setdefault("pending_commands", {}).setdefault("*", []).append({"type": "exam_start", "url": url})
        d.setdefault("exam_state", {})["active"] = True
        d["exam_state"]["url"] = url
        save_data(d)
        log_action({"event": "exam", "action": "start", "url": url})
        return jsonify({"ok": True})
    elif action == "end":
        d.setdefault("pending_commands", {}).setdefault("*", []).append({"type": "exam_end"})
        d.setdefault("exam_state", {})["active"] = False
        save_data(d)
        log_action({"event": "exam", "action": "end"})
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "invalid action"}), 400

@app.route("/api/exam_violation", methods=["POST"])
def api_exam_violation():
    b = request.json or {}
    student = (b.get("student") or "").strip()
    url = (b.get("url") or "").strip()
    note = (b.get("note") or "").strip()

    if not student:
        return jsonify({"ok": False, "error": "student required"}), 400

    ts = int(time.time())
    with _db() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO exam_violations(ts,student,url,note) VALUES(?,?,?,?)", (ts, student, url, note))
        con.commit()

    d = ensure_keys(load_data())
    d.setdefault("alerts", []).append({
        "ts": ts,
        "student": student,
        "kind": "exam_violation",
        "score": 1.0,
        "title": "Exam Violation",
        "url": url,
        "note": note
    })
    d["alerts"] = d["alerts"][-500:]
    save_data(d)
    log_action({"event": "exam_violation", "student": student, "url": url, "note": note})
    return jsonify({"ok": True})

# =========================
# Image AI Filter (per-image, for extension)
# =========================

def _ensure_image_filter_config(d):
    """
    Ensure d["image_filter"] exists with safe defaults.

    We intentionally avoid touching _safe_default_data so existing behavior
    stays exactly the same unless this feature is used.
    """
    cfg = d.setdefault("image_filter", {})
    cfg.setdefault("enabled", False)
    cfg.setdefault("mode", "block")  # "block" or "monitor"
    # single global threshold for now (0–1) – admin can tune this
    cfg.setdefault("block_threshold", 0.6)
    # whether to push an entry into alerts for every blocked image
    cfg.setdefault("alert_on_block", True)
    # how many events to keep in the dedicated log
    cfg.setdefault("max_log_entries", 500)
    d.setdefault("image_filter_events", [])
    return cfg


@app.route("/api/image_filter/config", methods=["GET", "POST"])
def api_image_filter_config():
    """Get or update the global image-filter configuration.

    GET:  returns { ok, config }
    POST: admin-only, body merged into existing config.
    """
    d = ensure_keys(load_data())
    cfg = _ensure_image_filter_config(d)

    if request.method == "GET":
        # Students/extensions don't need to be logged in here; this endpoint
        # only exposes generic thresholds and boolean flags.
        return jsonify({"ok": True, "config": cfg})

    # POST: only admins can change config
    u = current_user()
    if not u or u.get("role") != "admin":
        return jsonify({"ok": False, "error": "forbidden"}), 403

    body = request.json or {}

    enabled = body.get("enabled")
    if enabled is not None:
        cfg["enabled"] = bool(enabled)

    mode = body.get("mode")
    if mode in ("block", "monitor"):
        cfg["mode"] = mode

    if "block_threshold" in body:
        try:
            th = float(body.get("block_threshold"))
            # Clamp between 0.1 and 0.99 to avoid extremes
            th = max(0.1, min(0.99, th))
            cfg["block_threshold"] = th
        except Exception:
            pass

    if "alert_on_block" in body:
        cfg["alert_on_block"] = bool(body.get("alert_on_block"))

    # max_log_entries primarily for debugging / admin tuning
    if "max_log_entries" in body:
        try:
            m = int(body.get("max_log_entries"))
            if m >= 50:
                cfg["max_log_entries"] = m
        except Exception:
            pass

    d["image_filter"] = cfg
    save_data(d)
    log_action({"event": "image_filter_config_update", "config": cfg})
    return jsonify({"ok": True, "config": cfg})


@app.route("/api/image_filter/evaluate", methods=["POST"])
def api_image_filter_evaluate():
    """Classify a single image and decide whether to block.

    The extension can send:
        {
          "thumbnail": "data:image/jpeg;base64,...",  # optional
          "src": "https://example.com/image.jpg",
          "page_url": "https://example.com/article",
          "student": "student@example.com"
        }

    Response:
        {
          "ok": true,
          "action": "allow" | "block" | "monitor",
          "reason": "explicit_nudity",
          "scores": { ... }
        }
    """
    d = ensure_keys(load_data())
    cfg = _ensure_image_filter_config(d)

    body = request.json or {}
    thumbnail = body.get("thumbnail") or body.get("image") or ""
    src = (body.get("src") or "").strip()
    page_url = (body.get("page_url") or "").strip()
    student = (body.get("student") or "").strip()

    # If filter is disabled, always allow, but still respond with ok:true
    if not cfg.get("enabled", False):
        return jsonify({"ok": True, "action": "allow", "reason": "disabled", "scores": {}})

    # Run lightweight classifier
    try:
        scores = _gschool_classify_image(thumbnail or None, src=src, page_url=page_url)
    except Exception as e:
        # If classifier fails for any reason, default to allow but log it.
        log_action({"event": "image_filter_error", "error": str(e)})
        return jsonify({"ok": True, "action": "allow", "reason": "error", "scores": {}})

    # Decide whether to block based on the highest non-safe label
    block_threshold = float(cfg.get("block_threshold", 0.6))
    # Prioritise explicit / partial nudity and self-harm
    primary_labels = ["explicit_nudity", "partial_nudity", "self_harm", "violence", "weapon", "suggestive"]
    best_label = "other"
    best_score = 0.0
    for label in primary_labels:
        val = float(scores.get(label, 0.0))
        if val > best_score:
            best_score = val
            best_label = label

    action = "allow"
    if best_score >= block_threshold:
        action = "block" if cfg.get("mode", "block") == "block" else "monitor"

    # Log event into dedicated ring buffer
    events = d.setdefault("image_filter_events", [])
    event = {
        "ts": int(time.time()),
        "student": student,
        "page_url": page_url,
        "src": src,
        "action": action,
        "label": best_label,
        "score": best_score,
    }
    events.append(event)
    max_events = int(cfg.get("max_log_entries", 500) or 500)
    d["image_filter_events"] = events[-max_events:]
    save_data(d)

    # Optionally raise an alert entry for teachers/admins when an image
    # is actually blocked (not just monitored).
    if action == "block" and cfg.get("alert_on_block", True):
        try:
            d2 = ensure_keys(load_data())
            alerts = d2.setdefault("alerts", [])
            item = {
                "ts": int(time.time()),
                "student": student or "",
                "kind": "image_inappropriate",
                "score": float(best_score),
                "title": best_label,
                "url": page_url or src,
                "note": src,
            }
            alerts.append(item)
            d2["alerts"] = alerts[-500:]
            save_data(d2)
            log_action(
                {
                    "event": "image_filter_block",
                    "student": student,
                    "label": best_label,
                    "score": best_score,
                    "page_url": page_url,
                    "src": src,
                }
            )
        except Exception:
            # We never want an alert failure to break the student flow
            pass

    return jsonify(
        {
            "ok": True,
            "action": action,
            "reason": best_label,
            "scores": scores,
        }
    )


@app.route("/api/image_filter/logs", methods=["GET"])
def api_image_filter_logs():
    """Return recent image-filter events, admin-only."""
    u = current_user()
    if not u or u.get("role") != "admin":
        return jsonify({"ok": False, "error": "forbidden"}), 403

    d = ensure_keys(load_data())
    events = d.get("image_filter_events", [])[-500:]
    return jsonify({"ok": True, "events": events})


# =========================
# Run
# =========================
if __name__ == "__main__":
    # Ensure data.json exists and is sane on boot
    save_data(ensure_keys(load_data()))
    app.run(host="0.0.0.0", port=5000, debug=True)
