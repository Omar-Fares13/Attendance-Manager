import re
from io import BytesIO
import pdfplumber

# For proper Arabic shaping and bidi reordering
import arabic_reshaper
from bidi.algorithm import get_display


def remove_new_line(name: str) -> str:
    """Flatten multi-line cell text."""
    # Simply remove newlines; we will handle reshaping/reordering later
    print(name)
    ret = " ".join(part for part in name.splitlines() if part)
    print('=' * 80)
    print(ret)
    return ret


def normalize_arabic(text: str) -> str:
    """
    Reshape Arabic letters and apply bidi algorithm to convert visual order
    into correct logical order for storage and search.
    """
    # Reshape letters to proper presentation forms
    reshaped = arabic_reshaper.reshape(text)
    # Apply bidi algorithm
    bidi_text = get_display(reshaped)
    return bidi_text


def get_faculty_name(page: pdfplumber.page.Page) -> str:
    """Extract and normalize the faculty name from the header line."""
    raw = page.extract_text() or ""
    match = re.search(r"ﺔﻌﻣﺎﺟ\s+(.*?)\s+ﺔﺒﻠﻄﻟ", raw)
    if not match:
        raise ValueError("Couldn't find faculty pattern on the first page")
    name_visual = match.group(1)
    # Normalize to logical order
    return normalize_arabic(name_visual)


def read_pdf(path: str, is_male: bool = True):
    """
    Parse the given PDF file into a list of Student-like dicts and the faculty name.
    Each student dict has keys: seq_number (int), name (str), national_id (str), is_male (bool).
    Uses national ID as the primary key to prevent duplicates.
    """
    students = []
    with pdfplumber.open(path) as pdf:
        # Extract faculty name once at the start
        faculty_name = get_faculty_name(pdf.pages[0])
        
        # Track unique national IDs and maintain highest sequence number
        unique_national_ids = {}  # national_id -> student_dict
        max_seq_number = 0
        
        # Process all pages in one pass
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                for row in table:
                    # Skip invalid rows early
                    if not row or len(row) < 3 or not row[-1] or not row[-1][0].isdigit():
                        continue
                    
                    # Extract and validate national ID first
                    national_id = row[-3].strip() if row[-3] else ""
                    if not national_id or len(national_id) < 5:  # Basic validation for national ID
                        continue
                    
                    seq_number = int(row[-1])
                    max_seq_number = max(max_seq_number, seq_number)
                    
                    # Process name
                    raw_name = remove_new_line(row[-2])
                    name = normalize_arabic(raw_name)
                    
                    # Create student dict
                    student = {
                        "seq_number": seq_number,
                        "name": name,
                        "raw_name": raw_name,
                        "national_id": national_id,
                        "is_male": is_male,
                        "faculty": faculty_name
                    }
                    
                    # If this national ID is new, add it
                    if national_id not in unique_national_ids:
                        unique_national_ids[national_id] = student
                    else:
                        # If we find a duplicate, keep the one with the lower sequence number
                        existing_student = unique_national_ids[national_id]
                        if seq_number < existing_student["seq_number"]:
                            unique_national_ids[national_id] = student
        
        # Convert dictionary values to list and sort by sequence number
        students = list(unique_national_ids.values())
        students.sort(key=lambda x: x["seq_number"])
        
        # Reassign sequence numbers to ensure they are sequential and unique
        for idx, student in enumerate(students, 1):
            student["seq_number"] = idx

    return students, faculty_name
