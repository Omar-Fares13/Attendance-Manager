from db import create_db_and_tables
import models
from logic.faculties import create_faculty
from logic.students import create_student,get_student_by_id
from logic.course import create_course
from DTOs.StudentCreateDTO import StudentCreateDTO
create_db_and_tables()
create_faculty("Engineering")

# Create and save a faculty
student_1 = StudentCreateDTO(
    name="Ali Ahmed",
    is_male=True,
    faculty_id=1,
    national_id="29801011234567",
    phone_number="0123456789"  # Make sure to provide a valid phone number
)

student_2 = StudentCreateDTO(
    name="Fatma Hassan",
    is_male=False,
    faculty_id=2,
    national_id="29902021234567",
    phone_number="0987654321"  # Provide a valid phone number
)

create_course(is_male_type = True)
create_course(is_male_type = False)
create_student(student_1)
create_student(student_2)


print(get_student_by_id(1))