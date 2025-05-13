import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session

load_dotenv()

# Create AppData directory
app_data_dir = os.path.join(os.environ.get('APPDATA', ''), 'Attendance Manager')
os.makedirs(app_data_dir, exist_ok=True)
db_path = os.path.join(app_data_dir, 'attendance.db')

# Make sure we have a valid connection string
# The problem is that your code is getting an empty DATABASE_URL from somewhere
DATABASE_URL = f"sqlite:///{db_path.replace(os.sep, '/')}"

print(f"Database will be stored at: {db_path}")
print(f"Using connection string: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    import models
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session