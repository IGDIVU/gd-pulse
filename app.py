from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gd_pulse_secret_key_2025")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB max upload

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

        img = Image.open(file.stream)
        resized = img.resize((width, height), Image.LANCZOS)

        output = io.BytesIO()
        fmt = img.format if img.format else "PNG"
        if fmt not in ("JPEG", "PNG", "WEBP", "GIF", "BMP"):
            fmt = "PNG"
        if fmt == "JPEG" and resized.mode in ("RGBA", "P"):
            resized = resized.convert("RGB")
        resized.save(output, format=fmt)
        output.seek(0)

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

@app.route("/tools/photo-to-pdf")
def photo_to_pdf_tool():
    return render_template("photo-to-pdf.html")

@app.route("/tools/photo-to-pdf/process", methods=["POST"])
def photo_to_pdf_process():
    try:
        files = request.files.getlist("images")
        files = [f for f in files if f and f.filename != ""]

        if not files:
            return "Koi image select nahi ki", 400

        images = []
        for f in files:
            img = Image.open(f.stream)
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)

        first = images[0]
        rest = images[1:]

        output = io.BytesIO()
        first.save(output, format="PDF", save_all=True, append_images=rest)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="gd-pulse-images.pdf"
        )

    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/tools/video-to-mp3")
def video_to_mp3_tool():
    return render_template("video-to-mp3.html")

@app.route("/tools/video-to-mp3/process", methods=["POST"])
def video_to_mp3_process():
    try:
        file = request.files.get("video")
        if not file or file.filename == "":
            return "Koi video select nahi ki", 400

        # Video ko temp me save karo
        temp_dir = "/tmp"
        input_path = os.path.join(temp_dir, "input_video")
        output_path = os.path.join(temp_dir, "output_audio.mp3")

        file.save(input_path)

        # MoviePy se audio extract karo
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(input_path)
        clip.audio.write_audiofile(output_path, codec="mp3", verbose=False, logger=None)
        clip.close()

        # MP3 file bhejo
        original_name = os.path.splitext(file.filename)[0]
        download_name = f"{original_name}.mp3"

        return send_file(
            output_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return f"Error: {str(e)}", 500

# ---------- Error Handler ----------

@app.errorhandler(413)
def too_large(e):
    return "File bahut badi hai. Max 25MB allowed hai.", 413

# ---------- Run ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
