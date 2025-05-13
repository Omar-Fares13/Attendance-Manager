# student_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Student, Faculty, Course, Note
from db import get_session
from sqlalchemy.orm import joinedload, selectinload
from DTOs.StudentCreateDTO import StudentCreateDTO
import uuid
from sqlalchemy import func
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
    try:
        with next(get_session()) as session:
            # Set raw_name if not provided
            if not "raw_name" in student_data:
                student_data['raw_name'] = student_data['name']
            
            # Convert is_male to boolean before using in queries
            student_data["is_male"] = student_data["is_male"] == "1"
            
            # Find the current max seq_number for this faculty
            stmt = (
                select(Course.id)
                .where(Course.is_male_type == student_data["is_male"])
                .order_by(Course.start_date.desc())
                .limit(1)
            )
            course_id = session.exec(stmt).one_or_none()
            if not course_id:
                print(f"ERROR: No course found for is_male={student_data['is_male']}")
                return None
                
            student_data["course_id"] = course_id
            
            # Handle faculty lookup if needed
            if not 'faculty_id' in student_data:
                fac_name = student_data['faculty']
                student_data.pop('faculty', None)
                cands = get_faculties(fac_name)
                if not cands or len(cands) == 0:
                    cands = [create_faculty(fac_name)]
                fac = cands[0]
                student_data['faculty_id'] = fac.id
            
            # *** FIX: Explicitly convert faculty_id to integer ***
            faculty_id = int(student_data["faculty_id"])
            
            # Find max sequence with correct types
            stmt = (
                select(Student.seq_number)
                .where(Student.faculty_id == faculty_id)  # Using integer
                .where(Student.course_id == course_id)
                .order_by(Student.seq_number.desc())
                .limit(1)
            )
            seq = session.exec(stmt).one_or_none()
            
            # Debug output
            print(f"Looking for max sequence with faculty_id={faculty_id} (int), course_id={course_id}")
            print(f"Current max sequence number: {seq}")

            # Prepare the dict for instantiation
            data = student_data.copy()
            data["faculty_id"] = faculty_id  # Store the integer version
            data["qr_code"] = str(uuid.uuid4())
            
            # Handle sequence number calculation
            if not 'seq_number' in data:
                try:
                    if seq is not None:
                        data["seq_number"] = int(seq) + 1
                    else:
                        data["seq_number"] = 1
                    print(f"Assigned sequence number: {data['seq_number']}")
                except Exception as e:
                    print(f"Error processing sequence number: {e}")
                    data["seq_number"] = 1

            # Create and persist the Student
            student = Student(**data)
            session.add(student)
            session.commit()
            session.refresh(student)
            return student
    except Exception as e:
        print(f"Error creating student: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    
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
            raw_name = stu.raw_name,
            phone_number = stu.phone_number,
            is_male = stu.is_male,
            faculty_id = stu.faculty_id,
            national_id = stu.national_id,
            location=stu.location,
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
        stmt = (select(Student)
        .options(
            selectinload(Student.faculty),
            selectinload(Student.course),
            selectinload(Student.attendance),
            selectinload(Student.notes),
        )
        .where(Student.id == student_id)
        .limit(1)
        )
        student = session.exec(stmt).one_or_none()
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
        print("saved")
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
        statement = select(Student).where(Student.raw_name.ilike(f"%{name_query}%"))
        return session.exec(statement).all()

def get_students(search_attributes: dict[str, any]) -> List[Student]:
    """
    Fetch students matching any subset of the provided search_attributes,
    and eagerly load faculty, course, attendance, and notes relationships.
    Supported keys: name, national_id, phone_number, seq_num, faculty, qr_code,
    is_male, course_id
    """
    # start a fresh statement with eager-loading options for all relationships
    stmt = (
        select(Student)
        .options(
            selectinload(Student.faculty),
            selectinload(Student.course),
            selectinload(Student.attendance),
            selectinload(Student.notes),
        )
    )

    # apply filters
    if "name" in search_attributes:
        q = search_attributes["name"]
        stmt = stmt.where(Student.raw_name.ilike(f"%{q}%"))

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
        stmt = stmt.where(Student.qr_code == q)

    if "location" in search_attributes:
        q = search_attributes["location"]
        stmt = stmt.where(Student.location.ilike(f"%{q}%"))

    if 'faculty_id' in search_attributes:
        q = search_attributes['faculty_id']
        stmt = stmt.where(Student.faculty_id == q)

    if "is_male" in search_attributes:
        q = search_attributes["is_male"]
        # Make the boolean comparison more explicit
        if q is True:
            stmt = stmt.where(Student.is_male == True)
        elif q is False:
            stmt = stmt.where(Student.is_male == False)
        # No else needed - if q is None, don't add a filter
    
    if "course_id" in search_attributes:
        q = search_attributes["course_id"]
        stmt = stmt.where(Student.course_id == q)
    if 'page' in search_attributes:
        x = 20 * search_attributes['page']
        stmt = stmt.offset(x).limit(20)
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
            if not 'raw_name' in std:
                print("=" * 100)
                std['raw_name'] = std['name']
            create_student_from_dict(std)

def save_note(note : str, student_id : int, is_warning : bool = False):
    note_entry = Note(note = note, student_id = student_id, is_warning = is_warning)
    print(note)
    print(student_id)
    print(is_warning)
    print("="*50)
    with next(get_session()) as session:
        session.add(note_entry)
        session.commit()
        session.refresh(note_entry)
    return note_entry