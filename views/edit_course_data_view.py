# views/edit_course_data_view.py

import flet as ft
from logic.students import create_students_from_file
from components.banner import create_banner # Assuming banner component is reusable
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
raw_names = []
content_ref = ft.Ref[ft.Column]()
# --- Helper to create styled TextField for cells ---
def create_editable_cell(value: str, ref: ft.Ref[ft.TextField]):
    """Creates a pre-styled TextField for DataTable cells and assigns a Ref."""
    return ft.TextField(
        ref=ref, # Assign the passed Ref object
        value=value,
        text_align=ft.TextAlign.RIGHT,
        # Styling to make it look like part of the table cell
        border=ft.InputBorder.NONE, # No border
        color="#000000",
        filled=True,
        bgcolor=ft.colors.TRANSPARENT, # Let the cell background show through
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8), # Adjust padding
        text_size=14,
        expand=True, # Take available space in cell
        cursor_color=PRIMARY_COLOR, # Themed cursor
        height=40, # Ensure a minimum height for consistency
        text_vertical_align=ft.VerticalAlignment.CENTER,
    )

def create_edit_course_data_view(page: ft.Page):
    """Creates the Flet View for editing extracted course data."""

    print("[Edit View] Loading data...")
    # --- Retrieve Data Stored from Previous Step (or use defaults) ---
    headers = ["الاسم", "الرقم المتسلسل", "الرقم القومي", "الكلية"]
    attribs['is_male'] = (page.file_students)['students'][0]['is_male']
    attribs['date'] = page.file_students['date']
    data_rows = [[std['name'], std['seq_number'], std['national_id'], std['faculty']] for std in (page.file_students)['students']]
    raw_names = [std['raw_name']  for std in page.file_students['students']]
    course_file_name = page.client_storage.get("pending_course_name") or "ملف غير محدد"

    # --- Create refs for all TextFields ---
    # This creates a 2D list of Refs, matching the structure of data_rows
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
        page.routes = ['/dashboard']
        page.go("/register_course_options")

    def proceed_to_confirmation(e):
        print("[Edit View] Proceeding to confirmation.")
        # --- 1. Read data from TextFields ---
        updated_data = []
        for r_idx, row_refs in enumerate(text_field_refs):
            current_row_data = []
            for c_idx, tf_ref in enumerate(row_refs):
                if tf_ref.current:
                    # Get value, strip whitespace, default to empty string if None
                    value = tf_ref.current.value or ""
                    try:
                        value = value.strip()
                    except:
                        value = value
                    current_row_data.append(value)
            std = {'name' : current_row_data[0], 'raw_name' : raw_names[r_idx], 'seq_number' : current_row_data[1], 'national_id' : current_row_data[2], 'faculty' : current_row_data[3], 'is_male' : attribs['is_male']}
            
            updated_data.append(std)
        create_students_from_file(updated_data, attribs['date'], attribs['is_male'])
        # --- 3. Navigate ---
        page.routes = []
        page.go("/dashboard")


    # --- UI Controls ---
    
    scroll_down_fab = ft.FloatingActionButton(
    icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
    tooltip="اذهب إلى الأسفل",
    on_click=lambda e: content_ref.current.scroll_to(
        key="confirm_section",
        duration=400,
        curve=ft.AnimationCurve.EASE_IN_OUT
        )
    )

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # RTL back arrow
        icon_color=PRIMARY_COLOR,
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    title = ft.Text(
        "تسجيل دورة جديدة",
        size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR,
        font_family=FONT_FAMILY_BOLD, text_align=ft.TextAlign.CENTER
    )
    subtitle = ft.Text(
        f"تعديل الملف المرفوع: {course_file_name}", # Show the source file name being edited
        size=20, weight=ft.FontWeight.W_500, color=TEXT_COLOR_DARK,
        font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.CENTER
    )

    instruction_text = ft.Row(
        [
            ft.Text(
                # Shortened instruction for clarity
                "يرجى التأكد من تطابق عناوين الأعمدة مع النموذج المطلوب ومراجعة البيانات قبل المتابعة.",
                size=14, color=TEXT_COLOR_DARK, font_family=FONT_FAMILY_REGULAR,
                text_align=ft.TextAlign.RIGHT, expand=True
            ),
            ft.Icon(ft.icons.VISIBILITY_OUTLINED, color=PRIMARY_COLOR, size=24),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        # Limit width and add padding
        width=800, # Adjust as needed
        # padding=ft.padding.symmetric(horizontal=50) # Add padding if needed
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
                        create_editable_cell(cell_value, tf_ref),
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
    confirm_button = ft.ElevatedButton(
        key="confirm_section",     # ← this is your target
        text="تأكيد ومتابعة",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220, # Wider button
        on_click=proceed_to_confirmation,
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
             ft.Container(height=5),
             subtitle,
             ft.Container(height=20),
             instruction_text,
             ft.Container(height=20),

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
                 [confirm_button],
                 alignment=ft.MainAxisAlignment.CENTER
             ),

             ft.Container(height=30), # Bottom padding
        ],
        # expand=True, # Column itself takes vertical space
        ref=content_ref,
        scroll=ft.ScrollMode.ADAPTIVE, # Make the main column scrollable vertically
        horizontal_alignment=ft.CrossAxisAlignment.CENTER # Center items like title, instruction, button row
    )

    # --- View Definition ---
    return ft.View(
        route="/edit_course_data", # Route for this view
        bgcolor=BG_COLOR,
        floating_action_button=scroll_down_fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
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