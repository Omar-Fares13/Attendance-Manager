# student_crud.py

from sqlmodel import Session, select
from typing import List, Optional
from models import Student
from db import get_session

# Create
def create_student(student: Student) -> Student:
    with next(get_session()) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
        return student

# Read all
def get_all_students() -> List[Student]:
    with next(get_session()) as session:
        students = session.exec(select(Student)).all()
        return students

# Read one
def get_student_by_id(student_id: int) -> Optional[Student]:
    with next(get_session()) as session:
        student = session.get(Student, student_id)
        return student

# Update
def update_student(student_id: int, updated_fields: dict) -> Optional[Student]:
    with next(get_session()) as session:
        student = session.get(Student, student_id)
        if not student:
            return None
        for field, value in updated_fields.items():
            setattr(student, field, value)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student

# Delete
def delete_student(student_id: int) -> bool:
    with next(get_session()) as session:
        student = session.get(Student, student_id)
        if not student:
            return False
        session.delete(student)
        session.commit()
        return True


#Search by seq

def get_student_by_seq_number(seq_number: int) -> Optional[Student]:
    with next(get_session()) as session:
        statement = select(Student).where(Student.seq_number == seq_number)
        return session.exec(statement).first()

#Search by name

def search_students_by_name(name_query: str) -> List[Student]:
    with next(get_session()) as session:
        statement = select(Student).where(Student.name.ilike(f"%{name_query}%"))
        return session.exec(statement).all()