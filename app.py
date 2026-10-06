from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "gd_pulse_secret_key_2025"  # ise baad me change kar sakte ho

# Hardcoded users (abhi ke liye)
USERS = {
    "admin": {"password": "gdadmin123", "role": "admin"},
    "user":  {"password": "user123",    "role": "public"}
}

# ---------- Routes ----------

@app.route("/")
def dashboard():
    return render_template("dashboard.html", user=session.get("user"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            session["role"] = USERS[username]["role"]
            if USERS[username]["role"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))
        else:
            error = "Galat username ya password"

    return render_template("login.html", error=error)

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", user=session.get("user"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("dashboard"))

# ---------- Run ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
