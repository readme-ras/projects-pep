"""
NEXUS CHAT — Flask Backend
Uses Server-Sent Events (SSE) for real-time push (server→client).
Zero extra dependencies beyond Flask (already installed).
"""

import time
import json
import threading
import queue as stdlib_queue
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, Response, stream_with_context
from core.engine import engine
from core.data_structures import HashMap

app = Flask(__name__)

# ─────────────────────────────────────────────
# SSE CONNECTION MANAGER
# ─────────────────────────────────────────────
class SSEManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._room_clients = {}  # room_id -> list of (username, queue)

    def subscribe(self, room_id, username):
        q = stdlib_queue.Queue(maxsize=100)
        with self._lock:
            if room_id not in self._room_clients:
                self._room_clients[room_id] = []
            self._room_clients[room_id].append((username, q))
        return q

    def unsubscribe(self, room_id, username, q):
        with self._lock:
            clients = self._room_clients.get(room_id, [])
            try:
                clients.remove((username, q))
            except ValueError:
                pass

    def broadcast(self, room_id, event_data, exclude=None):
        payload = f"data: {json.dumps(event_data)}\n\n"
        with self._lock:
            clients = list(self._room_clients.get(room_id, []))
        dead = []
        for (uname, q) in clients:
            if uname == exclude:
                continue
            try:
                q.put_nowait(payload)
            except stdlib_queue.Full:
                dead.append((uname, q))
        if dead:
            with self._lock:
                for item in dead:
                    try:
                        self._room_clients.get(room_id, []).remove(item)
                    except ValueError:
                        pass

sse = SSEManager()

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

@app.route("/api/<path:path>", methods=["OPTIONS"])
@app.route("/sse/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    return "", 204

# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────
def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return engine.get_user_by_token(auth.split(" ", 1)[1])

def require_user():
    user = get_current_user()
    if not user:
        return None, jsonify({"error": "Unauthorized"}), 401
    return user, None, None

# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    result = engine.register(data.get("username",""), data.get("password",""), data.get("display_name",""))
    return jsonify(result), (400 if not result["ok"] else 200)

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    result = engine.login(data.get("username",""), data.get("password",""))
    return jsonify(result), (401 if not result["ok"] else 200)

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    auth = request.headers.get("Authorization","")
    if auth.startswith("Bearer "):
        engine.logout(auth.split(" ",1)[1])
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
# USER ROUTES
# ─────────────────────────────────────────────
@app.route("/api/users/online")
def online_users():
    user, err, code = require_user()
    if err: return err, code
    usernames = engine.get_online_users()
    users = [engine.users_map.get(u).to_dict() for u in usernames if engine.users_map.get(u)]
    return jsonify({"users": users})

@app.route("/api/users/notifications")
def get_notifications():
    user, err, code = require_user()
    if err: return err, code
    return jsonify({"notifications": engine.get_notifications(user.username)})

@app.route("/api/stats")
def stats():
    return jsonify(engine.stats())

# ─────────────────────────────────────────────
# ROOM ROUTES
# ─────────────────────────────────────────────
@app.route("/api/rooms")
def list_rooms():
    user, err, code = require_user()
    if err: return err, code
    return jsonify({"rooms": engine.get_all_rooms()})

@app.route("/api/rooms", methods=["POST"])
def create_room():
    user, err, code = require_user()
    if err: return err, code
    data = request.json or {}
    return jsonify(engine.create_room(data.get("name",""), data.get("description",""), user.username))

@app.route("/api/rooms/<room_id>/join", methods=["POST"])
def join_room(room_id):
    user, err, code = require_user()
    if err: return err, code
    result = engine.join_room(room_id, user.username)
    return jsonify(result), (404 if not result["ok"] else 200)

@app.route("/api/rooms/<room_id>/leave", methods=["POST"])
def leave_room(room_id):
    user, err, code = require_user()
    if err: return err, code
    engine.leave_room(room_id, user.username)
    return jsonify({"ok": True})

@app.route("/api/rooms/<room_id>/participants")
def get_participants(room_id):
    user, err, code = require_user()
    if err: return err, code
    return jsonify({"participants": engine.get_room_participants(room_id)})

# ─────────────────────────────────────────────
# MESSAGE ROUTES
# ─────────────────────────────────────────────
@app.route("/api/rooms/<room_id>/messages")
def get_messages(room_id):
    user, err, code = require_user()
    if err: return err, code
    page = int(request.args.get("page", 1))
    result = engine.get_messages(room_id, page=page)
    return jsonify(result), (404 if not result["ok"] else 200)

@app.route("/api/rooms/<room_id>/messages", methods=["POST"])
def send_message(room_id):
    user, err, code = require_user()
    if err: return err, code
    data = request.json or {}
    result = engine.send_message(room_id, user.username, data.get("content",""), data.get("msg_type","text"))
    if not result["ok"]: return jsonify(result), 400
    msg = result["message"]
    msg["avatar_color"] = user.avatar_color
    sse.broadcast(room_id, {"type": "new_message", "message": msg})
    return jsonify(result)

@app.route("/api/rooms/<room_id>/messages/undo", methods=["DELETE"])
def undo_message(room_id):
    user, err, code = require_user()
    if err: return err, code
    result = engine.undo_last_message(room_id, user.username)
    if not result["ok"]: return jsonify(result), 400
    sse.broadcast(room_id, {"type": "message_deleted", "message_id": result["message_id"]})
    return jsonify(result)

@app.route("/api/rooms/<room_id>/search")
def search_messages(room_id):
    user, err, code = require_user()
    if err: return err, code
    return jsonify(engine.search_messages(room_id, request.args.get("q","")))

# ─────────────────────────────────────────────
# SSE ENDPOINT — real-time event stream
# ─────────────────────────────────────────────
@app.route("/sse/<room_id>")
def sse_stream(room_id):
    token = request.args.get("token","")
    user = engine.get_user_by_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    username = user.username
    engine.set_online(username)
    engine.join_room(room_id, username)
    q = sse.subscribe(room_id, username)

    sse.broadcast(room_id, {
        "type": "user_joined",
        "username": username,
        "display_name": user.display_name,
        "avatar_color": user.avatar_color,
    }, exclude=username)

    def generate():
        yield f"data: {json.dumps({'type': 'connected', 'username': username})}\n\n"
        try:
            while True:
                try:
                    msg = q.get(timeout=25)
                    yield msg
                except stdlib_queue.Empty:
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except GeneratorExit:
            pass
        finally:
            sse.unsubscribe(room_id, username, q)
            engine.set_offline(username)
            sse.broadcast(room_id, {"type": "user_left", "username": username})

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

@app.route("/sse/<room_id>/typing", methods=["POST"])
def typing_event(room_id):
    auth = request.headers.get("Authorization","")
    if auth.startswith("Bearer "):
        user = engine.get_user_by_token(auth.split(" ",1)[1])
        if user:
            data = request.json or {}
            sse.broadcast(room_id, {
                "type": "typing",
                "username": user.username,
                "is_typing": data.get("is_typing", False),
            }, exclude=user.username)
    return "", 204

if __name__ == "__main__":
    print("⚡ Nexus Chat running on http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, threaded=True, debug=False)
