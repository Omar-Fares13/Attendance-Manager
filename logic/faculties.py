# faculty_crud.py
from sqlmodel import Session, select
from typing import List, Optional
from models import Faculty
from sqlalchemy.orm import selectinload
from typing import List, Optional
from db import get_session

# Create faculty
def create_faculty(name : str) -> Faculty:
    faculty = Faculty(name = name)
    with next(get_session()) as session:
        session.add(faculty)
        session.commit()
        session.refresh(faculty)
        return faculty

# Get all faculties
def get_all_faculties() -> List[Faculty]:
    with next(get_session()) as session:
        faculties = session.exec(select(Faculty)).all()
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
    with next(get_session()) as session:
        faculty = session.get(Faculty, faculty_id)
        if not faculty:
            return False
        session.delete(faculty)
        session.commit()
        return True


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