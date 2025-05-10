class StudentCreateDTO:
    def __init__(
        self,
        phone_number: str,
        name: str,
        is_male: bool,
        faculty_id: int,
        national_id: str,
        location: str
        ):
        self.phone_number = phone_number
        self.name = name
        self.is_male = is_male
        self.faculty_id = faculty_id
        self.national_id = national_id
        self.location = location
        self.raw_name = name

    def to_student():
        student = Student(
            name = self.name,
            raw_name = self.raw_name,
            phone_number = self.phone_number,
            is_male = self.is_male,
            faculty = self.faculty_id,
            national_id = self.national_id,
            qr_code = str(uuid.uuid4())
        )
