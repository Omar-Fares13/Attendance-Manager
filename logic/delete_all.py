from sqlmodel import Session, delete
from db import engine, images_dir  # Import images_dir directly from db.py
from models import Note, Attendance, Student, Course, Faculty
import os
from db import create_db_and_tables

def delete_all_data():
    # Delete image files from folder
    if os.path.exists(images_dir):
        for filename in os.listdir(images_dir):
            file_path = os.path.join(images_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Failed to delete {file_path}: {e}")
        print("🧹 Image folder cleared.")
    else:
        print(f"❌ Folder not found: {images_dir}")

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