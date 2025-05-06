from sqlmodel import Session, delete
from db import engine
from models import Note, Attendance, Student, Course, Faculty
import os
from db import create_db_and_tables

# Get the folder path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER_PATH = os.path.join(SCRIPT_DIR, "..", "captured_images")  # navigate up one level, then to captured_images
IMAGE_FOLDER_PATH = os.path.abspath(IMAGE_FOLDER_PATH)  # normalize to full path


def delete_all_data():
    # Delete image files from folder
    if os.path.exists(IMAGE_FOLDER_PATH):
        for filename in os.listdir(IMAGE_FOLDER_PATH):
            file_path = os.path.join(IMAGE_FOLDER_PATH, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Failed to delete {file_path}: {e}")
        print("🧹 Image folder cleared.")
    else:
        print(f"❌ Folder not found: {IMAGE_FOLDER_PATH}")

    # Delete data from database
    with Session(engine) as session:
        session.exec(delete(Note))
        session.exec(delete(Attendance))
        session.exec(delete(Student))
        session.exec(delete(Course))
        session.exec(delete(Faculty))
        session.commit()
        print("✅ All data deleted successfully.")

    create_db_and_tables()
    print("✅ tables were initiated.")