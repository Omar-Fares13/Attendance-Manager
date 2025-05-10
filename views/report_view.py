# views/edit_course_data_view.py

import flet as ft
from logic.students import create_students_from_file
from components.banner import create_banner
from logic.file_write import get_student_data, create_excel

# --- Define Colors & Fonts ---
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18"  # Gold/Brown
TEXT_COLOR_DARK = "#333333"  # Dark text for table content
TEXT_COLOR_HEADER = ft.colors.WHITE  # Header text color
TABLE_HEADER_BG = "#5A5A5A"  # Dark grey for header background
TABLE_CELL_BG = ft.colors.with_opacity(0.95, ft.colors.WHITE)  # Almost opaque white for cells
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, PRIMARY_COLOR)  # Use primary color for border
BUTTON_CONFIRM_COLOR = ft.colors.GREEN_700
BUTTON_CANCEL_COLOR = ft.colors.GREY_700
BUTTON_TEXT_COLOR = ft.colors.WHITE

FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

attribs = {}


def create_uneditable_cell(value: str, ref: ft.Ref[ft.TextField]):
    """Creates a pre-styled TextField for DataTable cells with dark text."""
    return ft.Text(
        value=value,
        text_align=ft.TextAlign.RIGHT,
        size=14,
        font_family=FONT_FAMILY_REGULAR,
        color=TEXT_COLOR_DARK,  # Dark text color
        overflow=ft.TextOverflow.ELLIPSIS,
        no_wrap=True
    )


def create_report_view(page: ft.Page):
    """Creates the Flet View for editing extracted course data."""
    headers = ["الاسم", "الرقم المسلسل", "الرقم القومي", "الكلية", "انذارات", "حضور", "ملاحظات", "الحالة"]
    data_rows = get_student_data(page.course_id, page.faculty_id, page.student_name)

    # Remove the absent column data from each row (assuming it was the 6th index)
    data_rows = [row[:6] + row[7:] for row in data_rows]

    text_field_refs = [
        [ft.Ref[ft.TextField]() for _ in range(len(headers))] for _ in range(len(data_rows))
    ]

    # --- Event Handlers ---
    def go_back(e):
        page.go("/report_course")

    def extract_pdf(e):
        print("pdf")

    def extract_xlsx(e):
        # Separate failing and passing students
        failing_students = []
        passing_students = []

        for row in data_rows:
            # Assuming status is the last column (index -1)
            if row[-1] == "راسب":
                failing_students.append(row)
            else:
                passing_students.append(row)

        # Combine with failing students first
        sorted_data = failing_students + passing_students

        # Add a summary row at the top
        summary_row = [
            "",  # Name
            "",  # Serial
            "",  # National ID
            "",  # Faculty
            "",  # Warnings
            "",  # Attendance
            "",  # Notes
            f"إجمالي الراسب: {len(failing_students)} | إجمالي الناجح: {len(passing_students)}"
        ]

        # Create Excel with sorted data
        create_excel(headers, [summary_row] + sorted_data, page.course_name)

    # --- UI Controls ---
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED,
        icon_color=PRIMARY_COLOR,
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    title = ft.Text(
        "تقرير",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY_COLOR,
        font_family=FONT_FAMILY_BOLD,
        text_align=ft.TextAlign.CENTER
    )

    # --- Create DataTable Columns ---
    dt_columns = []
    for header_text in headers:
        dt_columns.append(
            ft.DataColumn(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=8, vertical=10),
                    alignment=ft.alignment.center_right,
                    content=ft.Row(
                        [
                            ft.Text(
                                header_text,
                                color=TEXT_COLOR_HEADER,
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                font_family=FONT_FAMILY_BOLD,
                                text_align=ft.TextAlign.RIGHT,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Icon(ft.icons.EDIT_OUTLINED, color=TEXT_COLOR_HEADER, size=16)
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=5,
                        tight=True,
                    )
                )
            )
        )

    # --- Create DataTable Rows ---
    dt_rows = []
    for r_idx, row_data in enumerate(data_rows):
        dt_cells = []
        for c_idx, cell_value in enumerate(row_data):
            if c_idx < len(text_field_refs[r_idx]):
                tf_ref = text_field_refs[r_idx][c_idx]
                dt_cells.append(
                    ft.DataCell(
                        create_uneditable_cell(cell_value, tf_ref),
                    )
                )
            else:
                dt_cells.append(ft.DataCell(ft.Text("خطأ", color=ft.colors.RED)))

        dt_rows.append(ft.DataRow(
            cells=dt_cells,
            color=TABLE_CELL_BG
        ))

    # --- DataTable Widget ---
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

    # --- Table Container ---
    table_container = ft.Container(
        content=data_table,
        border_radius=ft.border_radius.all(8),
        expand=True
    )

    # --- Action Buttons ---
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
        text="استخراج ملف Excel",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220,
        on_click=extract_xlsx,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    # --- Banner ---
    banner_control = create_banner()

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            # Header with back button
            ft.Container(
                content=ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(top=15, left=30, right=30)
            ),

            # Title
            ft.Container(
                content=title,
                padding=ft.padding.symmetric(horizontal=30),
                alignment=ft.alignment.center
            ),

            # Table container
            table_container,

            # Action buttons at bottom
            ft.Container(height=30),
            ft.Row([excel_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=20
    )

    # --- View Definition ---
    return ft.View(
        route="/report",
        bgcolor=BG_COLOR,
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