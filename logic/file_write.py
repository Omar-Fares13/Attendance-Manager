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
        [std.seq_number,
         std.name,
         std.national_id,
         std.faculty.name,
         get_warnings(std),
         len(std.attendance),
         12 - len(std.attendance),
         "ناجح" if len(std.attendance) >= 10 else "راسب",
         get_notes(std),
        ]
        for std in students
    ]
    for i in range(len(formated_students)):
        formated_students[i][1] = str(formated_students[i][1])
        formated_students[i][6] -= formated_students[i][5]
    return formated_students



import os
import pandas as pd


def extract_xlsx(e, page, report_dates, processed_data, headers):
    """
    Extract attendance data to Excel file
    
    Args:
        e: Event from button click
        page: Flet page object
        report_dates: List of dates in the report
        processed_data: List of dictionaries containing student data
        headers: List of column headers
    """
    # Initialize data rows for Excel
    excel_rows = []
    
    # Track attendance statistics
    attendance_threshold = 8  # Students need to attend at least 8 days to pass (configurable)
    
    # Process each student's data
    for student in processed_data:
        # Count attended days (at least arrival or departure time recorded)
        attended_days = sum(1 for date in report_dates if 
                          date in student['attendance'] and 
                          (student['attendance'][date].get('arrival') or 
                           student['attendance'][date].get('departure')))
        
        # Determine pass/fail status based on attendance threshold
        status = "ناجح" if attended_days >= attendance_threshold else "راسب"
        
        # Create row for this student with all columns
        row = [
            student['seq'],
            student['name'],
            student['faculty']
        ]
        
        # Add attendance for each date
        for date in report_dates:
            if date in student['attendance']:
                attendance = student['attendance'][date]
                arrival = attendance.get('arrival', '')
                departure = attendance.get('departure', '')
                row.append(f"{arrival}/{departure}" if arrival or departure else "غائب")
            else:
                row.append("غائب")  # Absent
        
        # Add attendance status and count
        row.append(status)
        row.append(f"{attended_days}/{len(report_dates)}")
        
        excel_rows.append(row)
    
    # Separate passing and failing students
    failing_students = [row for row in excel_rows if row[-2] == "راسب"]
    passing_students = [row for row in excel_rows if row[-2] == "ناجح"]
    
    # Sort: failing students first, then passing students
    sorted_data = failing_students + passing_students
    
    # Create extended headers with status columns
    extended_headers = headers.copy()
    extended_headers.append("الحالة")  # Status column
    extended_headers.append("أيام الحضور")  # Attendance days count
    
    # Add summary row
    summary_row = ["-" for _ in extended_headers]
    summary_row[-2] = f"إجمالي الراسب: {len(failing_students)} | إجمالي الناجح: {len(passing_students)}"
    
    # Add summary row to data
    if sorted_data:
        sorted_data.append(summary_row)
    
    # Get course name from page or use default
    course_name = getattr(page, 'course_name', 'attendance_report') + "_بالايام"
    
    # Call function to create Excel file
    create_excel(extended_headers, sorted_data, course_name)
    
    # Show success message (could use a Flet snackbar here)
    print(f"تم استخراج ملف Excel: {course_name}")


def create_excel(headers: list[str], rows: list[list], course_name: str) -> None:
    """
    Create an Excel file with the given headers and rows.
    
    Args:
        headers: List of column headers
        rows: List of data rows
        course_name: Name of the course (used in filename)
    """
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", f"{course_name}.xlsx")

    # Build DataFrame and write out
    df = pd.DataFrame(rows, columns=headers)
    
    # Create a writer with xlsxwriter engine for more formatting options
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='تقرير الحضور')
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['تقرير الحضور']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#5A5A5A',
            'font_color': 'white',
            'border': 1
        })
        
        present_format = workbook.add_format({
            'bg_color': '#E0F2E9',  # Light green
            'border': 1
        })
        
        absent_format = workbook.add_format({
            'bg_color': '#FADBD8',  # Light red
            'border': 1
        })
        
        fail_format = workbook.add_format({
            'bg_color': '#FADBD8',  # Light red
            'bold': True,
            'border': 1
        })
        
        pass_format = workbook.add_format({
            'bg_color': '#E0F2E9',  # Light green
            'bold': True,
            'border': 1
        })
        
        # Apply formats
        for col_num, value in enumerate(headers):
            worksheet.write(0, col_num, value, header_format)
        
        # Format data cells
        for row_num, row_data in enumerate(rows):
            for col_num, cell_value in enumerate(row_data):
                # Skip header row
                if row_num == 0:
                    continue
                    
                # Format based on content
                if col_num >= 3 and col_num < len(headers) - 2:
                    # Attendance cells
                    if cell_value != "غائب" and cell_value != "-":
                        worksheet.write(row_num + 1, col_num, cell_value, present_format)
                    else:
                        worksheet.write(row_num + 1, col_num, cell_value, absent_format)
                elif col_num == len(headers) - 2:
                    # Status column
                    if cell_value == "ناجح":
                        worksheet.write(row_num + 1, col_num, cell_value, pass_format)
                    elif cell_value == "راسب":
                        worksheet.write(row_num + 1, col_num, cell_value, fail_format)
                    else:
                        worksheet.write(row_num + 1, col_num, cell_value)
                else:
                    worksheet.write(row_num + 1, col_num, cell_value)
        
        # Auto-adjust column widths
        for i, width in enumerate([10, 20, 15] + [12] * (len(headers) - 5) + [10, 10]):
            worksheet.set_column(i, i, width)
    
    print(f"Excel exported to {file_path}")