import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from functools import wraps
from flask import request, jsonify

ADMIN_TOKEN = "change_this_to_a_secret_key"

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-ADMIN-TOKEN")
        if token != ADMIN_TOKEN:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return wrapper

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, 'static', 'uploads')
DB_PATH     = os.path.join(BASE_DIR, 'rixsolve.db')
MAX_MB      = 500
ALLOWED_EXT = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'm4v'}

app.config['MAX_CONTENT_LENGTH'] = MAX_MB * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Database ─────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS videos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                filename   TEXT NOT NULL,
                mimetype   TEXT,
                size       INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS comments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id   INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
                name       TEXT NOT NULL DEFAULT 'Anonymous',
                text       TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)


init_db()


# ── Helpers ───────────────────────────────────────────────────────────
def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def fmt_size(b):
    if b is None:
        return ''
    if b >= 1_048_576:
        return f"{b/1_048_576:.1f} MB"
    return f"{b/1024:.0f} KB"


def row_to_dict(row):
    return dict(row) if row else None


# ── Frontend ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── Video API ─────────────────────────────────────────────────────────
@app.route('/api/videos', methods=['GET'])
def get_videos():
    with get_db() as db:
        rows = db.execute("""
            SELECT v.*, COUNT(c.id) as comment_count
            FROM videos v
            LEFT JOIN comments c ON c.video_id = v.id
            GROUP BY v.id
            ORDER BY v.created_at DESC
        """).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/videos/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    ext      = file.filename.rsplit('.', 1)[1].lower()
    safe     = secure_filename(file.filename)
    unique   = f"{int(datetime.now().timestamp()*1000)}_{safe}"
    savepath = os.path.join(UPLOAD_DIR, unique)
    file.save(savepath)
    size = os.path.getsize(savepath)

    title = request.form.get('title') or file.filename.rsplit('.', 1)[0]

    with get_db() as db:
        cur = db.execute(
            "INSERT INTO videos (title, filename, mimetype, size) VALUES (?, ?, ?, ?)",
            (title, unique, file.content_type, size)
        )
        video = db.execute("SELECT * FROM videos WHERE id = ?", (cur.lastrowid,)).fetchone()

    return jsonify(dict(video)), 201


@app.route('/api/videos/<int:vid_id>', methods=['DELETE'])
@admin_required
def delete_video(vid_id):
    with get_db() as db:
        video = db.execute("SELECT * FROM videos WHERE id = ?", (vid_id,)).fetchone()
        if not video:
            return jsonify({'error': 'Not found'}), 404
        filepath = os.path.join(UPLOAD_DIR, video['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        db.execute("DELETE FROM videos WHERE id = ?", (vid_id,))
    return jsonify({'message': 'Deleted'})


# ── Comment API ───────────────────────────────────────────────────────
@app.route('/api/videos/<int:vid_id>/comments', methods=['GET'])
def get_comments(vid_id):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM comments WHERE video_id = ? ORDER BY created_at ASC", (vid_id,)
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/videos/<int:vid_id>/comments', methods=['POST'])
def add_comment(vid_id):
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()
    name = (data.get('name') or 'Anonymous').strip()
    if not text:
        return jsonify({'error': 'Comment text required'}), 400
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO comments (video_id, name, text) VALUES (?, ?, ?)", (vid_id, name, text)
        )
        comment = db.execute("SELECT * FROM comments WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(comment)), 201


@app.route('/api/comments/<int:cid>', methods=['DELETE'])
@admin_required
def delete_comment(cid):
    with get_db() as db:
        db.execute("DELETE FROM comments WHERE id = ?", (cid,))
    return jsonify({'message': 'Deleted'})


# ── Serve uploads ─────────────────────────────────────────────────────
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ── Run ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
