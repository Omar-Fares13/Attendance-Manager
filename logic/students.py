# student_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Student,Faculty
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

def get_students(search_attributes: dict[str, any]) -> List[Student]:
    """
    Fetch students matching any subset of the provided search_attributes.
    Supported keys: name, national_id, phone_number, seq_num, faculty, qr_code
    """
    # start a fresh statement
    stmt = select(Student).join(Faculty)

    # apply filters in the order you like
    if "name" in search_attributes:
        q = search_attributes["name"]
        stmt = stmt.where(Student.name.ilike(f"%{q}%"))

    if "national_id" in search_attributes:
        q = search_attributes["national_id"]
        stmt = stmt.where(Student.national_id == q)

    if "phone_number" in search_attributes:
        q = search_attributes["phone_number"]
        stmt = stmt.where(Student.phone_numer.ilike(f"%{q}%"))

    if "seq_num" in search_attributes:
        q = search_attributes["seq_num"]
        # your model calls it suq_number
        stmt = stmt.where(Student.suq_number.ilike(f"%{q}%"))

    if "qr_code" in search_attributes:
        q = search_attributes["qr_code"]
        stmt = stmt.where(Student.qr_code.ilike(f"%{q}%"))

    if "faculty" in search_attributes:
        q = search_attributes["faculty"]
        stmt = stmt.where(Faculty.name.ilike(f"%{q}%"))

    # execute and return
    with next(get_session()) as session:
        students: List[Student] = session.exec(stmt).all()
    return students