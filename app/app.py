"""
QA Practice App — UI + REST API + SQLite.

Run:
    python -m app.app
Open:
    http://127.0.0.1:5000/
"""

from __future__ import annotations

from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app import db

app = Flask(__name__)
app.secret_key = "qa-practice-secret-key-change-me"

ALLOWED_STATUSES = {"open", "in_progress", "done"}


def create_app() -> Flask:
    db.init_db()
    return app


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def api_auth_required(view):
    """Simple API auth via X-API-Key header (username:password base style key).

    For learning: send header  X-API-Key: admin:admin123
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        api_key = request.headers.get("X-API-Key", "")
        if ":" not in api_key:
            return jsonify({"error": "Missing or invalid X-API-Key header"}), 401
        username, password = api_key.split(":", 1)
        user = db.get_user_by_credentials(username.strip(), password)
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        request.api_user = user  # type: ignore[attr-defined]
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# UI routes
# ---------------------------------------------------------------------------


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html"), 400

        user = db.get_user_by_credentials(username, password)
        if not user:
            flash("Invalid username or password.", "error")
            return render_template("login.html"), 401

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["display_name"] = user["display_name"]
        flash(f"Welcome, {user['display_name']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    tasks = db.list_tasks(session["user_id"])
    return render_template(
        "dashboard.html",
        username=session["username"],
        display_name=session["display_name"],
        tasks=tasks,
    )


@app.route("/tasks/new", methods=["GET", "POST"])
@login_required
def new_task():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        status = (request.form.get("status") or "open").strip()

        if not title:
            flash("Title is required.", "error")
            return render_template(
                "task_form.html",
                username=session["username"],
                display_name=session["display_name"],
            ), 400

        if status not in ALLOWED_STATUSES:
            flash("Invalid status.", "error")
            return render_template(
                "task_form.html",
                username=session["username"],
                display_name=session["display_name"],
            ), 400

        task_id = db.create_task(session["user_id"], title, description, status)
        flash(f"Task #{task_id} created successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "task_form.html",
        username=session["username"],
        display_name=session["display_name"],
    )


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
@login_required
def update_status(task_id: int):
    status = (request.form.get("status") or "").strip()
    task = db.get_task(task_id)

    if not task or task["user_id"] != session["user_id"]:
        flash("Task not found.", "error")
        return redirect(url_for("dashboard"))

    if status not in ALLOWED_STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("dashboard"))

    db.update_task_status(task_id, status)
    flash(f"Task #{task_id} updated to {status}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task_ui(task_id: int):
    task = db.get_task(task_id)
    if not task or task["user_id"] != session["user_id"]:
        flash("Task not found.", "error")
        return redirect(url_for("dashboard"))

    db.delete_task(task_id)
    flash(f"Task #{task_id} deleted.", "success")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# API routes  (prefix: /api)
# ---------------------------------------------------------------------------


@app.get("/api/health")
def api_health():
    return jsonify({"status": "ok", "service": "qa-practice-app"})


@app.post("/api/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = db.get_user_by_credentials(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify(
        {
            "message": "login successful",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "display_name": user["display_name"],
            },
            "api_key": f"{username}:{password}",
        }
    )


@app.get("/api/tasks")
@api_auth_required
def api_list_tasks():
    mine_only = request.args.get("mine", "true").lower() != "false"
    user = request.api_user  # type: ignore[attr-defined]
    rows = db.list_tasks(user["id"] if mine_only else None)
    return jsonify({"tasks": [db.row_to_task_dict(r) for r in rows]})


@app.get("/api/tasks/<int:task_id>")
@api_auth_required
def api_get_task(task_id: int):
    task = db.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task": db.row_to_task_dict(task)})


@app.post("/api/tasks")
@api_auth_required
def api_create_task():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip()
    status = (payload.get("status") or "open").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400
    if status not in ALLOWED_STATUSES:
        return jsonify({"error": f"status must be one of {sorted(ALLOWED_STATUSES)}"}), 400

    user = request.api_user  # type: ignore[attr-defined]
    task_id = db.create_task(user["id"], title, description, status)
    task = db.get_task(task_id)
    return jsonify({"message": "created", "task": db.row_to_task_dict(task)}), 201


@app.patch("/api/tasks/<int:task_id>")
@api_auth_required
def api_update_task(task_id: int):
    task = db.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    payload = request.get_json(silent=True) or {}
    status = (payload.get("status") or "").strip()
    if status not in ALLOWED_STATUSES:
        return jsonify({"error": f"status must be one of {sorted(ALLOWED_STATUSES)}"}), 400

    db.update_task_status(task_id, status)
    updated = db.get_task(task_id)
    return jsonify({"message": "updated", "task": db.row_to_task_dict(updated)})


@app.delete("/api/tasks/<int:task_id>")
@api_auth_required
def api_delete_task(task_id: int):
    if not db.get_task(task_id):
        return jsonify({"error": "Task not found"}), 404
    db.delete_task(task_id)
    return jsonify({"message": "deleted", "id": task_id})


@app.get("/api/db/tasks/<int:task_id>")
@api_auth_required
def api_db_lookup(task_id: int):
    """Convenience endpoint that mirrors a direct DB read — useful while learning.

    In real projects you would query SQLite/Postgres from your test code instead.
    """
    task = db.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found", "exists_in_db": False}), 404
    return jsonify({"exists_in_db": True, "task": db.row_to_task_dict(task)})


# Ensure DB exists when module is imported / run
create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
