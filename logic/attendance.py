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


def get_attendance_data(page, report_dates):
    """
    Fetch and format student attendance data from the database
    
    Args:
        page: Flet page object with course_id property
        report_dates: List of dates for the report
        
    Returns:
        List of formatted student attendance data dictionaries
    """
    from logic.students import get_students
    from logic.attendance import get_attendance_by_student_id
    
    processed_data = []
    
    # Get course ID from page or use latest course if not provided
    course_id = getattr(page, 'course_id', None)
    if not course_id:
        from logic.course import get_latest_course
        course = get_latest_course()
        if course:
            course_id = course.id
    
    # Get students for this course
    search_params = {'course_id': course_id}
    
    # Add faculty filter if specified
    if hasattr(page, 'faculty_id') and page.faculty_id:
        search_params['faculty_id'] = page.faculty_id
        
    # Add name filter if specified
    if hasattr(page, 'student_name') and page.student_name:
        search_params['name'] = page.student_name
    
    # Fetch students from database
    students = get_students(search_params)
    
    # Process each student
    for idx, student in enumerate(students):
        # Create student base data
        student_data = {
            'seq': student.seq_number,
            'name': student.name,
            'faculty': student.faculty.name if student.faculty else "",
            'attendance': {}
        }
        
        # Get attendance records for this student
        attendance_records = get_attendance_by_student_id(student.id)
        
        # Process attendance records
        for record in attendance_records:
            # Check if this date is in our report period
            if record.date in report_dates:
                # Format times as strings
                arrival = record.arrival_time.strftime("%H:%M") if record.arrival_time else ""
                departure = record.leave_time.strftime("%H:%M") if record.leave_time else ""
                
                # Add to student's attendance dictionary
                student_data['attendance'][record.date] = {
                    'arrival': arrival,
                    'departure': departure
                }
        
        # Add this student to processed data
        processed_data.append(student_data)
    
    return processed_data