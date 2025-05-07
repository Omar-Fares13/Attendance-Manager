# views/edit_course_data_view.py

import flet as ft
from logic.students import create_students_from_file
from components.banner import create_banner 
from logic.file_write import get_student_data, create_excel
# --- Define Colors & Fonts (copy from other views for consistency) ---
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18" # Gold/Brown
TEXT_COLOR_DARK = "#333333" # Dark text for instructions etc.
TABLE_HEADER_BG = "#5A5A5A" # Dark grey for header background
TABLE_HEADER_TEXT = ft.colors.WHITE
TABLE_CELL_BG = ft.colors.with_opacity(0.95, ft.colors.WHITE) # Almost opaque white for cells
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, PRIMARY_COLOR) # Use primary color for border
BUTTON_CONFIRM_COLOR = ft.colors.GREEN_700
BUTTON_CANCEL_COLOR = ft.colors.GREY_700 # For back button if styled like confirm
BUTTON_TEXT_COLOR = ft.colors.WHITE

FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

attribs = {}

# --- Helper to create styled TextField for cells ---
def create_uneditable_cell(value: str, ref: ft.Ref[ft.TextField]):
    """Creates a pre-styled TextField for DataTable cells and assigns a Ref."""
    return ft.Text(
    value = value,
    text_align=ft.TextAlign.RIGHT,
    size=14,
    font_family=FONT_FAMILY_REGULAR,
    overflow=ft.TextOverflow.ELLIPSIS,
    no_wrap=True
    )

def create_report_view(page: ft.Page):
    """Creates the Flet View for editing extracted course data."""

    # --- Retrieve Data Stored from Previous Step (or use defaults) ---
    headers = ["الاسم", "الرقم المسلسل", "الرقم القومي", "الكلية", "انذارات", "حضور", "لم يحضر", "ملاحظات", "الحالة"]
    
    print((page.course_id, page.faculty_id, page.student_name))
    data_rows = get_student_data(page.course_id, page.faculty_id, page.student_name)
    text_field_refs = [
        [ft.Ref[ft.TextField]() for _ in range(len(headers))] for _ in range(len(data_rows))
    ]

    # --- Event Handlers ---
    def go_back(e):
        print("[Edit View] Navigating back to options.")
        # Consider clearing the pending data if going back means cancelling
        # page.client_storage.remove("pending_course_headers")
        # page.client_storage.remove("pending_course_data")
        # page.client_storage.remove("pending_course_name")
        # page.client_storage.remove("pending_course_date") # Also clear date if set
        page.go("/report_course")
    
    def extract_pdf(e):
        print("pdf")
    def extract_xlsx(e):
        create_excel(headers, data_rows, page.course_name)

        
    # --- UI Controls ---
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # RTL back arrow
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
                # Wrap header content in a Container for styling
                ft.Container(
                    # bgcolor=TABLE_HEADER_BG, # Background set on DataTable header_row_color
                    padding=ft.padding.symmetric(horizontal=8, vertical=10),
                    alignment=ft.alignment.center_right, # Align content right
                    content=ft.Row(
                        [
                            ft.Text(
                                header_text,
                                color=TABLE_HEADER_TEXT,
                                weight=ft.FontWeight.BOLD, size=14,
                                font_family=FONT_FAMILY_BOLD,
                                text_align=ft.TextAlign.RIGHT,
                                overflow=ft.TextOverflow.ELLIPSIS, # Handle long headers
                            ),
                            ft.Icon(ft.icons.EDIT_OUTLINED, color=TABLE_HEADER_TEXT, size=16)
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=5,
                        # vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=True, # Reduce spacing around items
                    )
                )
            )
        )

    # --- Create DataTable Rows ---
    dt_rows = []
    for r_idx, row_data in enumerate(data_rows):
        dt_cells = []
        for c_idx, cell_value in enumerate(row_data):
            # Ensure we don't try to access an index out of bounds for refs
            if c_idx < len(text_field_refs[r_idx]):
                tf_ref = text_field_refs[r_idx][c_idx]
                dt_cells.append(
                    ft.DataCell(
                        create_uneditable_cell(cell_value, tf_ref),
                        # tap_handler=lambda e: print(f"Cell ({r_idx},{c_idx}) tapped"), # Optional: Handle tap
                    )
                )
            else:
                # Fallback for inconsistent data/headers (should ideally not happen)
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
        sort_ascending=True, # Default sort state (can be made functional later)
        heading_row_color=TABLE_HEADER_BG,
        heading_row_height=50,
        data_row_max_height=50, # Limit row height
        # column_spacing=20, # Adjust spacing between columns
        divider_thickness=0, # Set to 0 if using lines property
        horizontal_margin=10,
        show_checkbox_column=False,
        expand=True # Allows table to expand within its container
    )

    # --- Confirmation Button ---
    pdf_button = ft.ElevatedButton(
        text="استخراج ملف PDF",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220, # Wider button
        on_click=extract_pdf,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    excel_button = ft.ElevatedButton(
        text="استخراج ملف Excel",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220, # Wider button
        on_click=extract_xlsx,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    # --- Get Banner ---
    banner_control = create_banner()

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            # Top structure: Back button, Titles, Instruction
             ft.Container(
                 content=ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                 padding=ft.padding.only(top=15, left=30, right=30)
             ),
             ft.Container(height=5),
             title,
             # DataTable needs horizontal scrolling capability
             ft.Row(
                 [
                     ft.Container( # Wrap DataTable for potential horizontal scroll
                        content=data_table,
                        border_radius=ft.border_radius.all(8), # Clip content
                        expand=True, # Take available horizontal space
                     )
                 ],
                 scroll=ft.ScrollMode.ADAPTIVE, # Enable horizontal scroll if needed
                 expand=True, # Allow row to take space for scrolling
             ),

             ft.Container(height=30), # Spacer before button

             # Confirmation Button centered at bottom
             ft.Row(
                 [excel_button],
                 alignment=ft.MainAxisAlignment.CENTER
             ),

             ft.Container(height=30), # Bottom padding
        ],
        # expand=True, # Column itself takes vertical space
        scroll=ft.ScrollMode.ADAPTIVE, # Make the main column scrollable vertically
        horizontal_alignment=ft.CrossAxisAlignment.CENTER # Center items like title, instruction, button row
    )

    # --- View Definition ---
    return ft.View(
        route="/report", # Route for this view
        bgcolor=BG_COLOR,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    # Wrap the main content in a container for consistent padding maybe?
                    ft.Container(
                        content=content_column,
                        expand=True, # Allow content column to fill space below banner
                        padding=ft.padding.only(left=30, right=30, bottom=20) # Add some horizontal padding
                    )
                ],
                expand=True, # Fill the entire view height
                spacing=0 # No space between banner and content container
            )
        ]
    )