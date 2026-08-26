import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = (
    "super_secret_key_for_mood_pebble"  # Required for secure login sessions
)


# Initialize SQLite database (Pebbles & Users)
def init_db():
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pebbles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


# Route: Home Page
@app.route("/")
def index():
  if "username" not in session:
    return redirect(url_for("login"))
  return render_template(
      "index.html", username=session["username"], role=session.get("role")
  )


# Route: Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
      return render_template("register.html", error="All fields are required!")

    # Set role to 'admin' ONLY if it matches your secret admin username, otherwise 'user'
    # CHANGE 'my_admin_name' to whatever username you want for yourself!
    role = "admin" if username == "my_admin_name" else "user"
    hashed_password = generate_password_hash(password)

    try:
      conn = sqlite3.connect("database.db")
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
          (username, hashed_password, role),
      )
      conn.commit()
      conn.close()
      return redirect(url_for("login"))
    except sqlite3.IntegrityError:
      return render_template("register.html", error="Username already exists!")

  return render_template("register.html")


# Route: Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password, role FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
      session["user_id"] = user[0]
      session["username"] = user[1]
      session["role"] = user[3]
      return redirect(url_for("index"))
    else:
      return render_template(
          "login.html", error="Invalid username or password!"
      )

  return render_template("login.html")


# Route: Logout
@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))


# Route: Protected Admin Dashboard (Only accessible by you)
@app.route("/admin")
def admin():
  if session.get("role") != "admin":
    return "Access Denied! You are not authorized to view this page.", 403

  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, username, role FROM users")
  users = cursor.fetchall()
  conn.close()

  return render_template("admin.html", users=users, username=session["username"])


# API Endpoint: Get all saved pebbles
@app.route("/api/pebbles", methods=["GET"])
def get_pebbles():
  if "username" not in session:
    return jsonify({"error": "Unauthorized"}), 401

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
  if "username" not in session:
    return jsonify({"error": "Unauthorized"}), 401

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