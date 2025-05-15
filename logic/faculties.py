# faculty_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Faculty
from sqlalchemy.orm import selectinload
from typing import List, Optional
from db import get_session, engine


# Create faculty
def create_faculty(name : str) -> Faculty:
    faculty = Faculty(name = name)
    with next(get_session()) as session:
        session.add(faculty)
        session.commit()
        session.refresh(faculty)
        return faculty

# Get all faculties
def get_all_faculties() -> list[Faculty]:
    with Session(engine) as session:
        statement = select(Faculty).options(selectinload(Faculty.students))
        results = session.exec(statement)
        faculties = results.all()
        # At this point, each faculty object in the 'faculties' list
        # will have its 'students' attribute already populated.
        return faculties

# Get by ID
def get_faculty_by_id(faculty_id: int) -> Optional[Faculty]:
    with next(get_session()) as session:
        faculty = session.get(Faculty, faculty_id)
        return faculty

# Update
def update_faculty(faculty_id: int, updated_fields: dict) -> Optional[Faculty]:
    with next(get_session()) as session:
        faculty = session.get(Faculty, faculty_id)
        if not faculty:
            return None
        for field, value in updated_fields.items():
            setattr(faculty, field, value)
        session.add(faculty)
        session.commit()
        session.refresh(faculty)
        return faculty

# Delete
def delete_faculty(faculty_id: int) -> bool:
    """
    Delete a faculty and all its associated students.
    
    Args:
        faculty_id: The ID of the faculty to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    from logic.students import delete_student  # Import here to avoid circular imports
    
    with next(get_session()) as session:
        try:
            # Get faculty with its students loaded
            stmt = (
                select(Faculty)
                .options(selectinload(Faculty.students))
                .where(Faculty.id == faculty_id)
            )
            faculty = session.exec(stmt).one_or_none()
            
            if not faculty:
                return False
            
            # Delete all students associated with this faculty
            student_count = 0
            if faculty.students:
                print(f"Deleting {len(faculty.students)} students from faculty '{faculty.name}'")
                for student in faculty.students:
                    # Use the delete_student function to properly handle student relationships
                    success = delete_student(student.id)
                    if success:
                        student_count += 1
                    else:
                        print(f"Failed to delete student {student.id} ({student.name})")
                
                # Refresh the faculty object to reflect changes
                session.refresh(faculty)
            
            # Now delete the faculty
            session.delete(faculty)
            session.commit()
            print(f"Successfully deleted faculty '{faculty.name}' and {student_count} students")
            return True
            
        except Exception as e:
            print(f"Error deleting faculty: {e}")
            session.rollback()
            return False

def get_faculties(name_query: str) -> List[Faculty]:
    """
    Fetch all faculties whose name contains the given substring (case-insensitive).
    """
    stmt = (
        select(Faculty)
        .options(selectinload(Faculty.students))
        .where(Faculty.name.ilike(f"%{name_query}%"))
    )

    with next(get_session()) as session:
        return session.exec(stmt).all()