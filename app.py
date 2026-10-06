from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gd_pulse_secret_key_2025")

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

# ---------- Tools ----------

@app.route("/tools/gst")
def gst_tool():
    return render_template("gst.html")

@app.route("/tools/emi")
def emi_tool():
    return render_template("emi.html")

@app.route("/tools/image-resize")
def image_resize_tool():
    return render_template("image-resize.html")

@app.route("/tools/image-resize/process", methods=["POST"])
def image_resize_process():
    try:
        file = request.files.get("image")
        if not file or file.filename == "":
            return "Koi image select nahi ki", 400

        width = int(request.form.get("width", 0))
        height = int(request.form.get("height", 0))
        if width <= 0 or height <= 0:
            return "Sahi width/height daalo", 400

        # Image kholo
        img = Image.open(file.stream)

        # Resize karo
        resized = img.resize((width, height), Image.LANCZOS)

        # Output buffer me save karo
        output = io.BytesIO()
        fmt = img.format if img.format else "PNG"
        if fmt not in ("JPEG", "PNG", "WEBP", "GIF", "BMP"):
            fmt = "PNG"
        if fmt == "JPEG" and resized.mode in ("RGBA", "P"):
            resized = resized.convert("RGB")
        resized.save(output, format=fmt)
        output.seek(0)

        # Original filename ka extension nikalo
        original_name = file.filename
        base = os.path.splitext(original_name)[0]
        ext = fmt.lower() if fmt != "JPEG" else "jpg"
        download_name = f"{base}_{width}x{height}.{ext}"

        return send_file(
            output,
            mimetype=f"image/{ext}",
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return f"Error: {str(e)}", 500

# ---------- Run ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
