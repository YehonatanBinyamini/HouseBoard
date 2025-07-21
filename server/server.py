from flask import Flask, request, redirect, send_from_directory, jsonify, session, render_template_string
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder='../client/dist')
app.secret_key = 'SOME_SECRET'  # לשמירת סשנים

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'rashi63/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = "admin"
PASSWORD = "1234"  # החלף בסיסמה חזקה

# דף התחברות בסיסי
LOGIN_HTML = """
<form method="post">
  <input name="username" placeholder="User">
  <input name="password" placeholder="Pass" type="password">
  <button type="submit">Login</button>
</form>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect("/rashi63/upload")
    return render_template_string(LOGIN_HTML)

# דף העלאה
UPLOAD_HTML = """
<form method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <button type="submit">Upload</button>
</form>
"""

@app.route("/rashi63/upload", methods=["GET", "POST"])
def upload_file():
    if not session.get("logged_in"):
        return redirect("/login")
    if request.method == "POST":
        f = request.files["file"]
        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            return f"Uploaded: <a href='/rashi63/uploads/{filename}'>{filename}</a>"
    return render_template_string(UPLOAD_HTML)

# הצגת כל הקישורים
@app.route("/image-urls")
def image_urls():
    files = os.listdir(UPLOAD_FOLDER)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

