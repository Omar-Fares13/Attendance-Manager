# attendance_crud.py

from sqlmodel import Session, select
from typing import List, Optional
from models import Attendance
from db import get_session

# Create attendance record
def create_attendance(record: Attendance) -> Attendance:
    with next(get_session()) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

# Get all records
def get_all_attendance() -> List[Attendance]:
    with next(get_session()) as session:
        records = session.exec(select(Attendance)).all()
        return records

# Get attendance by student ID
def get_attendance_by_student_id(student_id: int) -> List[Attendance]:
    with next(get_session()) as session:
        statement = select(Attendance).where(Attendance.student_id == student_id)
        return session.exec(statement).all()

# Update attendance record
def update_attendance(record_id: int, updated_fields: dict) -> Optional[Attendance]:
    with next(get_session()) as session:
        record = session.get(Attendance, record_id)
        if not record:
            return None
        for field, value in updated_fields.items():
            setattr(record, field, value)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

# Delete attendance record
def delete_attendance(record_id: int) -> bool:
    with next(get_session()) as session:
        record = session.get(Attendance, record_id)
        if not record:
            return False
        session.delete(record)
        session.commit()
        return True
