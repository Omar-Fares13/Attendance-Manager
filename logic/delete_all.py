from sqlmodel import Session, delete
from db import engine
from models import Note, Attendance, Student, Course, Faculty


def delete_all_data():
    with Session(engine) as session:
        # Delete in reverse dependency order
        session.exec(delete(Note))
        session.exec(delete(Attendance))
        session.exec(delete(Student))
        session.exec(delete(Course))
        session.exec(delete(Faculty))

        session.commit()
        print("✅ All data deleted successfully.")