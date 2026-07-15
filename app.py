"""
Task Management App - Flask Backend
------------------------------------
Handles:
  - Admin login/logout (session based)
  - Serving the login page and task dashboard page
  - REST API for tasks: list, create, delete (connected to MySQL)

Run:
    pip install -r requirements.txt
    python app.py

Make sure MySQL is running and database.sql has been imported first.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"  # needed for sessions

# ---------------------------------------------------------
# Database configuration - update these to match your setup
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "task_manager"
}


def get_db_connection():
    """Create and return a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def login_required(func):
    """Simple decorator to protect routes that need an authenticated admin."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------
# Page routes
# ---------------------------------------------------------

@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect(url_for("tasks_page"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM admin WHERE username = %s AND password = %s",
                (username, password)
            )
            admin_user = cursor.fetchone()
            cursor.close()
            conn.close()

            if admin_user:
                session["logged_in"] = True
                session["username"] = admin_user["username"]
                return redirect(url_for("tasks_page"))
            else:
                error = "Invalid username or password."
        except Error as e:
            error = f"Database error: {e}"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/tasks")
@login_required
def tasks_page():
    return render_template("tasks.html", username=session.get("username"))


# ---------------------------------------------------------
# API routes (used by script.js via fetch)
# ---------------------------------------------------------

@app.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "tasks": tasks})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/tasks", methods=["POST"])
@login_required
def add_task():
    data = request.get_json()

    employee_id = data.get("employee_id", "").strip()
    employee_name = data.get("employee_name", "").strip()
    task_title = data.get("task_title", "").strip()
    completed = data.get("completed", "No")

    if not employee_id or not employee_name or not task_title:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if completed not in ("Yes", "No"):
        completed = "No"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (employee_id, employee_name, task_title, completed)
               VALUES (%s, %s, %s, %s)""",
            (employee_id, employee_name, task_title, completed)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Task added.", "id": new_id})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    data = request.get_json()

    employee_id = data.get("employee_id", "").strip()
    employee_name = data.get("employee_name", "").strip()
    task_title = data.get("task_title", "").strip()
    completed = data.get("completed", "No")

    if not employee_id or not employee_name or not task_title:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if completed not in ("Yes", "No"):
        completed = "No"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE tasks
               SET employee_id = %s, employee_name = %s, task_title = %s, completed = %s
               WHERE id = %s""",
            (employee_id, employee_name, task_title, completed, task_id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"success": False, "message": "Task not found."}), 404
        return jsonify({"success": True, "message": "Task updated."})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"success": False, "message": "Task not found."}), 404
        return jsonify({"success": True, "message": "Task deleted."})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
