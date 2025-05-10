from logic.students import get_students

def get_student_data(course_id, faculty_id = None, student_name = None):
    attribs = {'course_id' : course_id}
    if faculty_id:
        attribs['faculty_id'] = faculty_id
    if student_name:
        attribs['name'] = student_name
    print("Looking up students with " + "=" * 30)
    print(attribs)
    students = get_students(attribs)
    return format_students(students)

def get_warnings(student):
    warnings = 0
    for note in student.notes:
        if note.is_warning:
            warnings = warnings + 1
    return warnings

def get_notes(std):
    final_notes = ""
    for note in std.notes:
        if final_notes:
            final_notes += '|'
        final_notes += note.note
    return final_notes

def format_students(students):
    formated_students = [
        [std.name,
         std.seq_number,
         std.national_id,
         std.faculty.name,
         get_warnings(std),
         len(std.attendance),
         len(std.attendance) - 12,
         get_notes(std),
         "ناجح" if len(std.attendance) >= 10 else "راسب"
        ]
        for std in students
    ]
    for i in range(len(formated_students)):
        formated_students[i][1] = str(formated_students[i][1])
        formated_students[i][6] -= formated_students[i][5]
    return formated_students

import os

# PDF deps
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# Arabic shaping/BiDi
import arabic_reshaper
from bidi.algorithm import get_display

# Excel deps
import pandas as pd


def _reshape_if_arabic(text: str) -> str:
    """
    Reshape and apply BiDi if the string contains Arabic letters.
    Otherwise returns the original text.
    """
    if any("\u0600" <= ch <= "\u06FF" for ch in text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text


def create_pdf(headers: list[str], rows: list[list], course_name: str) -> None:
    """
    Create a PDF file with a table of the given headers and rows.
    Saves to data/{course_name}.pdf

    Note: Uses ReportLab's default font. PDF viewers will typically substitute
    in a system Arabic font when rendering.
    """
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", f"{course_name}.pdf")

    # reshape all text for proper Arabic joining/RTL
    data = [
        [ _reshape_if_arabic(h) for h in headers ]
    ] + [
        [ _reshape_if_arabic(str(cell)) for cell in row ]
        for row in rows
    ]

    # build PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    tbl = Table(data)

    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgrey),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN",       (0, 0), (-1, -1), "RIGHT"),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),  # default font
    ]))

    doc.build([tbl])
    print(f"PDF exported to {file_path}")


def create_excel(headers: list[str], rows: list[list], course_name: str) -> None:
    """
    Create an Excel file with the given headers and rows.
    Saves to data/{course_name}.xlsx
    """
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", f"{course_name}.xlsx")

    # Build DataFrame and write out
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(file_path, index=False)
    print(f"Excel exported to {file_path}")
