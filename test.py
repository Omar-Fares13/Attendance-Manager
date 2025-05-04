from db import create_db_and_tables
from models import Faculty, Student
from logic.faculties import create_faculty
from logic.students import create_student,get_student_by_id


create_db_and_tables()

# Create and save a faculty
faculty = Faculty(name="handasa")
create_faculty(faculty)  # After this, faculty.id will be populated

student_1 = Student(
    name="Ali Ahmed",
    is_male=True,
    faculty_id=faculty.id,
    suq_number="SUQ12345",
    national_id="29801011234567",
    qr_code="qr1",
    photo_path="path1.jpg",
    phone_numer="0123456789"  # Make sure to provide a valid phone number
)

student_2 = Student(
    name="Fatma Hassan",
    is_male=False,
    faculty_id=faculty.id,
    suq_number="SUQ12346",
    national_id="29902021234567",
    qr_code="qr2",
    photo_path="path2.jpg",
    phone_numer="0987654321"  # Provide a valid phone number
)


create_student(student_1)
create_student(student_2)


print(get_student_by_id(1))