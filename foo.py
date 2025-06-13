# Please review the provided Flask code that implements two endpoints /user/{user_id} (GET) 
# and /user (POST), which interact with an SQLite database and send audit logs to an external 
# service.
# Your task is to write unit test cases for these endpoints, focusing on:
# - Testing the success and failure scenarios for both endpoints.
# - Mocking the database interactions so the tests do not depend on a real database.
# - Mocking the external audit log HTTP requests to avoid real network calls.
# - Validating that audit logs are sent appropriately when endpoints are called.
# You can use any testing framework and mocking tools you prefer. Please provide example test 
# functions that cover the main behaviors.

from datetime import datetime
from flask import Flask, request, jsonify, abort
import sqlite3
import json
import requests

# SQLite database file name.
# The database is assumed to already exist and contains the following table:
#
# +----------------------+
# |       users          |
# +----------------------+
# | id   : INTEGER       | <--- Primary Key, AUTOINCREMENT
# | name : TEXT NOT NULL |
# +----------------------+
#
# Note: Treat the database as a black box (external service); we focus on API logic here.

DB_NAME = "users.db"

# The external audit log service endpoint
AUDIT_LOG_URL = "https://example.com/audit"

# Initialize FastAPI application
app = Flask(__name__)


def send_audit_log(action: str, detail: dict):
    """Send an audit log entry to an external audit service.

    Args:
        action (str): The action being logged (e.g., "GET_USER", "CREATE_USER").
        detail (dict): Additional details about the action.

    Returns:
        None
    """
    ...
    try:
        payload = {
            "action": action,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        }
        # Sends a POST request to the audit service
        requests.post(AUDIT_LOG_URL, json=payload)
    except Exception as e:
        # Logging failure for debug purposes only; does not affect API response
        print(f"[Audit log failed] {e}")

# GET /user/{user_id}
# Fetch a user by ID and log the access action


@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """Retrieve a user by their ID from the database.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        dict: A dictionary containing user information with keys 'id' and 'name'.

    Raises:
        HTTPException: If the user is not found (404).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        user = {"id": row[0], "name": row[1]}
        send_audit_log("GET_USER", user)  # Audit the GET action
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404


@app.route("/user", methods=["POST"])
def create_user():
    """Create a new user based on JSON payload from the request.

    Args:
        request (Request): The incoming FastAPI HTTP request.

    Returns:
        dict: A dictionary containing the created user's 'id' and 'name'.

    Raises:
        HTTPException: If the input data is invalid (400).
    """
    try:
        data = request.get_json(force=True)
        name = data["name"]
    except (KeyError, json.JSONDecodeError):
        return jsonify({"message": "Invalid input"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    result = {"id": user_id, "name": name}
    send_audit_log("CREATE_USER", result)  # Audit the CREATE action
    return jsonify(result), 201


if __name__ == "__main__":
    app.run(debug=True)
