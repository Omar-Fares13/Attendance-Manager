# views/search_student_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset # Only needed if using specific assets later
from models import Student, Faculty
from logic.students import get_students, get_student_by_id
from logic.course import get_latest_course
from logic.file_reader import normalize_arabic
search_attributes = {}

# --- Helper Function for Search TextFields ---
def create_search_field(label: str, width: float = None, expand: bool = False, name :str = "", update = None):
    """Creates a styled TextField for search criteria."""
    return ft.TextField(
        data = name,
        label=label,
        color="#000000",
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18", size=14), # Gold label
        border=ft.InputBorder.UNDERLINE, # Underline border style
        border_color="#B58B18",          # Gold border color
        focused_border_color="#B58B18",  # Gold focus border color
        bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK12), # Very light background
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45, # Control height
        width=width,
        expand=expand,
        on_change = lambda e : update(e.control.data, e.control.value)
    )

# --- Helper for Table Header Cell ---
def create_header_cell(text: str):
    """Creates a styled header cell for the DataTable."""
    return ft.DataColumn(
        ft.Container( # Wrap text in container for background color and padding
            content=ft.Text(
                text,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                size=14,
                text_align=ft.TextAlign.CENTER
            ),
            bgcolor="#B58B18", # Gold background for headers
            padding=ft.padding.symmetric(vertical=10, horizontal=5),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(top_left=8, top_right=8) # Optional rounded top corners
        )
    )

# --- Helper for Table Data Cell ---
def create_data_cell(content: ft.Control):
    """Creates a styled data cell for the DataTable."""
    # Set text color and alignment if content is Text
    if isinstance(content, ft.Text):
        content.color = ft.colors.BLACK87 # Darker, visible text color
        content.text_align = ft.TextAlign.CENTER # Center align text in cell

    return ft.DataCell(
        ft.Container( # Wrap cell content for styling and alignment
            content=content,
            bgcolor=ft.colors.WHITE70, # Light background for data cells
            padding=ft.padding.symmetric(vertical=8, horizontal=5),
            alignment=ft.alignment.center, # Center content (like buttons) in cell
            border_radius=4 # Slight rounding for data cells
        )
    )

# --- Main View Creation Function ---
def create_qr_search_student_view(page: ft.Page):
    """Creates the Flet View for the Search Student screen."""

    # --- Controls ---
    # Back button navigation
    search_attributes['is_male'] = page.is_male == '1'
    search_attributes['course_id'] = get_latest_course(is_male_type = page.is_male).id
    def go_back(e):
        page.go("/register_course_options")
    
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # Looks like back arrow in RTL
        icon_color="#B58B18",
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    # Page Title
    page_title = ft.Text(
        "بحث", # Title "Search"
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#B58B18"
    )

    # --- Search Fields Definition ---
    def search():
        students: List[Student] = get_students(search_attributes)
        rows: List[ft.DataRow] = []   
        for stu in students:
            # action button for this student
            search_button = ft.ElevatedButton(
                data = stu.id,
                text="تصوير",
                bgcolor=ft.colors.ORANGE,
                color=ft.colors.BLACK,
                width=70, height=35,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                tooltip=f"Action for {stu.name}",
                on_click = lambda e : search_data_click(e.control.data)
            )

            # assemble all the cells
            cells = [
                create_data_cell(search_button),
                create_data_cell(ft.Text(stu.name)),
                create_data_cell(ft.Text(stu.national_id)),
                create_data_cell(ft.Text(stu.seq_number)),
                create_data_cell(ft.Text(stu.faculty.name if stu.faculty else "-")),
                create_data_cell(ft.Text(stu.phone_number)),
                create_data_cell(ft.Text(stu.qr_code)),
            ]
            rows.append(ft.DataRow(cells=cells))

        results_table.rows = rows
        results_table.update()

    def update_attribute(name, value):
        if not value:
            search_attributes.pop(name, None)
        else:
            # Normalize Arabic fields so search matches storage
            if name in ("name", "faculty", "qr_code", "national_id"):
                value = normalize_arabic(value)
            search_attributes[name] = value
        search()

        
    national_id_field = create_search_field("البحث باستخدام الرقم القومي", expand=True, update = update_attribute, name = "national_id")
    name_field = create_search_field("البحث باستخدام الاسم", expand=True, update = update_attribute, name = "name")
    

    search_field_row1 = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[name_field, national_id_field]
    )
    phone_field = create_search_field("البحث باستخدام رقم الهاتف", expand=True, update = update_attribute, name = "phone_number")
    serial_field = create_search_field("البحث باستخدام رقم المسلسل", width=200, update = update_attribute, name = "seq_num")
    faculty_field = create_search_field("البحث باستخدام الكلية", width=200, update = update_attribute, name = "faculty")
    
    search_field_row2 = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[phone_field, serial_field, faculty_field]
    )
    qr_field = create_search_field("بحث باستخدام الكيو أر", expand = True, update = update_attribute, name = "qr_code")
    search_field_row3 = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[qr_field]
    )
    search_fields_container = ft.Column(
        controls=[search_field_row1, ft.Container(height=10), search_field_row2, search_field_row3],
        spacing=0 # Let Rows handle internal spacing
    )

    # --- Action Buttons Definition ---
    # Click Handlers (Placeholders - replace with actual logic)
    def add_student_click(e):
        print("Add Student Clicked - Navigate or show form")
        page.go('/add_student')
        # Example: page.go("/add_student_form")

    def add_file_click(e):
        print("Add Students File Clicked - Trigger file picker")
        page.show_snack_bar(ft.SnackBar(ft.Text("فتح نافذة إضافة ملف..."), open=True))
        # Example: Implement file picker logic here

    def search_data_click(student_id : int = 1):
        page.student_id = student_id
        page.go(f"/camera_qr") # Navigate to the edit student view route

    # Button Styling
    button_style = ft.ButtonStyle( shape=ft.RoundedRectangleBorder(radius=8) )
    button_height = 45

    # Button Controls
    add_student_btn = ft.ElevatedButton(
        text="اضافة طالب", icon=ft.icons.PERSON_ADD_ALT_1, bgcolor="#6FA03C", color=ft.Colors.WHITE,
        height=button_height, style=button_style, on_click=add_student_click, tooltip="إضافة طالب جديد بشكل فردي"
    )
    add_file_btn = ft.ElevatedButton(
        text="اضافه ملف طلبه", icon=ft.icons.UPLOAD_FILE, bgcolor="#6FA03C", color=ft.Colors.WHITE,
        height=button_height, style=button_style, on_click=add_file_click, tooltip="إضافة مجموعة طلاب من ملف (Excel, CSV)"
    )
    # Layout for Action Buttons
    action_buttons_row = ft.Row(
        [add_student_btn, add_file_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        wrap=True, # Allow wrapping on small screens
        run_spacing=10
    )
    action_buttons_container = ft.Container(
        content=action_buttons_row,
        padding=ft.padding.only(top=25, bottom=15) # Spacing around buttons
    )

    # --- Results DataTable Definition ---
    # Define Columns
    columns = [
        create_header_cell("اجراء"),      # Action
        create_header_cell("الاسم"),      # Name
        create_header_cell("الرقم القومي"), # National ID
        create_header_cell("رقم المسلسل"), # Serial
        create_header_cell("الكلية"),     # Faculty
        create_header_cell("رقم الهاتف"),  # Phone
        create_header_cell("م."),         # Misc/Notes
    ]


    # Placeholder Data Rows (Replace with dynamic data later)
    rows = []
    results_table = ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.with_opacity(0.5, "#B58B18")), # Subtle gold border
        border_radius=ft.border_radius.all(10),
        vertical_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.2, ft.colors.BLACK)),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.2, ft.colors.BLACK)),
        column_spacing=10, # Adjust spacing
        expand=True # Make table fill horizontal space
    )
    
    # Create the DataTable widget
    

    # --- Get Banner ---
    banner_control = create_banner(page.width)

    # --- Page Content Layout (Column holding all sections) ---
    content_column = ft.Column(
        [
            # Row for Back Button and Title
            ft.Container(
                padding=ft.padding.only(top=15, bottom=15, left=30, right=30),
                content=ft.Row(
                    [page_title, back_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            # Search Fields Area
            ft.Container(
                 padding=ft.padding.symmetric(horizontal=50, vertical=10),
                 content=search_fields_container
            ),
            # Action Buttons Area
            action_buttons_container,
            # DataTable Area (in an expanding container)
            ft.Container(
                padding=ft.padding.symmetric(horizontal=30, vertical=20),
                alignment=ft.alignment.top_center, # Align table within container
                content=results_table,
                expand=True # Allow container to expand vertically
            ),
        ],
        expand=True, # Allow column to fill vertical page space
        scroll=ft.ScrollMode.ADAPTIVE, # Enable scrolling for the whole content column
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Stretch children horizontally
    )
    # --- View Definition ---
    return ft.View(
        route="/search_qr_student", # Route for this view
        padding=0,
        bgcolor="#E3DCCC", # Background color
        controls=[
            ft.Column( # Main page structure: Banner + Content
                [
                    banner_control,
                    content_column
                ],
                expand=True, # Fill page height
                spacing=0 # No space between banner and content
            )
        ]
    )