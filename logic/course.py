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