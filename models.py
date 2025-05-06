from typing import List, Optional
from datetime import date, time
from sqlmodel import SQLModel, Field, Relationship


class Faculty(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Back‑reference to students
    students: List["Student"] = Relationship(back_populates="faculty")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_date: date
    end_date: date
    is_male_type: bool

    # Direct enrollments
    students: List["Student"] = Relationship(back_populates="course")


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = ""
    name: str
    is_male: bool
    faculty_id: int = Field(foreign_key="faculty.id")
    course_id: int = Field(foreign_key="course.id")    # ← new FK
    seq_number: str
    national_id: str
    qr_code: str
    photo_path: Optional[str] = ""

    # Relationships
    faculty: Optional[Faculty] = Relationship(back_populates="students")
    course: Optional[Course] = Relationship(back_populates="students")
    attendance: List["Attendance"] = Relationship(back_populates="student")
    notes: List["Note"]       = Relationship(back_populates="student")


class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    arrival_time: time
    leave_time: time

    student_id: int = Field(foreign_key="student.id")   # ← now points to Student

    # Relationship to the student
    student: Optional[Student] = Relationship(back_populates="attendance")


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    note: str
    is_warning: bool

    student_id: int = Field(foreign_key="student.id")   # ← now points to Student

    # Relationship to the student
    student: Optional[Student] = Relationship(back_populates="notes")
