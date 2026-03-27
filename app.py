from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
import uuid

app = Flask(__name__)

# アップロード先
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DB
DB_NAME = "kid_friendly_places.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)

    is_select = query.strip().lower().startswith("select")
    if is_select:
        rv = cur.fetchall()
    else:
        rv = None

    conn.commit()
    conn.close()

    if is_select:
        return (rv[0] if rv else None) if one else rv
    return None


def to_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def save_uploaded_file(file):
    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)
    ext = os.path.splitext(original_name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(save_path)
    return unique_name


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS kid_friendly_places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        has_kids_area INTEGER DEFAULT 0,
        has_diaper_facility INTEGER DEFAULT 0,
        indoor INTEGER DEFAULT 0,
        travel_time_minutes INTEGER DEFAULT 0,
        crowd_rating INTEGER DEFAULT 0,
        rain_friendly INTEGER DEFAULT 0,
        friendly_rating INTEGER DEFAULT 0,
        safety_rating INTEGER DEFAULT 0,
        cleanliness_rating INTEGER DEFAULT 0,
        comments TEXT,
        image TEXT
    )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    places = query_db("SELECT * FROM kid_friendly_places ORDER BY id DESC")
    return render_template("index.html", places=places)


@app.route("/add", methods=["GET", "POST"])
def add_place():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()

        has_kids_area = int(request.form.get("has_kids_area") == "on")
        has_diaper_facility = int(request.form.get("has_diaper_facility") == "on")
        indoor = int(request.form.get("indoor") == "on")

        travel_time_minutes = to_int(request.form.get("travel_time_minutes"))
        crowd_rating = to_int(request.form.get("crowd_rating"))
        rain_friendly = to_int(request.form.get("rain_friendly"))
        friendly_rating = to_int(request.form.get("friendly_rating"))
        safety_rating = to_int(request.form.get("safety_rating"))
        cleanliness_rating = to_int(request.form.get("cleanliness_rating"))

        comments = request.form.get("comments", "").strip()

        file = request.files.get("image")
        filename = save_uploaded_file(file)

        query_db(
            """
            INSERT INTO kid_friendly_places
            (
                name, category, location,
                has_kids_area, has_diaper_facility, indoor,
                travel_time_minutes, crowd_rating, rain_friendly,
                friendly_rating, safety_rating, cleanliness_rating,
                comments, image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name, category, location,
                has_kids_area, has_diaper_facility, indoor,
                travel_time_minutes, crowd_rating, rain_friendly,
                friendly_rating, safety_rating, cleanliness_rating,
                comments, filename
            )
        )

        return redirect(url_for("home"))

    return render_template("add.html")


@app.route("/edit/<int:place_id>", methods=["GET", "POST"])
def edit_place(place_id):
    place = query_db(
        "SELECT * FROM kid_friendly_places WHERE id = ?",
        (place_id,),
        one=True
    )

    if place is None:
        return "Place not found", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()

        has_kids_area = int(request.form.get("has_kids_area") == "on")
        has_diaper_facility = int(request.form.get("has_diaper_facility") == "on")
        indoor = int(request.form.get("indoor") == "on")

        travel_time_minutes = to_int(request.form.get("travel_time_minutes"))
        crowd_rating = to_int(request.form.get("crowd_rating"))
        rain_friendly = to_int(request.form.get("rain_friendly"))
        friendly_rating = to_int(request.form.get("friendly_rating"))
        safety_rating = to_int(request.form.get("safety_rating"))
        cleanliness_rating = to_int(request.form.get("cleanliness_rating"))

        comments = request.form.get("comments", "").strip()

        filename = place["image"]
        file = request.files.get("image")
        new_filename = save_uploaded_file(file)
        if new_filename:
            filename = new_filename

        query_db(
            """
            UPDATE kid_friendly_places
            SET
                name = ?,
                category = ?,
                location = ?,
                has_kids_area = ?,
                has_diaper_facility = ?,
                indoor = ?,
                travel_time_minutes = ?,
                crowd_rating = ?,
                rain_friendly = ?,
                friendly_rating = ?,
                safety_rating = ?,
                cleanliness_rating = ?,
                comments = ?,
                image = ?
            WHERE id = ?
            """,
            (
                name, category, location,
                has_kids_area, has_diaper_facility, indoor,
                travel_time_minutes, crowd_rating, rain_friendly,
                friendly_rating, safety_rating, cleanliness_rating,
                comments, filename, place_id
            )
        )

        return redirect(url_for("home"))

    return render_template("edit.html", place=place)


@app.route("/delete/<int:place_id>")
def delete_place(place_id):
    query_db("DELETE FROM kid_friendly_places WHERE id = ?", (place_id,))
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)