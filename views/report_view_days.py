# views/report_view_days.py

import flet as ft

from logic import course
from logic.students import create_students_from_file
from components.banner import create_banner
from logic.file_write import create_excel, get_student_data
from logic.attendance import get_attendance_by_student_id
from datetime import date, time, timedelta

# --- Define Colors & Fonts ---
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18"
TEXT_COLOR_DARK = "#333333"
TEXT_COLOR_HEADER = ft.colors.WHITE
TABLE_HEADER_BG = "#5A5A5A"
TABLE_CELL_BG = ft.colors.with_opacity(0.95, ft.colors.WHITE)
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, PRIMARY_COLOR)
BUTTON_CONFIRM_COLOR = ft.colors.GREEN_700
BUTTON_CANCEL_COLOR = ft.colors.GREY_700
BUTTON_TEXT_COLOR = ft.colors.WHITE

FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

attribs = {}

content_ref = ft.Ref[ft.Column]()


def create_uneditable_cell(value: str, ref: ft.Ref[ft.TextField]):
    return ft.Text(
        value=value,
        text_align=ft.TextAlign.RIGHT,
        size=14,
        font_family=FONT_FAMILY_REGULAR,
        color=TEXT_COLOR_DARK,
        overflow=ft.TextOverflow.ELLIPSIS,
        no_wrap=True
    )


def create_report_alt_view(page: ft.Page):
    # Define the start and end dates for the report (you might want to make this dynamic)
    start_date = date(2025, 5, 10)  # Example start date (Saturday)
    end_date = date(2025, 5, 16)  # Example end date (Friday)
    delta = timedelta(days=1)
    current_date = start_date
    report_dates = {}
    day_names = ["سبت", "أحد", "اتنين", "ثلاثاء", "أربعاء", "خميس", "جمعة"]

    headers = ["م", "الاسم", "الرقم القومي"]
    while current_date <= end_date:
        day_index = current_date.weekday()
        if day_index < 6:  # Exclude Friday (weekday 4 is Thursday, 5 is Friday)
            day_name = day_names[day_index]
            headers.extend([f"{day_name} حضور", f"{day_name} انصراف"])
            report_dates[current_date] = day_name
        current_date += delta

    data_rows = get_student_data(page.course_id, page.faculty_id, page.student_name)
    processed_data_rows = []

    for row in data_rows:
        student_id = row[0]  # Assuming student ID is the first element
        student_name = row[1]
        national_id = row[2]
        attendance_records = get_attendance_by_student_id(student_id)
        student_data = [student_id, student_name, national_id]
        attendance_by_date = {record.date: record for record in attendance_records}

        for report_date in report_dates:
            arrival = None
            leave = None
            if report_date in attendance_by_date:
                arrival = attendance_by_date[report_date].arrival_time.strftime("%H:%M")
                if attendance_by_date[report_date].leave_time:
                    leave = attendance_by_date[report_date].leave_time.strftime("%H:%M")
            student_data.extend([arrival or "", leave or ""])
        processed_data_rows.append(student_data)

    text_field_refs = [
        [ft.Ref[ft.TextField]() for _ in headers] for _ in processed_data_rows
    ]

    def go_back(e):
        page.go("/report_course")

    def extract_pdf(e):
        print("PDF extraction for alt view")

    def extract_xlsx(e):
        # Modify this to use the new headers and processed data
        failing_students_indices = [-2]  # Assuming the failing status is still in the second to last column
        failing_students = [row for row in processed_data_rows if any(row[i] == "راسب" for i in failing_students_indices)]
        passing_students = [row for row in processed_data_rows if not any(row[i] == "راسب" for i in failing_students_indices)]

        sorted_data = failing_students + passing_students

        summary_row = ["-" for _ in headers]
        # You might need to adjust the index based on where the pass/fail status is now
        summary_row[3] = f"إجمالي الراسب: {len(failing_students)} | إجمالي الناجح: {len(passing_students)}" # Adjust index

        create_excel(headers,sorted_data, page.course_name + "_بالايام")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED,
        icon_color=PRIMARY_COLOR,
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    title = ft.Text(
        "تقرير مفصل بالايام",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY_COLOR,
        font_family=FONT_FAMILY_BOLD,
        text_align=ft.TextAlign.CENTER
    )

    dt_columns = [
        ft.DataColumn(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=10),
                alignment=ft.alignment.center_right,
                content=ft.Text(
                    header_text,
                    color=TEXT_COLOR_HEADER,
                    weight=ft.FontWeight.BOLD,
                    size=14,
                    font_family=FONT_FAMILY_BOLD,
                    text_align=ft.TextAlign.RIGHT,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            )
        ) for header_text in headers
    ]

    dt_rows = []

    for r_idx, row_data in enumerate(processed_data_rows):
        dt_cells = []
        for c_idx, cell_value in enumerate(row_data):
            tf_ref = text_field_refs[r_idx][c_idx]
            dt_cells.append(ft.DataCell(create_uneditable_cell(str(cell_value), tf_ref)))
        dt_rows.append(ft.DataRow(cells=dt_cells, color=TABLE_CELL_BG))

    data_table = ft.DataTable(
        columns=dt_columns,
        rows=dt_rows,
        border=ft.border.all(1, TABLE_BORDER_COLOR),
        border_radius=ft.border_radius.all(8),
        vertical_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        horizontal_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        sort_ascending=True,
        heading_row_color=TABLE_HEADER_BG,
        heading_row_height=50,
        data_row_max_height=50,
        divider_thickness=0,
        horizontal_margin=10,
        show_checkbox_column=False,
    )

    table_container = ft.Container(
        content=data_table,
        border_radius=ft.border_radius.all(8),
        expand=True
    )

    pdf_button = ft.ElevatedButton(
        text="استخراج ملف PDF",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220,
        on_click=extract_pdf,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    excel_button = ft.ElevatedButton(
        key="confirm_section",
        text="استخراج ملف Excel",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220,
        on_click=extract_xlsx,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    scroll_down_fab = ft.FloatingActionButton(
        icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
        tooltip="اذهب إلى الأسفل",
        on_click=lambda e: content_ref.current.scroll_to(
            key="confirm_section",
            duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )
    )

    banner_control = create_banner()

    content_column = ft.Column(
        [
            ft.Container(
                content=ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(top=15, left=30, right=30)
            ),
            ft.Container(
                content=title,
                padding=ft.padding.symmetric(horizontal=30),
                alignment=ft.alignment.center
            ),
            table_container,
            ft.Container(height=30),
            ft.Row([excel_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
        ],
        ref=content_ref,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=20
    )

    return ft.View(
        route="/report_alt",
        bgcolor=BG_COLOR,
        floating_action_button=scroll_down_fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(
                        content=content_column,
                        expand=True,
                        padding=ft.padding.only(left=30, right=30, bottom=20)
                    )
                ],
                expand=True,
                spacing=0
            )
        ]
    )