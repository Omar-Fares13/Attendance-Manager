"""
Excel file generation utilities for student data exports.
Provides functions to format and export student data to Excel files.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import flet as ft

from logic.students import get_students


def get_student_data(course_id: int, faculty_id: Optional[int] = None, 
                     student_name: Optional[str] = None) -> List[List[Any]]:
    """
    Get formatted student data for a course with optional filters.
    
    Args:
        course_id: ID of the course
        faculty_id: Optional ID of the faculty to filter by
        student_name: Optional student name to search for
        
    Returns:
        List of formatted student data rows
    """
    # Build query attributes
    attribs = {'course_id': course_id}
    if faculty_id:
        attribs['faculty_id'] = faculty_id
    if student_name:
        attribs['name'] = student_name
        
    print("Looking up students with " + "=" * 30)
    print(attribs)
    
    # Get and format student data
    students = get_students(attribs)
    return format_students(students)


def get_warnings(student) -> int:
    """Count warning notes for a student."""
    return sum(1 for note in student.notes if note.is_warning)


def get_notes(student) -> str:
    """Concatenate all notes for a student with '|' separator."""
    return '|'.join(note.note for note in student.notes)


def format_students(students) -> List[List[Any]]:
    """Format student objects into rows of data for reports."""
    formatted_students = [
        [std.seq_number,
         str(std.name),  # Ensure name is a string
         std.national_id,
         std.faculty.name,
         get_warnings(std),
         len(std.attendance),
         12 - len(std.attendance),  # Calculate absences based on 12 total days
         "ناجح" if len(std.attendance) >= 10 else "راسب",
         get_notes(std),
        ]
        for std in students
    ]
    
    # Calculate actual absences
    for i in range(len(formatted_students)):
        formatted_students[i][6] = 12 - formatted_students[i][5]
        
    return formatted_students


def extract_xlsx(e: ft.ControlEvent, page: ft.Page, report_dates: List[str], 
                processed_data: List[Dict[str, Any]], headers: List[str]) -> None:
    """
    Extract attendance data to Excel file with user-selected save location.
    
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
    attendance_threshold = 8  # Students need to attend at least 8 days to pass
    
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
    
    # Show file dialog to choose save location
    file_path = show_save_dialog(course_name)
    if file_path:
        # Call function to create Excel file
        create_excel(extended_headers, sorted_data, file_path)
        
        # Show success message using Flet
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"تم استخراج ملف Excel: {os.path.basename(file_path)}")
        )
        page.snack_bar.open = True
        page.update()
    else:
        # User canceled save dialog
        page.snack_bar = ft.SnackBar(
            content=ft.Text("تم إلغاء عملية حفظ الملف")
        )
        page.snack_bar.open = True
        page.update()


def show_save_dialog(default_filename: str) -> Optional[str]:
    """
    Show a file save dialog and return the selected path.
    
    Args:
        default_filename: Default name for the file
        
    Returns:
        Selected file path or None if canceled
    """
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # On some platforms, need to force to foreground
    root.attributes('-topmost', True)
    
    # Show the save file dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=f"{default_filename}.xlsx",
        title="حفظ تقرير Excel"
    )
    
    # Destroy the tkinter instance
    root.destroy()
    
    return file_path if file_path else None


def create_excel(headers: List[str], rows: List[List[Any]], file_path: str) -> None:
    """
    Create an Excel file with the given headers and rows at the specified path.
    
    Args:
        headers: List of column headers
        rows: List of data rows
        file_path: Full path where Excel file should be saved
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Build DataFrame
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
        
        # Apply header format
        for col_num, value in enumerate(headers):
            worksheet.write(0, col_num, value, header_format)
        
        # Format data cells
        for row_num, row_data in enumerate(rows):
            # Skip header row
            row_offset = row_num + 1  # +1 because we have a header row
            
            for col_num, cell_value in enumerate(row_data):
                # Format based on content
                if col_num >= 3 and col_num < len(headers) - 2:
                    # Attendance cells
                    if cell_value != "غائب" and cell_value != "-":
                        worksheet.write(row_offset, col_num, cell_value, present_format)
                    else:
                        worksheet.write(row_offset, col_num, cell_value, absent_format)
                elif col_num == len(headers) - 2:
                    # Status column
                    if cell_value == "ناجح":
                        worksheet.write(row_offset, col_num, cell_value, pass_format)
                    elif cell_value == "راسب":
                        worksheet.write(row_offset, col_num, cell_value, fail_format)
                    else:
                        worksheet.write(row_offset, col_num, cell_value)
                else:
                    worksheet.write(row_offset, col_num, cell_value)
        
        # Auto-adjust column widths
        for i, width in enumerate([10, 20, 15] + [12] * (len(headers) - 5) + [10, 10]):
            worksheet.set_column(i, i, width)
    
    print(f"Excel exported to {file_path}")


if __name__ == "__main__":
    # Test code to run when module is executed directly
    print("This module provides Excel generation functions for the application.")
    print("It should be imported and used by other modules, not run directly.")