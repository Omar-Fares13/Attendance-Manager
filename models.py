from typing import List, Optional
from datetime import date, time
from sqlmodel import SQLModel, Field, Relationship


class Faculty(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Back-reference to students
    students: List["Student"] = Relationship(back_populates="faculty")


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_numer : str
    name: str
    is_male: bool
    faculty_id: int = Field(foreign_key="faculty.id")
    suq_number: str
    national_id: str
    qr_code: str
    photo_path: str

    # Relationships
    faculty: Optional[Faculty] = Relationship(back_populates="students")
    student_courses: List["StudentCourse"] = Relationship(back_populates="student")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_date: date
    end_date: date
    is_male_type: bool

    # Relationship to enrollments
    student_courses: List["StudentCourse"] = Relationship(back_populates="course")


class StudentCourse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    course_id: int = Field(foreign_key="course.id")

    # Relationships
    student: Optional[Student] = Relationship(back_populates="student_courses")
    course: Optional[Course] = Relationship(back_populates="student_courses")
    attendance: List["Attendance"] = Relationship(back_populates="student_course")
    notes: List["Note"] = Relationship(back_populates="student_course")


class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    arrival_time: time
    leave_time: time
    student_course_id: int = Field(foreign_key="studentcourse.id")

    # Relationship to the enrollment
    student_course: Optional[StudentCourse] = Relationship(back_populates="attendance")


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    note: str
    is_warning: bool
    student_course_id: int = Field(foreign_key="studentcourse.id")

    # Relationship to the enrollment
    student_course: Optional[StudentCourse] = Relationship(back_populates="notes")
