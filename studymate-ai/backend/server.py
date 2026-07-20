#!/usr/bin/env python3
"""
StudyMate AI — Complete Backend Server
Replaces Firebase Auth + Firestore + Storage entirely.
Run: python server.py
Then access:
  - API:        http://YOUR_IP:8765/api/...
  - Admin Site: http://YOUR_IP:8765/admin
  - App:        Connect via YOUR_IP:8765
"""

import os
import re
import io
import json
import uuid
import hashlib
import base64
import sqlite3
import datetime
import threading
import time
import mimetypes
from datetime import timezone
from pathlib import Path
from functools import wraps
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ─── Configuration ─────────────────────────────────

HOST = "0.0.0.0"
PORT = 8765
DB_PATH = Path(__file__).parent / "studymate.db"
SECRET_KEY = "studymate-ai-secret-key-2026-ultra-secure"

# ─── Database Setup ────────────────────────────────

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            photo_url TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            degree TEXT DEFAULT '',
            department TEXT DEFAULT '',
            year TEXT DEFAULT '',
            semester INTEGER DEFAULT 1,
            stream TEXT DEFAULT '',
            college TEXT DEFAULT '',
            class_division TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0,
            is_profile_complete INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak INTEGER DEFAULT 0,
            total_study_minutes INTEGER DEFAULT 0,
            quizzes_completed INTEGER DEFAULT 0,
            flashcards_reviewed INTEGER DEFAULT 0,
            notes_created INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            last_active TEXT
        )
    """)

    # Study sessions
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id TEXT PRIMARY KEY,
            user_uid TEXT NOT NULL,
            subject TEXT DEFAULT '',
            duration_minutes INTEGER DEFAULT 0,
            start_time TEXT NOT NULL,
            end_time TEXT,
            notes TEXT DEFAULT '',
            FOREIGN KEY (user_uid) REFERENCES users(uid)
        )
    """)

    # Notes
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            user_uid TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            FOREIGN KEY (user_uid) REFERENCES users(uid)
        )
    """)

    # Quizzes
    c.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id TEXT PRIMARY KEY,
            user_uid TEXT NOT NULL,
            title TEXT NOT NULL,
            subject TEXT DEFAULT '',
            questions TEXT DEFAULT '[]',
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid)
        )
    """)

    # Flashcards
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id TEXT PRIMARY KEY,
            user_uid TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            subject TEXT DEFAULT '',
            difficulty INTEGER DEFAULT 1,
            reviewed_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid)
        )
    """)

    # Friends
    c.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id TEXT PRIMARY KEY,
            user_uid TEXT NOT NULL,
            friend_uid TEXT NOT NULL,
            friend_name TEXT DEFAULT '',
            friend_photo_url TEXT DEFAULT '',
            status TEXT DEFAULT 'accepted',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_uid) REFERENCES users(uid)
        )
    """)

    # Messages
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            sender_uid TEXT NOT NULL,
            sender_name TEXT DEFAULT '',
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"[OK] Database ready: {DB_PATH}")

# ─── Helper Functions ──────────────────────────────

def hash_password(password):
    """SHA256 hash with salt."""
    salt = "studymate_ai_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_uid():
    return str(uuid.uuid4())

def now_iso():
    return datetime.datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def row_to_dict(row):
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return dict(row)

def rows_to_list(rows):
    return [dict(r) for r in rows]

def json_response(status, data):
    body = json.dumps(data, default=str).encode()
    return (status, body, {"Content-Type": "application/json"})

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

# ─── JWT-like Token (simple HMAC) ──────────────────

def create_token(uid, username, is_admin=0):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "uid": uid,
        "username": username,
        "is_admin": is_admin,
        "iat": time.time(),
        "exp": time.time() + 86400 * 30  # 30 days
    }
    import base64
    def b64(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()
    h = b64(header)
    p = b64(payload)
    sig_input = f"{h}.{p}"
    sig = hashlib.sha256((sig_input + SECRET_KEY).encode()).hexdigest()
    return f"{h}.{p}.{sig}"

def verify_token(token):
    """Returns payload dict or None."""
    import base64
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        h, p, sig = parts
        sig_input = f"{h}.{p}"
        expected = hashlib.sha256((sig_input + SECRET_KEY).encode()).hexdigest()
        if sig != expected:
            return None
        # Decode payload
        padded = p + "=" * (4 - len(p) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

# ─── HTTP Handler ──────────────────────────────────

class StudyMateHandler(BaseHTTPRequestHandler):

    def _send(self, status, body, extra_headers=None):
        headers = cors_headers()
        if extra_headers:
            headers.update(extra_headers)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, data):
        body = json.dumps(data, default=str).encode()
        self._send(status, body)

    def _text(self, status, text):
        body = text.encode()
        self._send(status, body, {"Content-Type": "text/plain; charset=utf-8"})

    def _html(self, status, html):
        body = html.encode()
        self._send(status, body, {"Content-Type": "text/html; charset=utf-8"})

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _get_token_user(self):
        """Extract user from Authorization header."""
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            payload = verify_token(token)
            if payload:
                conn = get_db()
                user = conn.execute("SELECT * FROM users WHERE uid = ?", (payload["uid"],)).fetchone()
                conn.close()
                return row_to_dict(user)
        return None

    def _require_auth(self):
        user = self._get_token_user()
        if not user:
            self._json(401, {"error": "Unauthorized. Please login again."})
            return None
        return user

    def _require_admin(self):
        user = self._require_auth()
        if not user:
            return None
        if not user.get("is_admin"):
            self._json(403, {"error": "Admin access required."})
            return None
        return user

    def log_message(self, format, *args):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}")

    # ─── Routing ───────────────────────────────────

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        # Admin dashboard
        if path == "/admin" or path == "":
            return self._serve_admin()
        if path == "/admin/users":
            return self._serve_admin_users()
        if path == "/admin/login":
            return self._serve_admin_login()

        # Photo upload page
        if path == "/upload":
            return self._serve_upload_page()

        # Serve uploaded photos
        if path.startswith("/photos/"):
            return self._serve_photo(path)

        # Serve uploaded files
        if path.startswith("/uploads/"):
            return self._serve_upload(path)

        # API routes
        if path == "/api/health":
            return self._json(200, {"status": "ok", "message": "StudyMate AI Backend Running!"})
        if path == "/api/users":
            return self._api_get_users()
        if path.startswith("/api/users/"):
            uid = path.split("/")[-1]
            return self._api_get_user(uid)
        if path == "/api/sessions":
            return self._api_list("study_sessions", "user_uid")
        if path == "/api/notes":
            return self._api_list("notes", "user_uid")
        if path == "/api/quizzes":
            return self._api_list("quizzes", "user_uid")
        if path == "/api/flashcards":
            return self._api_list("flashcards", "user_uid")
        if path == "/api/friends":
            return self._api_list("friends", "user_uid")
        if path == "/api/messages":
            return self._api_list("messages", "user_uid")

        self._json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = self._read_body()

        # Auth routes
        if path == "/api/auth/register":
            return self._api_register(data)
        if path == "/api/auth/login":
            return self._api_login(data)
        if path == "/api/auth/login/username":
            return self._api_login_username(data)
        if path == "/api/auth/login/uid":
            return self._api_login_uid(data)
        if path == "/api/auth/forgot-password":
            return self._api_forgot_password(data)

        # Photo upload (base64)
        if path == "/api/upload/photo":
            return self._api_upload_photo(data)

        # Create routes
        if path == "/api/sessions":
            return self._api_create("study_sessions", data)
        if path == "/api/notes":
            return self._api_create("notes", data)
        if path == "/api/quizzes":
            return self._api_create("quizzes", data)
        if path == "/api/flashcards":
            return self._api_create("flashcards", data)
        if path == "/api/friends":
            return self._api_create("friends", data)

        self._json(404, {"error": "Not found"})

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = self._read_body()

        if path.startswith("/api/users/"):
            uid = path.split("/")[-1]
            return self._api_update_user(uid, data)
        if path.startswith("/api/notes/"):
            note_id = path.split("/")[-1]
            return self._api_update("notes", note_id, data)

        self._json(404, {"error": "Not found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/notes/"):
            note_id = path.split("/")[-1]
            return self._api_delete("notes", note_id)

        self._json(404, {"error": "Not found"})

    # ─── Auth API ──────────────────────────────────

    def _api_register(self, data):
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        name = (data.get("displayName") or data.get("name") or "").strip()
        if not email or not password or not name:
            return self._json(400, {"error": "Email, password, and name are required."})

        conn = get_db()
        # Check if email exists
        exists = conn.execute("SELECT uid FROM users WHERE email = ?", (email,)).fetchone()
        if exists:
            conn.close()
            return self._json(409, {"error": "An account with this email already exists."})

        # Generate unique username
        base = re.sub(r'[^a-z0-9]', '', name.lower())[:20]
        username = base
        counter = 1
        while conn.execute("SELECT uid FROM users WHERE username = ?", (username,)).fetchone():
            counter += 1
            username = f"{base}{counter:02d}"

        uid = generate_uid()
        now = now_iso()
        pw_hash = hash_password(password)

        conn.execute("""INSERT INTO users (uid, email, username, display_name, password_hash, created_at, last_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (uid, email, username, name, pw_hash, now, now))
        conn.commit()

        # Return user without password
        user = conn.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()
        conn.close()
        user_dict = row_to_dict(user)
        token = create_token(uid, username, 0)
        return self._json(201, {
            "message": "Account created successfully!",
            "token": token,
            "user": user_dict
        })

    def _api_login(self, data):
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not password:
            return self._json(400, {"error": "Email and password are required."})

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user:
            conn.close()
            return self._json(401, {"error": "No account found with this email."})

        user_dict = row_to_dict(user)
        if user_dict["password_hash"] != hash_password(password):
            conn.close()
            return self._json(401, {"error": "Incorrect password. Please try again."})

        # Update last active
        conn.execute("UPDATE users SET last_active = ? WHERE uid = ?", (now_iso(), user_dict["uid"]))
        conn.commit()
        conn.close()

        token = create_token(user_dict["uid"], user_dict["username"], user_dict.get("is_admin", 0))
        return self._json(200, {"token": token, "user": user_dict})

    def _api_login_username(self, data):
        username = (data.get("username") or "").strip().lower()
        password = data.get("password") or ""
        if not username or not password:
            return self._json(400, {"error": "Username and password are required."})

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            conn.close()
            return self._json(401, {"error": f'No account found with username "{username}".'})

        user_dict = row_to_dict(user)
        if user_dict["password_hash"] != hash_password(password):
            conn.close()
            return self._json(401, {"error": "Incorrect password. Please try again."})

        conn.execute("UPDATE users SET last_active = ? WHERE uid = ?", (now_iso(), user_dict["uid"]))
        conn.commit()
        conn.close()

        token = create_token(user_dict["uid"], user_dict["username"], user_dict.get("is_admin", 0))
        return self._json(200, {"token": token, "user": user_dict})

    def _api_login_uid(self, data):
        uid = data.get("uid") or ""
        if not uid:
            return self._json(400, {"error": "UID is required."})

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()
        if not user:
            conn.close()
            return self._json(401, {"error": "User not found."})

        user_dict = row_to_dict(user)
        conn.execute("UPDATE users SET last_active = ? WHERE uid = ?", (now_iso(), uid))
        conn.commit()
        conn.close()

        token = create_token(user_dict["uid"], user_dict["username"], user_dict.get("is_admin", 0))
        return self._json(200, {"token": token, "user": user_dict})

    def _api_forgot_password(self, data):
        email = (data.get("email") or "").strip().lower()
        username = (data.get("username") or "").strip().lower()

        conn = get_db()
        if email:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        elif username:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        else:
            conn.close()
            return self._json(400, {"error": "Email or username required."})

        if not user:
            conn.close()
            return self._json(404, {"error": "No account found."})

        user_dict = row_to_dict(user)
        conn.close()
        # In local mode, password reset is done via face recognition
        return self._json(200, {
            "message": "User found. Use face recognition to reset password.",
            "email": user_dict["email"],
            "uid": user_dict["uid"]
        })

    # ─── User API ──────────────────────────────────

    def _api_get_users(self):
        admin = self._require_admin()
        if not admin:
            return
        conn = get_db()
        users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
        conn.close()
        return self._json(200, {"users": rows_to_list(users)})

    def _api_get_user(self, uid):
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()
        conn.close()
        if not user:
            return self._json(404, {"error": "User not found"})
        return self._json(200, {"user": row_to_dict(user)})

    def _api_update_user(self, uid, data):
        user = self._require_auth()
        if not user:
            return
        # Only allow updating own profile (or admin)
        if user["uid"] != uid and not user.get("is_admin"):
            return self._json(403, {"error": "Cannot update another user's profile."})

        allowed_fields = [
            "display_name", "photo_url", "bio", "degree", "department", "year",
            "semester", "stream", "college", "class_division", "is_profile_complete",
            "xp", "level", "streak", "total_study_minutes", "quizzes_completed",
            "flashcards_reviewed", "notes_created"
        ]

        updates = {}
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]

        if not updates:
            return self._json(400, {"error": "No valid fields to update."})

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [uid]

        conn = get_db()
        conn.execute(f"UPDATE users SET {set_clause} WHERE uid = ?", values)
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()
        conn.close()
        return self._json(200, {"message": "Profile updated.", "user": row_to_dict(user)})

    # ─── Generic CRUD ──────────────────────────────

    def _api_list(self, table, user_field):
        user = self._require_auth()
        if not user:
            return
        # Support ?user_uid=xxx query param
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        uid = params.get(user_field, [user["uid"]])[0]

        conn = get_db()
        rows = conn.execute(f"SELECT * FROM {table} WHERE {user_field} = ? ORDER BY created_at DESC",
                           (uid,)).fetchall()
        conn.close()
        return self._json(200, {table: rows_to_list(rows)})

    def _api_create(self, table, data):
        user = self._require_auth()
        if not user:
            return
        data["id"] = data.get("id", generate_uid())
        data["user_uid"] = user["uid"]
        data["created_at"] = data.get("created_at", now_iso())

        # Get columns from the actual table
        conn = get_db()
        cols = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        filtered = {k: v for k, v in data.items() if k in cols}

        if not filtered:
            conn.close()
            return self._json(400, {"error": "No valid data."})

        placeholders = ", ".join("?" for _ in filtered)
        columns = ", ".join(filtered.keys())
        values = list(filtered.values())

        conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        return self._json(201, {"message": "Created.", "id": data["id"]})

    def _api_update(self, table, item_id, data):
        user = self._require_auth()
        if not user:
            return

        allowed_fields = {
            "notes": ["title", "content", "subject", "tags", "is_pinned", "updated_at"],
            "study_sessions": ["subject", "duration_minutes", "end_time", "notes"],
            "quizzes": ["title", "subject", "questions", "score", "total_questions", "completed_at"],
            "flashcards": ["question", "answer", "subject", "difficulty", "reviewed_count"],
        }

        allowed = allowed_fields.get(table, [])
        updates = {k: v for k, v in data.items() if k in allowed}

        if not updates:
            return self._json(400, {"error": "No valid fields to update."})

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [item_id]

        conn = get_db()
        conn.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return self._json(200, {"message": "Updated."})

    def _api_delete(self, table, item_id):
        user = self._require_auth()
        if not user:
            return
        conn = get_db()
        conn.execute(f"DELETE FROM {table} WHERE id = ? AND user_uid = ?", (item_id, user["uid"]))
        conn.commit()
        conn.close()
        return self._json(200, {"message": "Deleted."})

    # ─── Photo Upload ─────────────────────────────

    def _serve_photo(self, path):
        """Serve uploaded photo files."""
        photos_dir = Path(__file__).parent / "photos"
        filename = path.replace("/photos/", "").replace("..", "").replace("/", "")
        filepath = photos_dir / filename
        if not filepath.exists() or not filepath.is_file():
            # Return default avatar SVG
            return self._svg_avatar(filename.replace(".jpg", "").replace(".png", ""))
        mime_type, _ = mimetypes.guess_type(str(filepath))
        if mime_type is None:
            mime_type = "image/jpeg"
        with open(filepath, "rb") as f:
            data = f.read()
        self._send(200, data, {"Content-Type": mime_type, "Cache-Control": "max-age=3600"})

    def _serve_upload(self, path):
        """Serve uploaded files."""
        uploads_dir = Path(__file__).parent / "uploads"
        filename = path.replace("/uploads/", "").replace("..", "").replace("/", "")
        filepath = uploads_dir / filename
        if not filepath.exists() or not filepath.is_file():
            return self._json(404, {"error": "File not found"})
        mime_type, _ = mimetypes.guess_type(str(filepath))
        if mime_type is None:
            mime_type = "application/octet-stream"
        with open(filepath, "rb") as f:
            data = f.read()
        self._send(200, data, {"Content-Type": mime_type})

    def _svg_avatar(self, name):
        """Generate a simple SVG avatar with initials."""
        initial = (name[:2] if name else "?").upper()
        colors = ["#6C63FF", "#3F51B5", "#00C853", "#FF6B6B", "#FFA726", "#26C6DA", "#AB47BC", "#66BB6A"]
        color_idx = hash(name) % len(colors)
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
          <rect width="100" height="100" rx="50" fill="{colors[color_idx]}"/>
          <text x="50" y="50" text-anchor="middle" dy=".35em" fill="white" font-size="36" font-family="Arial, sans-serif" font-weight="bold">{initial}</text>
        </svg>'''
        return self._send(200, svg.encode(), {"Content-Type": "image/svg+xml"})

    def _api_upload_photo(self, data):
        """Upload a profile photo via base64 JSON."""
        user = self._require_auth()
        if not user:
            return
        uid = user["uid"]
        image_data = data.get("image", "")
        if not image_data:
            return self._json(400, {"error": "No image data provided."})

        try:
            # Remove data:image/... prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]
            # Decode base64
            img_bytes = base64.b64decode(image_data)
            # Save file
            photos_dir = Path(__file__).parent / "photos"
            photos_dir.mkdir(exist_ok=True)
            ext = data.get("format", "jpg")
            filename = f"{uid}.{ext}"
            filepath = photos_dir / filename
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            # Update user record
            photo_url = f"/photos/{filename}"
            conn = get_db()
            conn.execute("UPDATE users SET photo_url = ? WHERE uid = ?", (photo_url, uid))
            conn.commit()
            conn.close()
            return self._json(200, {"message": "Photo uploaded!", "photo_url": photo_url})
        except Exception as e:
            return self._json(500, {"error": f"Photo upload failed: {str(e)}"})

    def _serve_upload_page(self):
        """Serve a simple web page for uploading profile photos."""
        return self._html(200, UPLOAD_HTML)

    # ─── Admin Dashboard ──────────────────────────

    def _serve_admin(self):
        return self._html(200, ADMIN_HTML)

    def _serve_admin_users(self):
        admin = self._require_admin()
        if not admin:
            return self._html(401, "<h2>Unauthorized. Please login as admin.</h2><a href='/admin/login'>Login</a>")
        conn = get_db()
        users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
        conn.close()
        rows_html = ""
        for u in users:
            d = dict(u)
            photo = d.get('photo_url', '') or ''
            uid = d.get('uid', '')
            name = d.get('display_name', '')
            photo_img = f'<img src="{photo}" width="36" height="36" style="border-radius:50%;object-fit:cover;" onerror="this.style.display=\'none\'" alt="">' if photo else ''
            rows_html += f"""
            <tr>
              <td><div style="display:flex;align-items:center;gap:8px;">{photo_img}<span>{d.get('username','')}</span></div></td>
              <td>{name}</td>
              <td>{d.get('email','')}</td>
              <td>{d.get('degree','')} {d.get('department','')}</td>
              <td>{d.get('xp',0)}</td>
              <td>{d.get('level',1)}</td>
              <td>{d.get('streak',0)}</td>
              <td>{d.get('total_study_minutes',0)}</td>
              <td>{d.get('quizzes_completed',0)}</td>
              <td>{d.get('notes_created',0)}</td>
              <td>{d.get('created_at','')[:10]}</td>
              <td>{'✅' if d.get('is_admin') else ''}</td>
            </tr>
            """
        return self._html(200, f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>StudyMate AI — Admin Dashboard</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f1a; color:#e0e0e0; padding:20px; }}
            h1 {{ background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom:8px; font-size:1.8em; }}
            .sub {{ color:#888; margin-bottom:24px; }}
            table {{ width:100%; border-collapse:collapse; background:#1a1a2e; border-radius:12px; overflow:hidden; }}
            th {{ background:#16213e; color:#a78bfa; padding:12px 10px; text-align:left; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; }}
            td {{ padding:10px; border-bottom:1px solid #2a2a4a; font-size:14px; }}
            tr:hover {{ background:#1e1e36; }}
            .stats {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:16px; margin-bottom:24px; }}
            .stat-card {{ background:#1a1a2e; padding:16px; border-radius:12px; text-align:center; }}
            .stat-card .num {{ font-size:2em; font-weight:bold; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .stat-card .label {{ color:#888; font-size:13px; margin-top:4px; }}
            .badge {{ display:inline-block; background:#4a3f6b; color:#c4b5fd; padding:2px 8px; border-radius:4px; font-size:12px; }}
            @media (max-width:768px) {{ 
              table {{ font-size:12px; }} 
              th, td {{ padding:8px 6px; }}
              body {{ padding:12px; }}
            }}
          </style>
          <script>
            setTimeout(() => location.reload(), 15000);
          </script>
        </head>
        <body>
          <h1>📊 StudyMate Admin</h1>
          <div class="sub">Live user data — auto-refreshes every 15s</div>
          <div class="stats">
            <div class="stat-card"><div class="num">{len(users)}</div><div class="label">Total Users</div></div>
            <div class="stat-card"><div class="num">{sum(u['total_study_minutes'] or 0 for u in users)}</div><div class="label">Total Study Min</div></div>
            <div class="stat-card"><div class="num">{sum(u['quizzes_completed'] or 0 for u in users)}</div><div class="label">Quizzes Done</div></div>
            <div class="stat-card"><div class="num">{sum(u['notes_created'] or 0 for u in users)}</div><div class="label">Notes Created</div></div>
          </div>
          <table>
            <thead><tr>
              <th>User</th><th>Name</th><th>Email</th><th>Degree/Dept</th><th>XP</th>
              <th>Level</th><th>Streak</th><th>Study Min</th><th>Quizzes</th><th>Notes</th><th>Joined</th><th>Admin</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
          <p style="margin-top:16px;color:#666;font-size:13px;">
            <a href="/admin" style="color:#667eea;">← Back to Dashboard</a>
          </p>
        </body>
        </html>
        """)

    def _serve_admin_login(self):
        return self._html(200, """
        <!DOCTYPE html>
        <html>
        <head>
          <title>Admin Login — StudyMate</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   background: #0f0f1a; color:#e0e0e0; display:flex; align-items:center; justify-content:center;
                   min-height:100vh; padding:20px; }
            .card { background:#1a1a2e; padding:40px; border-radius:16px; width:100%; max-width:400px; }
            h1 { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text;
                 -webkit-text-fill-color: transparent; margin-bottom:24px; text-align:center; }
            input { width:100%; padding:14px 16px; margin-bottom:16px; background:#16213e; border:1px solid #2a2a4a;
                    border-radius:10px; color:#fff; font-size:16px; outline:none; }
            input:focus { border-color:#667eea; }
            button { width:100%; padding:14px; background:linear-gradient(135deg, #667eea, #764ba2); border:none;
                     border-radius:10px; color:#fff; font-size:16px; font-weight:600; cursor:pointer; }
            button:hover { opacity:0.9; }
            .error { color:#f87171; margin-bottom:16px; font-size:14px; display:none; }
          </style>
        </head>
        <body>
          <div class="card">
            <h1>🔐 Admin Login</h1>
            <div class="error" id="error"></div>
            <input type="text" id="username" placeholder="Admin Username" autocomplete="username">
            <input type="password" id="password" placeholder="Password" autocomplete="current-password">
            <button onclick="login()">Login</button>
          </div>
          <script>
            async function login() {
              const username = document.getElementById('username').value;
              const password = document.getElementById('password').value;
              const err = document.getElementById('error');
              if (!username || !password) { err.textContent='Fill in both fields'; err.style.display='block'; return; }
              try {
                const res = await fetch('/api/auth/login/username', {
                  method: 'POST',
                  headers: {'Content-Type':'application/json'},
                  body: JSON.stringify({username, password})
                });
                const data = await res.json();
                if (!res.ok) { err.textContent=data.error; err.style.display='block'; return; }
                if (!data.user.is_admin) { err.textContent='Not an admin account'; err.style.display='block'; return; }
                localStorage.setItem('token', data.token);
                window.location.href = '/admin/users';
              } catch(e) { err.textContent='Connection error'; err.style.display='block'; }
            }
          </script>
        </body>
        </html>
        """)


# ─── Upload Page HTML ─────────────────────────────

UPLOAD_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Upload Photo — StudyMate AI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           background: #0f0f1a; color:#e0e0e0; display:flex; align-items:center; justify-content:center;
           min-height:100vh; padding:20px; }
    .card { background:#1a1a2e; padding:40px; border-radius:16px; width:100%; max-width:450px; text-align:center; }
    h1 { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text;
         -webkit-text-fill-color: transparent; margin-bottom:8px; }
    .sub { color:#888; margin-bottom:24px; font-size:14px; }
    .preview { width:120px; height:120px; border-radius:50%; margin:0 auto 20px; background:#16213e;
              display:flex; align-items:center; justify-content:center; overflow:hidden;
              border:3px solid #667eea; }
    .preview img { width:100%; height:100%; object-fit:cover; }
    .preview .placeholder { color:#555; font-size:14px; }
    input[type="file"] { display:none; }
    .btn { display:inline-block; padding:14px 28px; margin:8px; border-radius:10px;
           font-size:16px; font-weight:600; cursor:pointer; border:none; }
    .btn-primary { background:linear-gradient(135deg, #667eea, #764ba2); color:#fff; }
    .btn-secondary { background:#16213e; color:#a78bfa; border:1px solid #2a2a4a; }
    .btn:disabled { opacity:0.5; cursor:not-allowed; }
    .status { margin-top:16px; padding:12px; border-radius:8px; display:none; }
    .status.success { display:block; background:#1a3a2e; color:#4ade80; border:1px solid #4ade80; }
    .status.error { display:block; background:#3a1a1a; color:#f87171; border:1px solid #f87171; }
    input[type="text"] { width:100%; padding:14px 16px; margin-bottom:16px; background:#16213e;
                         border:1px solid #2a2a4a; border-radius:10px; color:#fff; font-size:16px; outline:none; }
    input[type="text"]:focus { border-color:#667eea; }
  </style>
</head>
<body>
  <div class="card">
    <h1>📸 Upload Profile Photo</h1>
    <p class="sub">Take a photo or upload one — admin can see your face!</p>
    <div class="preview" id="preview">
      <span class="placeholder">No photo</span>
    </div>
    <input type="text" id="token" placeholder="Your Auth Token (from app settings)">
    <input type="file" id="fileInput" accept="image/*" capture="user">
    <div>
      <button class="btn btn-secondary" onclick="document.getElementById('fileInput').click()">Choose Photo</button>
      <button class="btn btn-primary" id="uploadBtn" onclick="upload()" disabled>Upload</button>
    </div>
    <div class="status" id="status"></div>
  </div>
  <script>
    document.getElementById('fileInput').addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(ev) {
        document.getElementById('preview').innerHTML = '<img src="' + ev.target.result + '">';
        document.getElementById('uploadBtn').disabled = false;
        window._imageData = ev.target.result;
      };
      reader.readAsDataURL(file);
    });
    async function upload() {
      const token = document.getElementById('token').value.trim();
      if (!token) { showStatus('Please enter your auth token', 'error'); return; }
      if (!window._imageData) { showStatus('Please select a photo first', 'error'); return; }
      document.getElementById('uploadBtn').disabled = true;
      document.getElementById('uploadBtn').textContent = 'Uploading...';
      try {
        const res = await fetch('/api/upload/photo', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token},
          body: JSON.stringify({image: window._imageData, format: 'jpg'})
        });
        const data = await res.json();
        if (res.ok) {
          showStatus('✅ Photo uploaded! Admin can see your face now.', 'success');
        } else {
          showStatus('❌ ' + (data.error || 'Upload failed'), 'error');
        }
      } catch(e) {
        showStatus('❌ Connection error: ' + e.message, 'error');
      }
      document.getElementById('uploadBtn').disabled = false;
      document.getElementById('uploadBtn').textContent = 'Upload';
    }
    function showStatus(msg, type) {
      const el = document.getElementById('status');
      el.textContent = msg;
      el.className = 'status ' + type;
    }
  </script>
</body>
</html>
"""

# ─── Admin Dashboard HTML (Main) ──────────────────

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>StudyMate AI — Server Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           background: #0f0f1a; color:#e0e0e0; min-height:100vh; display:flex; align-items:center; justify-content:center; }
    .container { max-width:800px; width:100%; padding:40px 20px; text-align:center; }
    h1 { font-size:2.5em; background: linear-gradient(135deg, #667eea, #764ba2);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom:8px; }
    .sub { color:#888; font-size:1.1em; margin-bottom:40px; }
    .cards { display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:20px; margin-bottom:40px; }
    .card { background:#1a1a2e; padding:30px 20px; border-radius:16px; text-decoration:none; color:inherit;
            transition:transform 0.2s, box-shadow 0.2s; }
    .card:hover { transform:translateY(-4px); box-shadow:0 8px 30px rgba(102,126,234,0.2); }
    .card .icon { font-size:2.5em; margin-bottom:12px; }
    .card .title { font-size:1.2em; font-weight:600; margin-bottom:4px; }
    .card .desc { color:#888; font-size:14px; }
    .card.primary { background:linear-gradient(135deg, #667eea, #764ba2); }
    .card.primary .desc { color:rgba(255,255,255,0.8); }
    .info { color:#666; font-size:14px; }
    .info a { color:#667eea; }
    .status-dot { display:inline-block; width:10px; height:10px; border-radius:50%; background:#4ade80; margin-right:6px; }
    @media (max-width:480px) {
      h1 { font-size:1.8em; }
      .cards { grid-template-columns:1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 StudyMate AI Server</h1>
    <p class="sub">Your personal backend — running locally, fully offline</p>
    <div class="cards">
      <a href="/admin/users" class="card primary">
        <div class="icon">📊</div>
        <div class="title">Admin Panel</div>
        <div class="desc">View all users, stats & activity</div>
      </a>
      <a href="/api/health" class="card">
        <div class="icon">💚</div>
        <div class="title">API Status</div>
        <div class="desc">Server health & connectivity check</div>
      </a>
      <a href="/upload" class="card">
        <div class="icon">📸</div>
        <div class="title">Upload Photo</div>
        <div class="desc">Upload your profile photo for admin to see</div>
      </a>
      <a href="/" class="card" target="_blank">
        <div class="icon">📱</div>
        <div class="title">Connect App</div>
        <div class="desc">Set app to <strong>YOUR_IP:8765</strong></div>
      </a>
    </div>
    <div class="info">
      <p><span class="status-dot"></span> Server running on port <strong>8765</strong></p>
      <p style="margin-top:8px;">📱 On your phone, open the app and set server to <code style="background:#1a1a2e;padding:2px 8px;border-radius:4px;">YOUR_COMPUTER_IP:8765</code></p>
      <p style="margin-top:16px;">🔗 <a href="https://rushikesh-001.github.io/suzume-showcase/official/">Visit Suzume Showcase</a></p>
    </div>
  </div>
</body>
</html>
"""

# ─── Server Entry ──────────────────────────────────

def run_server():
    init_db()

    # Create default admin if not exists
    conn = get_db()
    admin = conn.execute("SELECT uid FROM users WHERE username = 'admin'").fetchone()
    if not admin:
        uid = generate_uid()
        now = now_iso()
        pw = hash_password("admin123")
        conn.execute("""INSERT INTO users (uid, email, username, display_name, password_hash, is_admin, created_at, last_active)
                        VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
                     (uid, "admin@studymate.local", "admin", "Admin", pw, now, now))
        conn.commit()
        print("✓ Default admin created: username='admin' password='admin123'")
    conn.close()

    # Get local IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    server = HTTPServer((HOST, PORT), StudyMateHandler)
    print(f"""
╔══════════════════════════════════════════════════════╗
║             🚀 StudyMate AI Server                   ║
╠══════════════════════════════════════════════════════╣
║  Admin Dashboard: http://{local_ip}:{PORT}/admin            ║
║  API Health:      http://{local_ip}:{PORT}/api/health       ║
║  Admin Login:     http://{local_ip}:{PORT}/admin/login      ║
║                                                      ║
║  📱 On your phone, set server IP to:                 ║
║     {local_ip}:{PORT}                               ║
║                                                      ║
║  🔑 Admin Login: username='admin' password='admin123'║
║  📁 Database: {DB_PATH}            ║
╚══════════════════════════════════════════════════════╝
    """)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
