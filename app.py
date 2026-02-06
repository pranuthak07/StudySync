from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "studysync_secret"


# ---------- CREATE DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # Tasks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            due_date TEXT
        )
    """)

    # Study sessions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        minutes INTEGER,
        date TEXT
    )
""")


    conn.commit()
    conn.close()


init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?",
                    (email,password))
        user = cur.fetchone()
        conn.close()

        if user:
         session["user"] = user[1]   # store user name
         return redirect(url_for("dashboard"))

        else:
            return "Invalid email or password"

    return render_template("login.html")


# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                    (name,email,password))
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # get tasks
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    task_count = len(tasks)

    # get total study minutes
    cur.execute("SELECT SUM(minutes) FROM study_sessions")
    result = cur.fetchone()[0]
    if result is None:
        result = 0
    hours = round(result / 60, 1)

    # get streak (unique study days)
    cur.execute("SELECT COUNT(DISTINCT date) FROM study_sessions")
    streak = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        hours=hours,
        task_count=task_count,
        streak=streak,
        username=session["user"]
    )



# ---------- ADD TASK ----------
@app.route("/add_task", methods=["POST"])
def add_task():
    title = request.form["title"]
    due_date = request.form["due_date"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, due_date) VALUES (?,?)",
                (title, due_date))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))
# ---------- DELETE TASK ----------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
# ---------- SAVE STUDY SESSION ----------
@app.route("/save_session")
def save_session():
    today = date.today().isoformat()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO study_sessions (minutes, date) VALUES (?,?)",
                (25, today))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
