import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_for_mood_pebble"


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
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER NOT NULL,
            role TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


@app.route("/")
def index():
  if "user_email" not in session:
    return redirect(url_for("login"))
  return render_template(
      "index.html", username=session["username"], role=session.get("role")
  )


@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    age = request.form.get("age", "").strip()

    if not username or not email or not password or not age:
      return render_template(
          "register.html", error="All fields are required!"
      )

    # Change this email to YOUR exact email address to make yourself the exclusive admin!
    admin_email = "jyothsna@admin.com"
    role = "admin" if email.lower() == admin_email.lower() else "user"
    hashed_password = generate_password_hash(password)

    try:
      conn = sqlite3.connect("database.db")
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO users (username, email, password, age, role) VALUES"
          " (?, ?, ?, ?, ?)",
          (username, email, hashed_password, int(age), role),
      )
      conn.commit()
      conn.close()
      return redirect(url_for("login"))
    except sqlite3.IntegrityError:
      return render_template("register.html", error="Email already registered!")

  return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, password, role, age FROM users WHERE email"
        " = ?",
        (email,),
    )
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
      session["user_id"] = user[0]
      session["username"] = user[1]
      session["user_email"] = user[2]
      session["role"] = user[4]
      session["age"] = user[5]

      if session["role"] == "admin":
        return redirect(url_for("admin"))
      return redirect(url_for("index"))
    else:
      return render_template("login.html", error="Invalid email or password!")

  return render_template("login.html")


@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))


@app.route("/admin")
def admin():
  if session.get("role") != "admin":
    return "Access Denied! Admin privileges required.", 403

  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, username, email, age, role FROM users")
  users = cursor.fetchall()
  conn.close()

  return render_template(
      "admin.html", users=users, username=session["username"]
  )


@app.route("/api/pebbles", methods=["GET"])
def get_pebbles():
  if "user_email" not in session:
    return jsonify({"error": "Unauthorized"}), 401

  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, message FROM pebbles ORDER BY id DESC")
  rows = cursor.fetchall()
  conn.close()
  return jsonify([{"id": row[0], "message": row[1]} for row in rows])


@app.route("/api/pebbles", methods=["POST"])
def add_pebble():
  if "user_email" not in session:
    return jsonify({"error": "Unauthorized"}), 401

  data = request.get_json()
  message = data.get("message", "").strip()
  if not message:
    return jsonify({"error": "Message cannot be empty"}), 400

  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("INSERT INTO pebbles (message) VALUES (?)", (message,))
  conn.commit()
  conn.close()
  return jsonify({"success": True, "message": message}), 201


if __name__ == "__main__":
  app.run(debug=True)
  