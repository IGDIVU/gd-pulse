from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gd_pulse_secret_key_2025")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB

# ---------- Users ----------
USERS = {
    "admin": {"password": "gdadmin123", "role": "admin"},
    "staff": {"password": "gdstaff123", "role": "staff"},
}

# ---------- Helpers ----------
def current_user():
    return session.get("user")

def current_role():
    return session.get("role")

def require_staff():
    return current_role() in ("staff", "admin")

def require_admin():
    return current_role() == "admin"

# ---------- Auto-Inject animations.js ----------
@app.after_request
def inject_animations(response):
    if (
        response.content_type
        and "text/html" in response.content_type
        and response.status_code == 200
    ):
        try:
            html = response.get_data(as_text=True)
            if "animations.js" not in html and "</body>" in html:
                script_tag = '  <script src="/static/animations.js"></script>\n</body>'
                html = html.replace("</body>", script_tag, 1)
                response.set_data(html)
        except Exception:
            pass
    return response

# ---------- Public Routes ----------

@app.route("/")
def portfolio():
    return render_template("portfolio.html", user=current_user())

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
            else:
                return redirect(url_for("tools"))
        else:
            error = "Galat username ya password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("portfolio"))

# ---------- Staff Routes ----------

@app.route("/tools")
def tools():
    if not require_staff():
        return redirect(url_for("login"))
    return render_template("tools.html", user=current_user(), role=current_role())

# ---------- Admin Routes ----------

@app.route("/admin")
def admin():
    if not require_admin():
        return redirect(url_for("login"))
    return render_template("admin.html", user=current_user())

# ============================================
# OFFICE TOOLS
# ============================================

@app.route("/tools/gst")
def gst_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("gst.html")

@app.route("/tools/emi")
def emi_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("emi.html")

@app.route("/tools/age")
def age_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("age.html")

@app.route("/tools/number-to-words")
def number_to_words_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("number-to-words.html")

@app.route("/tools/unit-converter")
def unit_converter_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("unit-converter.html")

@app.route("/tools/text-tools")
def text_tools():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("text-tools.html")

# ---------- QR Code ----------

@app.route("/tools/qr-code")
def qr_code_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("qr-code.html")

@app.route("/tools/qr-code/process", methods=["POST"])
def qr_code_process():
    try:
        import qrcode
        text = request.form.get("text", "").strip()
        size = int(request.form.get("size", 300))
        if not text:
            return "Kuch text daalo", 400
        if size < 100 or size > 1000:
            size = 300

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1a1a1a", back_color="white").convert("RGB")
        img = img.resize((size, size), Image.LANCZOS)

        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)

        return send_file(output, mimetype="image/png", as_attachment=True,
                         download_name="gd-pulse-qr.png")
    except Exception as e:
        return f"Error: {str(e)}", 500

# ---------- Image Tools ----------

@app.route("/tools/image-resize")
def image_resize_tool():
    if not require_staff(): return redirect(url_for("login"))
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
        base = os.path.splitext(file.filename)[0]
        ext = fmt.lower() if fmt != "JPEG" else "jpg"
        return send_file(output, mimetype=f"image/{ext}", as_attachment=True,
                         download_name=f"{base}_{width}x{height}.{ext}")
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/tools/image-compress")
def image_compress_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("image-compress.html")

@app.route("/tools/image-compress/process", methods=["POST"])
def image_compress_process():
    try:
        file = request.files.get("image")
        if not file or file.filename == "":
            return "Koi image select nahi ki", 400
        quality = int(request.form.get("quality", 70))
        if quality < 1 or quality > 100:
            return "Quality 1 se 100 ke beech honi chahiye", 400
        img = Image.open(file.stream)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        output.seek(0)
        base = os.path.splitext(file.filename)[0]
        return send_file(output, mimetype="image/jpeg", as_attachment=True,
                         download_name=f"{base}_compressed.jpg")
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/tools/image-crop")
def image_crop_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("image-crop.html")

@app.route("/tools/image-crop/process", methods=["POST"])
def image_crop_process():
    try:
        file = request.files.get("image")
        if not file or file.filename == "":
            return "Koi image select nahi ki", 400
        x = int(request.form.get("x", 0))
        y = int(request.form.get("y", 0))
        width = int(request.form.get("width", 0))
        height = int(request.form.get("height", 0))
        if width <= 0 or height <= 0:
            return "Sahi width/height daalo", 400
        img = Image.open(file.stream)
        img_w, img_h = img.size
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        width = min(width, img_w - x)
        height = min(height, img_h - y)
        cropped = img.crop((x, y, x + width, y + height))
        output = io.BytesIO()
        fmt = img.format if img.format else "PNG"
        if fmt not in ("JPEG", "PNG", "WEBP", "GIF", "BMP"):
            fmt = "PNG"
        if fmt == "JPEG" and cropped.mode in ("RGBA", "P"):
            cropped = cropped.convert("RGB")
        cropped.save(output, format=fmt)
        output.seek(0)
        base = os.path.splitext(file.filename)[0]
        ext = fmt.lower() if fmt != "JPEG" else "jpg"
        return send_file(output, mimetype=f"image/{ext}", as_attachment=True,
                         download_name=f"{base}_cropped.{ext}")
    except Exception as e:
        return f"Error: {str(e)}", 500

# ---------- PDF Tools ----------

@app.route("/tools/photo-to-pdf")
def photo_to_pdf_tool():
    if not require_staff(): return redirect(url_for("login"))
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
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)
        first = images[0]
        rest = images[1:]
        output = io.BytesIO()
        first.save(output, format="PDF", save_all=True, append_images=rest)
        output.seek(0)
        return send_file(output, mimetype="application/pdf", as_attachment=True,
                         download_name="gd-pulse-images.pdf")
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/tools/pdf-merge")
def pdf_merge_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("pdf-merge.html")

@app.route("/tools/pdf-merge/process", methods=["POST"])
def pdf_merge_process():
    try:
        from pypdf import PdfWriter, PdfReader
        files = request.files.getlist("pdfs")
        files = [f for f in files if f and f.filename != ""]
        if len(files) < 2:
            return "Kam se kam 2 PDF files select karo", 400
        writer = PdfWriter()
        for f in files:
            reader = PdfReader(f.stream)
            for page in reader.pages:
                writer.add_page(page)
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return send_file(output, mimetype="application/pdf", as_attachment=True,
                         download_name="gd-pulse-merged.pdf")
    except Exception as e:
        return f"Error: {str(e)}", 500

# ============================================
# MEDIA TOOLS
# ============================================

@app.route("/tools/video-to-mp3")
def video_to_mp3_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("video-to-mp3.html")

@app.route("/tools/video-to-mp3/process", methods=["POST"])
def video_to_mp3_process():
    try:
        file = request.files.get("video")
        if not file or file.filename == "":
            return "Koi video select nahi ki", 400
        input_path = "/tmp/input_video"
        output_path = "/tmp/output_audio.mp3"
        file.save(input_path)
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(input_path)
        clip.audio.write_audiofile(output_path, codec="mp3", verbose=False, logger=None)
        clip.close()
        base = os.path.splitext(file.filename)[0]
        return send_file(output_path, mimetype="audio/mpeg", as_attachment=True,
                         download_name=f"{base}.mp3")
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
