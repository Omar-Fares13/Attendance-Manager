# student_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Student, Faculty, Course, Note
from db import get_session
from sqlalchemy.orm import selectinload
from DTOs.StudentCreateDTO import StudentCreateDTO
import uuid
from sqlalchemy import func
from logic.faculties import create_faculty
from logic.course import create_course
# Create

def create_student_from_dict(student_data: dict[str, any]) -> Student:
    with next(get_session()) as session:
        # Find the current max seq_number for this faculty
        stmt = (
            select(Course.id)
            .where(Course.is_male_type == student_data["is_male"])
            .order_by(Course.start_date.desc())
            .limit(1)
        )
        course_id = session.exec(stmt).one_or_none()
        student_data["course_id"] = course_id
        student_data["is_male"] = student_data["is_male"] == "1"

        stmt = (
            select(Student.seq_number)
            .where(Student.faculty_id == student_data["faculty_id"])
            .where(Student.course_id == course_id)
            .order_by(Student.seq_number.desc())
            .limit(1)
        )
        seq = session.exec(stmt).one_or_none()

        # Prepare the dict for instantiation
        data = student_data.copy()
        data["qr_code"] = str(uuid.uuid4())
        data["seq_number"] = (int(seq) + 1) if seq is not None else 1

        # Create and persist the Student
        student = Student(**data)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


def create_student(stu : StudentCreateDTO) -> Student:
    with next(get_session()) as session:
        stmt = (
            select(Course.id)
            .where(Course.is_male_type == stu.is_male)
            .order_by(Course.start_date.desc())
            .limit(1)
        )
        course_id = session.exec(stmt).one_or_none()
        stmt = (
            select(Student.seq_number)
            .where(Student.faculty_id == stu.faculty_id)
            .where(Student.course_id == course_id)
            .order_by(Student.seq_number.desc())
            .limit(1)
        )
        seq = session.exec(stmt).one_or_none()
        student = Student(
            name = stu.name,
            phone_number = stu.phone_number,
            is_male = stu.is_male,
            faculty_id = stu.faculty_id,
            national_id = stu.national_id,
            qr_code = str(uuid.uuid4()),
            seq_number = int(seq) + 1 if seq else 1,
            course_id = course_id
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

def create_students_from_file(students, faculty, course_date, is_male):
    with next(get_session()) as session:
        stmt = (
            select(Faculty.id)
            .where(Faculty.name.ilike(f'%{faculty}%'))
            .limit(1)
        )
        faculty_id = session.exec(stmt).one_or_none()
        if faculty_id is None:
            fac = create_faculty(faculty)
            faculty_id = fac.id
        stmt = (
            select(Course.id)
            .where(func.extract('day', Course.start_date) == course_date.day)
            .where(Course.is_male_type == is_male)
            .limit(1)
        )
        course_id = session.exec(stmt).one_or_none()
        if course_id is None:
            course = create_course(is_male_type = is_male, start_date = course_date)
            course_id = course.id
        for std in students:
            std['course_id'] = course_id
            std['faculty_id'] = faculty_id
            std['is_male'] = is_male
            create_student_from_dict(std)