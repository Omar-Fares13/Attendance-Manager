import re
from io import BytesIO
import pdfplumber

def remove_new_line(name: str) -> str:
    """Flatten multi-line cell text and restore order."""
    parts, cur = [], ""
    for ch in name:
        if ch == "\n":
            if cur:
                parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        parts.append(cur)
    # parts were collected in visual order bottom→top, so reverse:
    return " ".join(parts[::-1])

def get_faculty_name(page: pdfplumber.page.Page) -> str:
    """Extract and reverse the faculty name from the header line."""
    text = page.extract_text() or ""
    match = re.search(r"ﺔﻌﻣﺎﺟ\s+(.*?)\s+ﺔﺒﻠﻄﻟ", text)
    if not match:
        raise ValueError("Couldn't find faculty pattern on the first page")
    # reverse the captured group to fix RTL logical→visual
    return match.group(1)[::-1]

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
                        name        = remove_new_line(row[-2])[::-1]
                        national_id = row[-3]
                        students.append({
                            "seq_number": seq_number,
                            "name":        name,
                            "national_id": national_id,
                            "is_male":     is_male
                        })

    return students, faculty_name

if __name__ == "__main__":
    pdf_path = "military_data.pdf"  # make sure this file is in the same folder
    students, faculty = read_pdf(pdf_path)

    print("Faculty:", faculty)
    print(f"Parsed {len(students)} students:\n")
    for s in students:
        print(f" Seq: {s['seq_number']} | Name: {s['name']} | ID: {s['national_id']}")
