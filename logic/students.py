# student_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Student, Faculty, StudentCourse
from db import get_session
from sqlalchemy.orm import selectinload
from DTOs.StudentCreateDTO import StudentCreateDTO
import uuid
# Create
def create_student(stu : StudentCreateDTO) -> Student:
    with next(get_session()) as session:
        stmt = select(Student.seq_number).where(Student.faculty_id == stu.faculty_id).order_by(Student.seq_number.desc()).limit(1)
        seq = session.exec(stmt).one_or_none()
        student = Student(
            name = stu.name,
            phone_number = stu.phone_number,
            is_male = stu.is_male,
            faculty_id = stu.faculty_id,
            national_id = stu.national_id,
            qr_code = str(uuid.uuid4()),
            seq_number = int(seq) + 1 if seq else 1
            )    
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
def update_student(updated_fields: dict) -> Optional[Student]:
    if not "id" in updated_fields:
        return
    student_id = updated_fields["id"]
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
    stmt = select(Student).options(selectinload(Student.faculty))

    # apply filters in the order you like
    if "name" in search_attributes:
        q = search_attributes["name"]
        stmt = stmt.where(Student.name.ilike(f"%{q}%"))

    if "national_id" in search_attributes:
        q = search_attributes["national_id"]
        stmt = stmt.where(Student.national_id.ilike(f"%{q}%"))

    if "phone_number" in search_attributes:
        q = search_attributes["phone_number"]
        stmt = stmt.where(Student.phone_number.ilike(f"%{q}%"))

    if "seq_num" in search_attributes:
        q = search_attributes["seq_num"]
        stmt = stmt.where(Student.seq_number.ilike(f"%{q}%"))

    if "qr_code" in search_attributes:
        q = search_attributes["qr_code"]
        stmt = stmt.where(Student.qr_code.ilike(f"{q}"))

    if "faculty" in search_attributes:
        q = search_attributes["faculty"]
        stmt = stmt.where(Faculty.name.ilike(f"%{q}%"))

    # execute and return
    with next(get_session()) as session:
        students: List[Student] = session.exec(stmt).all()
    return students