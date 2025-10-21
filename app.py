from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3

# Flaskアプリ
app = Flask(__name__)

# アップロード先
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DB接続関数
DB_NAME = "kid_friendly_places.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# DBテーブル自動作成
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS kid_friendly_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    has_kids_area INTEGER,
    has_diaper_facility INTEGER,
    indoor INTEGER,
    travel_time_minutes INTEGER,
    crowd_rating INTEGER,
    rain_friendly INTEGER,
    friendly_rating INTEGER,
    safety_rating INTEGER,
    cleanliness_rating INTEGER,
    comments TEXT,
    image TEXT
)""")
conn.commit()
conn.close()

# ホームページ
@app.route("/")
def home():
    places = query_db("SELECT * FROM kid_friendly_places")
    return render_template("index.html", places=places)

# スポット追加
@app.route("/add", methods=["GET", "POST"])
def add_place():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        location = request.form.get("location")
        has_kids_area = int(request.form.get("has_kids_area") == "on")
        has_diaper_facility = int(request.form.get("has_diaper_facility") == "on")
        indoor = int(request.form.get("indoor") == "on")
        travel_time_minutes = int(request.form.get("travel_time_minutes"))
        crowd_rating = int(request.form.get("crowd_rating"))
        rain_friendly = int(request.form.get("rain_friendly"))
        friendly_rating = int(request.form.get("friendly_rating"))
        safety_rating = int(request.form.get("safety_rating"))
        cleanliness_rating = int(request.form.get("cleanliness_rating"))
        comments = request.form.get("comments")

        # 画像処理
        file = request.files.get("image")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None

        # DBに保存
        query_db(
            """INSERT INTO kid_friendly_places
            (name, category, location, has_kids_area, has_diaper_facility, indoor,
            travel_time_minutes, crowd_rating, rain_friendly, friendly_rating,
            safety_rating, cleanliness_rating, comments, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, category, location, has_kids_area, has_diaper_facility, indoor,
             travel_time_minutes, crowd_rating, rain_friendly, friendly_rating,
             safety_rating, cleanliness_rating, comments, filename)
        )
        return redirect(url_for("home"))

    return render_template("add.html")

# スポット削除
@app.route("/delete/<int:place_id>")
def delete_place(place_id):
    query_db("DELETE FROM kid_friendly_places WHERE id=?", (place_id,))
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
