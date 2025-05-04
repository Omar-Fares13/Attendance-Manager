from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    seq_number: int
    faculty_id: int
    is_male: bool = True
    notes: Optional[str] = ""
    national_id: str
    qr_received: bool = False
    photo_path: Optional[str] = None
    qrCode_path: Optional[str] = None

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "faculty_id": self.faculty_id,
            "seq_number": self.seq_number,
            "is_male": self.is_male,
            "notes": self.notes,
            "photo": self.photo_path,
            "qr_received": self.qr_received,
            "national_id": self.national_id,
            "qrCode_path": self.qrCode_path
        }



class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    faculty_id: int = Field(foreign_key="student.faculty_id")
    entrance_time: datetime
    leave_time: Optional[datetime] = None
    is_male: bool = True

    def to_json(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "faculty_id": self.faculty_id,
            "entrance_time": self.entrance_time.isoformat(),
            "leave_time": self.leave_time.isoformat() if self.leave_time else None,
            "is_male": self.is_male
        }
    
class Faculty(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    is_male : bool
