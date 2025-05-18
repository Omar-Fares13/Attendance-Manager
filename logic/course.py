from models import Course
from datetime import date, timedelta
from sqlmodel import select, Session
from db import get_session

def create_course(
    *,
    start_date: date | None = None,
    end_date:   date | None = None,
    is_male_type: bool = True,
) -> Course:
    # 1) Compute defaults only when needed:
    if start_date is None:
        start_date = date.today() + timedelta(days=1)
    if end_date is None:
        end_date = start_date + timedelta(days=12)

    is_male_type = is_male_type == '1'
    # 2) Now create and persist:
    with next(get_session()) as session:
        course = Course(
            start_date=start_date,
            end_date=end_date,
            is_male_type=is_male_type,
        )
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

def get_latest_course(is_male_type : bool = True):
    with next(get_session()) as session:
        stmt = (
            select(Course)
            .where(Course.is_male_type == is_male_type)
            .order_by(Course.start_date.desc())
            .limit(1)
        )
        course = session.exec(stmt).one_or_none()
        return course

def get_all_courses():
    with next(get_session()) as session:
        stmt = (
            select(Course)
            .order_by(Course.start_date.desc())
        )
        courses = session.exec(stmt).all()
        return courses

def get_course_by_id(course_id: int):
    """Get a course by its ID"""
    with next(get_session()) as session:
        stmt = select(Course).where(Course.id == course_id)
        course = session.exec(stmt).one_or_none()
        return course