# views/edit_course_data_view.py

import flet as ft
import math
from logic.students import create_students_from_file
from components.banner import create_banner # Assuming banner component is reusable
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
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
loading_dialog_ref = ft.Ref[ft.AlertDialog]()
# --- Helper to create styled TextField for cells ---

def create_loading_dialog():
    return ft.AlertDialog(
        ref=loading_dialog_ref,
        modal=True,
        title=ft.Text("جاري تحميل البيانات", text_align=ft.TextAlign.CENTER),
        content=ft.Column(
            [
                ft.ProgressRing(width=50, height=50, stroke_width=3, color=PRIMARY_COLOR),
                ft.Container(height=10),
                ft.Text("يرجى الانتظار بينما يتم تحميل بيانات الدورة...", 
                       text_align=ft.TextAlign.CENTER, 
                       color=TEXT_COLOR_DARK)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            width=300,
            height=120
        ),
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )


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

    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    # ------------------------------------------------------------
    # 0) LOAD DATA
    # ------------------------------------------------------------
    headers = ["الاسم", "الرقم المتسلسل", "الرقم القومي", "الكلية"]
    attribs['is_male'] = (page.file_students)['students'][0]['is_male']
    attribs['date']    = page.file_students['date']

    data_rows_source = [
        [stu['name'], stu['seq_number'], stu['national_id'], stu['faculty']]
        for stu in page.file_students['students']
    ]
    raw_names = [stu['raw_name'] for stu in page.file_students['students']]
    course_file_name = page.client_storage.get("pending_course_name") or "ملف غير محدد"

    # ------------------------------------------------------------
    # 1)  PAGINATION STATE
    # ------------------------------------------------------------
    ROWS_PER_PAGE = 25
    current_page  = 0
    total_pages   = max(1, math.ceil(len(data_rows_source) / ROWS_PER_PAGE))

    # ------------------------------------------------------------
    # 2) CREATE REFS & ALL DataRow OBJECTS ONCE
    # ------------------------------------------------------------
    text_field_refs = [
        [ft.Ref[ft.TextField]() for _ in headers] for _ in data_rows_source
    ]

    def build_all_rows():
        all_rows = []
        for r_idx, row_data in enumerate(data_rows_source):
            cells = []
            for c_idx, cell_value in enumerate(row_data):
                tf_ref = text_field_refs[r_idx][c_idx]
                cells.append(ft.DataCell(create_editable_cell(cell_value, tf_ref)))
            all_rows.append(ft.DataRow(cells=cells, color=TABLE_CELL_BG))
        return all_rows

    all_rows = build_all_rows()

    def slice_rows(idx: int):
        start, end = idx * ROWS_PER_PAGE, (idx + 1) * ROWS_PER_PAGE
        return all_rows[start:end]
    
    # ------------------------------------------------------------
    # 3) DataTable – initialised with first slice only
    # ------------------------------------------------------------
    dt_columns = [
        ft.DataColumn(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=10),
                alignment=ft.alignment.center_right,
                content=ft.Row(
                    [
                        ft.Text(h, color=TABLE_HEADER_TEXT, weight=ft.FontWeight.BOLD,
                                size=14, font_family=FONT_FAMILY_BOLD,
                                text_align=ft.TextAlign.RIGHT,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Icon(ft.icons.EDIT_OUTLINED, color=TABLE_HEADER_TEXT, size=16)
                    ],
                    alignment=ft.MainAxisAlignment.END, spacing=5, tight=True
                )
            )
        ) for h in headers
    ]

    data_table = ft.DataTable(
        columns=dt_columns,
        rows=slice_rows(current_page),
        border=ft.border.all(1, TABLE_BORDER_COLOR),
        border_radius=ft.border_radius.all(8),
        vertical_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        horizontal_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        heading_row_color=TABLE_HEADER_BG,
        heading_row_height=50,
        data_row_max_height=50,
        divider_thickness=0,
        horizontal_margin=10,
        show_checkbox_column=False,
        expand=True
    )

    # ------------------------------------------------------------
    # 4) PAGINATION NAVIGATION BAR
    # ------------------------------------------------------------
    page_label = ft.Text(f"{current_page+1} / {total_pages}",
                         size=16, weight=ft.FontWeight.BOLD)

    def refresh_table():
        nonlocal current_page
        current_page = max(0, min(current_page, total_pages - 1))
        data_table.rows = slice_rows(current_page)
        page_label.value = f"{current_page+1} / {total_pages}"
        page.update()

    def next_page(e):
        nonlocal current_page
        if current_page < total_pages - 1:
            current_page += 1
            refresh_table()

    def prev_page(e):
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            refresh_table()

    nav_bar = ft.Row(
        [
            ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="السابق", on_click=prev_page),
            page_label,
            ft.IconButton(icon=ft.icons.CHEVRON_LEFT, tooltip="التالي", on_click=next_page),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=total_pages > 1
    )

    # ------------------------------------------------------------
    # 5) EVENT HANDLERS
    # ------------------------------------------------------------
    def go_back(e):
        page.routes = ['/dashboard']
        page.go("/register_course_options")

    def proceed_to_confirmation(e):
        # Show loading dialog
        page.dialog = loading_dialog_ref.current
        loading_dialog_ref.current.open = True
        page.update()
        
        # Define the processing function
        def do_processing():
            updated_data = []

            for r_idx, row_refs in enumerate(text_field_refs):
                row_values = []
                for rf in row_refs:
                    if rf.current:
                        raw_val = rf.current.value          # could be str or int or None
                        cleaned = str(raw_val).strip()      # cast to str, then strip
                    else:
                        cleaned = ""
                    row_values.append(cleaned)

                std = dict(
                    name        = row_values[0],
                    raw_name    = raw_names[r_idx],
                    seq_number  = row_values[1],
                    national_id = row_values[2],
                    faculty     = row_values[3],
                    is_male     = attribs['is_male'],
                )
                updated_data.append(std)

            # Create students - this is the time-consuming operation
            create_students_from_file(updated_data,
                                    attribs['date'],
                                    attribs['is_male'])
            
            # Navigation will handle closing the dialog
            page.routes = []
            page.go("/dashboard")
        
        # Use a timer to allow the dialog to render before starting processing
        import threading
        threading.Timer(0.1, do_processing).start()
        

    # ------------------------------------------------------------
    # 6) UI CONTROLS (unchanged except we insert nav_bar)
    # ------------------------------------------------------------
    scroll_down_fab = ft.FloatingActionButton(
        icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
        tooltip="اذهب إلى الأسفل",
        on_click=lambda e: content_ref.current.scroll_to(
            key="confirm_section", duration=400, curve=ft.AnimationCurve.EASE_IN_OUT)
    )

    back_button = ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED,
                                on_click=go_back, icon_size=30,
                                icon_color=PRIMARY_COLOR, tooltip="العودة")

    title = ft.Text("تسجيل دورة جديدة", size=32, weight=ft.FontWeight.BOLD,
                    color=PRIMARY_COLOR, font_family=FONT_FAMILY_BOLD,
                    text_align=ft.TextAlign.CENTER)

    subtitle = ft.Text(f"تعديل الملف المرفوع: {course_file_name}",
                       size=20, weight=ft.FontWeight.W_500,
                       color=TEXT_COLOR_DARK, font_family=FONT_FAMILY_REGULAR,
                       text_align=ft.TextAlign.CENTER)

    instruction_text = ft.Row(
        [
            ft.Text("يرجى التأكد من تطابق عناوين الأعمدة مع النموذج المطلوب ومراجعة البيانات قبل المتابعة.",
                    size=14, color=TEXT_COLOR_DARK,
                    font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.RIGHT,
                    expand=True),
            ft.Icon(ft.icons.VISIBILITY_OUTLINED, color=PRIMARY_COLOR, size=24),
        ],
        alignment=ft.MainAxisAlignment.END, spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER, width=800
    )

    confirm_button = ft.ElevatedButton(
        key="confirm_section", text="تأكيد ومتابعة",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR, color=BUTTON_TEXT_COLOR,
        height=50, width=220, on_click=proceed_to_confirmation,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    # --- Get Banner ---
    banner_control = create_banner()
    loading_dialog = create_loading_dialog()
    page.overlay.append(loading_dialog)
    # ------------------------------------------------------------
    # 7) PAGE LAYOUT
    # ------------------------------------------------------------
    content_column = ft.Column(
        [
            ft.Container(ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                         padding=ft.padding.only(top=15, left=30, right=30)),
            title,
            subtitle,
            ft.Container(height=20),
            instruction_text,
            ft.Container(height=20),

            # DataTable (with horizontal scroll) + nav bar
            ft.Row(
                [ft.Container(content=data_table, border_radius=ft.border_radius.all(8), expand=True)],
                scroll=ft.ScrollMode.ADAPTIVE, expand=True),
            nav_bar,

            ft.Container(height=30),
            ft.Row([confirm_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
        ],
        ref=content_ref,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- View Definition ---
    return ft.View(
        route="/edit_course_data",
        bgcolor=BG_COLOR,
        floating_action_button=scroll_down_fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(content=content_column,
                                 expand=True,
                                 padding=ft.padding.only(left=30, right=30, bottom=20))
                ],
                expand=True, spacing=0
            )
        ]
    )