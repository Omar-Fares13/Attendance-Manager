from db import create_db_and_tables
import models
from logic.faculties import create_faculty
from logic.students import create_student,get_student_by_id

create_db_and_tables()

faculty = models.Faculty(name="handasa")
create_faculty(faculty)  # After this, faculty.id will be populated

student_1 = models.Student(
name="Ali Ahmed",
is_male=True,
faculty_id=faculty.id,
seq_number="12345",
national_id="29801011234567",
qr_code="qr1",
photo_path="path1.jpg"
)

student_2 = models.Student(
name="Fatma Hassan",
is_male=False,
faculty_id=faculty.id,
seq_number="12346",
national_id="29902021234567",
qr_code="qr2",
photo_path="path2.jpg"
)

create_student(student_1)
create_student(student_2)


print(get_student_by_id(1))