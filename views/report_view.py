# views/edit_course_data_view.py

import flet as ft
from logic.students import create_students_from_file
from components.banner import create_banner
from logic.file_write import get_student_data, create_excel

# --- Define Colors & Fonts (copy from other views for consistency) ---
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18"  # Gold/Brown
TEXT_COLOR_DARK = "#333333"  # Dark text for instructions etc.
TABLE_HEADER_BG = "#5A5A5A"  # Dark grey for header background
TABLE_HEADER_TEXT = ft.colors.WHITE
TABLE_CELL_BG = ft.colors.with_opacity(0.95, ft.colors.WHITE)  # Almost opaque white for cells
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, PRIMARY_COLOR)  # Use primary color for border
BUTTON_CONFIRM_COLOR = ft.colors.GREEN_700
BUTTON_CANCEL_COLOR = ft.colors.GREY_700  # For back button if styled like confirm
BUTTON_TEXT_COLOR = ft.colors.WHITE

FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

attribs = {}  # Not used in this snippet, can be removed if not used elsewhere


# --- Helper to create styled TextField for cells ---
### CHANGED: Renamed function and modified to create editable TextField ###
# --- Helper to create styled TextField for cells ---
### CHANGED: Renamed function and modified to create editable TextField ###
def create_editable_cell(value: str, ref: ft.Ref[ft.TextField], r_idx: int, c_idx: int, data_source: list):
    """Creates a pre-styled, editable TextField for DataTable cells and assigns a Ref."""

    def on_cell_value_change(e):
        """Updates the underlying data_source when the TextField value changes."""
        if 0 <= r_idx < len(data_source) and 0 <= c_idx < len(data_source[r_idx]):
            data_source[r_idx][c_idx] = e.control.value
            print(f"Data updated at ({r_idx},{c_idx}): {e.control.value}")  # For debugging
        # No page.update() needed here usually, as TextField updates itself visually.
        # Only if other parts of the UI depend on this data_source change immediately.

    return ft.TextField(
        ref=ref,
        value=str(value),  # Ensure value is a string
        text_align=ft.TextAlign.RIGHT,
        text_size=14,
        ### CHANGED: font_family moved into TextStyle ###
        text_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR, color=ft.colors.BLACK),
        # color=ft.colors.BLACK, # Moved into text_style
        border=ft.InputBorder.NONE,  # Make it look like text until focused
        content_padding=ft.padding.symmetric(horizontal=5, vertical=2),  # Adjust padding for TextField
        bgcolor=ft.colors.TRANSPARENT,  # Blend with cell background
        on_change=on_cell_value_change,
    )

def create_report_view(page: ft.Page):
    """Creates the Flet View for editing extracted course data."""

    headers = ["الاسم", "الرقم المسلسل", "الرقم القومي", "الكلية", "انذارات", "حضور", "لم يحضر", "ملاحظات", "الحالة"]

    print((page.course_id, page.faculty_id, page.student_name))
    # --- Retrieve Data Stored ---
    # IMPORTANT: get_student_data should return a list of lists
    # e.g., [["John Doe", "S123"], ["Jane Smith", "S456"]]
    # Make sure each inner list element is a string or can be converted to one.
    data_rows = get_student_data(page.course_id, page.faculty_id, page.student_name)

    # Ensure all data elements are strings, as TextField expects string values
    # Also handles cases where data might be None
    for i in range(len(data_rows)):
        for j in range(len(data_rows[i])):
            if data_rows[i][j] is None:
                data_rows[i][j] = ""
            else:
                data_rows[i][j] = str(data_rows[i][j])

    ### CHANGED: Refs are now for ft.TextField ###
    text_field_refs = [
        [ft.Ref[ft.TextField]() for _ in range(len(headers))] for _ in range(len(data_rows))
    ]

    # --- Event Handlers ---
    def go_back(e):
        print("[Edit View] Navigating back to options.")
        page.go("/report_course")

    def extract_pdf(e):
        # Note: PDF extraction will use the current state of data_rows, including any edits.
        print("PDF extraction initiated with current data.")
        # Implement your PDF creation logic using the (potentially modified) data_rows
        # For example: create_pdf(headers, data_rows, page.course_name)

    def extract_xlsx(e):
        # Excel extraction will also use the current state of data_rows.
        print("XLSX extraction initiated with current data.")
        create_excel(headers, data_rows, page.course_name)
        page.show_snack_bar(ft.SnackBar(ft.Text(f"تم استخراج ملف {page.course_name}.xlsx بنجاح"), open=True))

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
        size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR,
        font_family=FONT_FAMILY_BOLD, text_align=ft.TextAlign.CENTER
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
                                color=TABLE_HEADER_TEXT,
                                weight=ft.FontWeight.BOLD, size=14,
                                font_family=FONT_FAMILY_BOLD,
                                text_align=ft.TextAlign.RIGHT,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            # ft.Icon(ft.icons.EDIT_OUTLINED, color=TABLE_HEADER_TEXT, size=16) # Removed edit icon from header, cells are now editable
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
    for r_idx, row_data_list in enumerate(data_rows):
        dt_cells = []
        for c_idx, cell_value in enumerate(row_data_list):
            if c_idx < len(text_field_refs[r_idx]):
                tf_ref = text_field_refs[r_idx][c_idx]
                ### CHANGED: Using create_editable_cell and passing necessary arguments ###
                editable_cell_widget = create_editable_cell(
                    value=str(cell_value),  # Ensure value is string
                    ref=tf_ref,
                    r_idx=r_idx,
                    c_idx=c_idx,
                    data_source=data_rows  # Pass the main data list for updates
                )
                dt_cells.append(ft.DataCell(editable_cell_widget))
            else:
                dt_cells.append(ft.DataCell(ft.Text("خطأ", color=ft.colors.RED)))

        dt_rows.append(ft.DataRow(cells=dt_cells, color=TABLE_CELL_BG))

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
        data_row_max_height=50,  # Adjust if TextField needs more vertical space
        # data_row_min_height=40, # Might be needed
        divider_thickness=0,
        horizontal_margin=10,
        show_checkbox_column=False,
        expand=True
    )

    # --- Confirmation Buttons ---
    pdf_button = ft.ElevatedButton(
        text="استخراج ملف PDF",
        # icon=ft.icons.PICTURE_AS_PDF, # More specific icon
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,  # Keeping original for now
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220,
        on_click=extract_pdf,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    excel_button = ft.ElevatedButton(
        text="استخراج ملف Excel",
        # icon=ft.icons.GRID_ON, # More specific icon for Excel/sheets
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,  # Keeping original for now
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220,
        on_click=extract_xlsx,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    # --- Get Banner ---
    banner_control = create_banner()

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            ft.Container(
                content=ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(top=15, left=30, right=30)
            ),
            ft.Container(height=5),
            title,
            ft.Row(
                [
                    ft.Container(
                        content=data_table,
                        border_radius=ft.border_radius.all(8),
                        expand=True,
                    )
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True,
            ),
            ft.Container(height=30),
            ft.Row(  # Row for both buttons
                [pdf_button, excel_button],  # Add pdf_button here
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20  # Add some space between buttons
            ),
            ft.Container(height=30),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

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
        ],
        # ADDED: Add the banner to the view's appbar or floating action button if it's meant to be persistent
        # For example, if banner_control is a SnackBar or AlertDialog trigger:
        # floating_action_button=banner_control if it's a button that shows a banner
        # Or ensure banner_control.open = True is called appropriately if it's a SnackBar
        # If create_banner() returns a Banner widget itself (like ft.Banner), then its placement in the column is correct.
    )


# Example of how get_student_data might be structured, ensure it returns list of lists of strings
# def get_student_data(course_id, faculty_id, student_name):
#     # Dummy data for demonstration
#     return [
#         ["أحمد محمد", "1001", "29001010123456", "الهندسة", "0", "10", "0", "طالب منتظم", "ناجح"],
#         ["فاطمة علي", "1002", "29102020123457", "العلوم", "1", "8", "2", "يحتاج متابعة", "معلق"],
#         ["خالد السيد", "1003", "29203030123458", "الآداب", "0", "9", "1", "", "ناجح"],
#     ]

# Example of how create_excel might be structured
# def create_excel(headers, data, course_name):
#     print(f"Creating Excel: {course_name}.xlsx with headers: {headers} and data: {data}")
#     # Actual Excel creation logic would go here (e.g., using openpyxl)
#     # For now, just simulate it:
#     with open(f"{course_name}.xlsx", "w", encoding="utf-8") as f: # Placeholder
#         f.write(str(headers) + "\n")
#         for row in data:
#             f.write(str(row) + "\n")
#     print("Excel file simulated.")
