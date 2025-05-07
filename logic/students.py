# student_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Student, Faculty, Course, Note
from db import get_session
from sqlalchemy.orm import joinedload, selectinload
from DTOs.StudentCreateDTO import StudentCreateDTO
import uuid
from sqlalchemy import func
from logic.faculties import create_faculty
from logic.course import create_course
from logic.faculties import get_faculties, create_faculty
# Create

def get_student_by_qr_code(qr_code: str) -> Optional[Student]:
    """
    Fetch a single Student (with its Faculty) by its QR code string.
    Returns None if no matching student is found.
    """
    with next(get_session()) as session:
        stmt = (
            select(Student)
            .options(
                joinedload(Student.faculty),    # single-valued join is fine
                selectinload(Student.notes)      # load notes in separate query, no row duplication
            )
            .where(Student.qr_code == qr_code)
        )
        return session.exec(stmt).one_or_none()

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
        if not 'faculty_id' in student_data:
            fac_name = student_data['faculty']
            student_data.pop('faculty', None)
            cands = get_faculties(fac_name)
            if not cands or len(cands) == 0:
                cands = [create_faculty(fac_name)]
            fac = cands[0]
            student_data['faculty_id'] = fac.id
        print(student_data)

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
        if not 'seq_number' in data:
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


def get_student_by_id(student_id: int) -> Optional[Student]:
    with next(get_session()) as session:
        student = session.query(Student).options(joinedload(Student.faculty)).filter(Student.id == student_id).one_or_none()
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
    
    if 'is_male' in search_attributes:
        q = search_attributes['is_male']
        stmt = stmt.where(Student.is_male == q)
    
    if 'course_id' in search_attributes:
        q = search_attributes['course_id']
        stmt = stmt.where(Student.course_id == q)
    # execute and return
    with next(get_session()) as session:
        students: List[Student] = session.exec(stmt).all()
    return students

def create_students_from_file(students, course_date, is_male):
    with next(get_session()) as session:
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
            std['is_male'] = is_male
            create_student_from_dict(std)