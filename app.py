import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# Initialize SQLite database
def init_db():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pebbles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


# Route to serve the frontend website
@app.route("/")
def index():
  return render_template("index.html")


# API Endpoint: Get all saved pebbles
@app.route("/api/pebbles", methods=["GET"])
def get_pebbles():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, message FROM pebbles ORDER BY id DESC")
  rows = cursor.fetchall()
  conn.close()

  pebbles = [{"id": row[0], "message": row[1]} for row in rows]
  return jsonify(pebbles)


# API Endpoint: Add a new pebble
@app.route("/api/pebbles", methods=["POST"])
def add_pebble():
  data = request.get_json()
  message = data.get("message", "").strip()

  if not message:
    return jsonify({"error": "Message cannot be empty"}), 400

  if len(message) > 100:
    return jsonify({"error": "Message is too long (max 100 chars)"}), 400

  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("INSERT INTO pebbles (message) VALUES (?)", (message,))
  conn.commit()
  conn.close()

  return jsonify({"success": True, "message": message}), 201


if __name__ == "__main__":
  app.run(debug=True)