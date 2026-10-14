
import os
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "schoolms_db")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is missing from .env")

# Create Flask application
app = Flask(__name__)

# Needed for Flask flash messages
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise ValueError("Add FLASK_SECRET_KEY to your .env file")

# Connect to MongoDB Atlas
mongo_client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=15000
)

db = mongo_client[MONGODB_DATABASE]
students_collection = db["students"]

try:
    mongo_client.admin.command("ping")
    print("SUCCESS: Flask connected to MongoDB Atlas!")
    print(f"Database selected: {MONGODB_DATABASE}")
except Exception:
    mongo_client.close()
    raise

# Ensure student IDs are unique
students_collection.create_index("student_id", unique=True)


@app.route("/")
def home():
    total_students = students_collection.count_documents({})
    return render_template(
        "index.html",
        total_students=total_students
    )


@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip().upper()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        class_name = request.form.get("class_name", "").strip()
        guardian_phone = request.form.get("guardian_phone", "").strip()

        if not all([student_id, first_name, last_name, class_name]):
            flash("Please complete all required fields.", "error")
            return redirect(url_for("students"))

        student = {
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "class_name": class_name,
            "guardian_phone": guardian_phone
        }

        try:
            students_collection.insert_one(student)
            flash("Student registered successfully!", "success")
        except DuplicateKeyError:
            flash("That Student ID already exists. Please use a unique ID.", "error")

        return redirect(url_for("students"))

    student_records = list(
        students_collection.find(
            {},
            {"_id": 0}
        ).sort("student_id", 1)
    )

    return render_template(
        "students.html",
        students=student_records
    )


if __name__ == "__main__":
    app.run(debug=True)
