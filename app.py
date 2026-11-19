import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS count FROM applications")
    total = cursor.fetchone()["count"]
    cursor.close()
    conn.close()
    return render_template("dashboard.html", total=total)


if __name__ == "__main__":
    app.run(debug=True)