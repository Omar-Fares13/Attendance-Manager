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
    """
    students = []
    with pdfplumber.open(path) as pdf:
        faculty_name = get_faculty_name(pdf.pages[0])

        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                for row in table:
                    # assume last cell is seq_number if it starts with a digit
                    if row and row[-1] and row[-1][0].isdigit():
                        seq_number = int(row[-1])
                        # raw name may be visual-order; remove newlines then normalize
                        raw_name = remove_new_line(row[-2])
                        name = normalize_arabic(raw_name)
                        national_id = row[-3]
                        students.append({
                            "seq_number": seq_number,
                            "name":        name,
                            "raw_name" : raw_name,
                            "national_id": national_id,
                            "is_male":     is_male,
                            "faculty": faculty_name
                        })

        # sort and dedupe as before
        students.sort(key=lambda x: x["seq_number"])
        unique_ids = set()
        duplicates = []
        max_id = 0
        for student in students:
            if student['seq_number'] in unique_ids:
                duplicates.append(student)
            else:
                unique_ids.add(student['seq_number'])
                if student['seq_number'] > max_id:
                    max_id = student['seq_number']
        clean_students = [s for s in students if s not in duplicates]
        new_id = max_id + 1
        for duplicate in duplicates:
            duplicate['seq_number'] = new_id
            clean_students.append(duplicate)
            new_id += 1

    return clean_students, faculty_name
