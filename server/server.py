from flask import Flask, request, redirect, send_from_directory, jsonify, session, render_template_string, abort
from werkzeug.utils import secure_filename
import hmac
import hashlib
import subprocess
import os
import time

app = Flask(__name__, static_folder='../client/dist')
app.secret_key = 'SOME_SECRET'
GITHUB_SECRET = 'houseBoard'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'rashi63/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "admin"
PASSWORD = "1204"  # החלף בסיסמה חזקה

# HTML בסיסי עם עיצוב
BASE_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f8f9fa;
      color: #333;
      padding: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    h1 {
      margin-bottom: 30px;
    }
    form {
      background: white;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.1);
      display: flex;
      flex-direction: column;
      gap: 15px;
      width: 100%;
      max-width: 400px;
    }
    input[type="file"], input[type="text"], input[type="password"] {
      padding: 10px;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 6px;
    }
    button {
      padding: 12px;
      font-size: 1rem;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover {
      background-color: #0056b3;
    }
    .message {
      margin-top: 20px;
      background: #e9ffe9;
      padding: 15px;
      border: 1px solid #b2ffb2;
      border-radius: 8px;
      color: #2e7d32;
    }
    a {
      color: #007bff;
    }
  </style>
</head>
<body>
  <h1>{{ title }}</h1>
  {{ body }}
</body>
</html>
"""

# טופס התחברות
LOGIN_FORM = """
<form method="post">
  <input name="username" placeholder="שם משתמש">
  <input name="password" placeholder="סיסמה" type="password">
  <button type="submit">התחבר</button>
</form>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect("/rashi63/upload")
    return render_template_string(BASE_HTML, title="התחברות", body=LOGIN_FORM)


# טופס העלאה
UPLOAD_FORM = """
<form method="post" enctype="multipart/form-data">
  <input type="file" name="file" required>
  <button type="submit">העלה קובץ</button>
</form>
{% if filename %}
<div class="message">
  הקובץ הועלה בהצלחה:
  <br>
  <a href="/rashi63/uploads/{{ filename }}" target="_blank">{{ filename }}</a>
</div>
{% endif %}
"""


@app.route("/rashi63/upload", methods=["GET", "POST"])
def upload_file():
    if not session.get("logged_in"):
        return redirect("/login")

    uploaded_filename = None

    if request.method == "POST":
        f = request.files["file"]
        if f:
            original_filename = secure_filename(f.filename)
            ext = os.path.splitext(original_filename)[1].lower()
            timestamp = int(time.time())
            new_filename = f"{timestamp}{ext}"
            f.save(os.path.join(UPLOAD_FOLDER, new_filename))
            uploaded_filename = new_filename

    return render_template_string(BASE_HTML, title="העלאת קובץ", body=UPLOAD_FORM, filename=uploaded_filename)

# API: רשימת קישורים לתמונות (מהחדש לישן)


@app.route("/image-urls")
def image_urls():
    files = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    ]
    files.sort(key=lambda f: os.path.getctime(
        os.path.join(UPLOAD_FOLDER, f)), reverse=True)
    urls = [request.host_url + f"rashi63/uploads/{file}" for file in files]
    return jsonify(urls)

# הגשת תמונות


@app.route("/rashi63/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# הגשת אתר React


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        abort(403)

    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        abort(501)

    mac = hmac.new(GITHUB_SECRET, msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)

    # שלב הפקודות:
    try:
        subprocess.run(["git", "pull"], cwd="/home/yb/houseBoard", check=True)
        subprocess.run(["npm", "install"],
                       cwd="/home/yb/houseBoard/client", check=True)
        subprocess.run(["npm", "run", "build"],
                       cwd="/home/yb/houseBoard/client", check=True)
        subprocess.run(["systemctl", "restart", "gunicorn"], check=True)
        return "Updated", 200
    except subprocess.CalledProcessError as e:
        return f"Update failed: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
