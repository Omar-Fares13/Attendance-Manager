from logic.students import get_students,create_student

students = get_students({"name" : "ali"}) 
print(students)
for s in students:
    print(s.faculty.name)
