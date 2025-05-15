# views/search_student_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset  # Only needed if using specific assets later
from models import Student, Faculty
from logic.students import get_students, get_student_by_id, delete_student
from logic.faculties import get_all_faculties
import arabic_reshaper
from bidi.algorithm import get_display
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
import asyncio
search_attributes = {}
faculty_lookup = {}
page_id = 0

def normalize_arabic(text: str) -> str:
    """Reshape and reorder Arabic text for consistent storage/search."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


# --- Helper Function for Search TextFields ---
def create_search_field(label: str, width: float = None, expand: bool = False, name: str = "", update=None):
    """Creates a styled TextField for search criteria."""
    return ft.TextField(
        data=name,
        label=label,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18", size=14),  # Gold label
        border=ft.InputBorder.UNDERLINE,  # Underline border style
        border_color="#B58B18",  # Gold border color
        focused_border_color="#B58B18",  # Gold focus border color
        bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK12),  # Very light background
        color="#000000",  # Dark font color
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45,  # Control height
        width=width,
        expand=expand,
        on_change=lambda e: update(e.control.data, e.control.value)
    )


# --- Helper for Table Header Cell ---
def create_header_cell(text: str):
    """Creates a styled header cell for the DataTable."""
    return ft.DataColumn(
        ft.Container(  # Wrap text in container for background color and padding
            content=ft.Text(
                text,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                size=14,
                text_align=ft.TextAlign.CENTER
            ),
            bgcolor="#B58B18",  # Gold background for headers
            padding=ft.padding.symmetric(vertical=10, horizontal=5),
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(top_left=8, top_right=8)  # Optional rounded top corners
        )
    )


# --- Helper for Table Data Cell ---
def create_data_cell(content: ft.Control):
    """Creates a styled data cell for the DataTable."""
    # Set text color and alignment if content is Text
    if isinstance(content, ft.Text):
        content.color = ft.colors.BLACK87  # Darker, visible text color
        content.text_align = ft.TextAlign.CENTER  # Center align text in cell

    return ft.DataCell(
        ft.Container(  # Wrap cell content for styling and alignment
            content=content,
            bgcolor=ft.colors.WHITE70,  # Light background for data cells
            padding=ft.padding.symmetric(vertical=8, horizontal=5),
            alignment=ft.alignment.center,  # Center content (like buttons) in cell
            border_radius=4  # Slight rounding for data cells
        )
    )


# --- Main View Creation Function ---
def create_search_student_view(page: ft.Page):
    """Creates the Flet View for the Search Student screen."""

    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event


    faculties = get_all_faculties()
    for fac in faculties:
        faculty_lookup[fac.id] = fac.name

    
    # Check if there's a pending delete action
    if hasattr(page, 'pending_delete_id') and page.pending_delete_id:
        # Get the student ID and clear the flag
        student_id = page.pending_delete_id
        page.pending_delete_id = None
        
        # Schedule the confirmation dialog to appear after the view is rendered
        print("I am here but the dialoge failed", student_id)

        async def show_dialog_after_delay():
            # Wait a short time to ensure view is rendered
            await asyncio.sleep(0.5)
            print("Showing delete confirmation dialog")
            show_delete_confirmation(student_id)
        
        # Schedule the timer to run
        asyncio.create_task(show_dialog_after_delay())

    # --- Controls ---
    # Back button navigation
    def go_back(e):
        page.go("/manage_students")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED,  # Looks like back arrow in RTL
        icon_color="#B58B18",
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    # Page Title
    page_title = ft.Text(
        "بحث",  # Title "Search"
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#B58B18"
    )

    # --- Show Delete Confirmation Dialog ---
    def show_delete_confirmation(student_id):
        """Shows a confirmation dialog for student deletion."""
        # Get student details
        student = get_student_by_id(student_id)
        if not student:
            page.show_snack_bar(ft.SnackBar(ft.Text("لم يتم العثور على الطالب"), open=True))
            print("I am here but snack bar doesn't work so now I am returning")
            return

        # Create confirmation dialog
        def close_dialog(e):
            dialog.open = False
            page.update()

        def confirm_delete(e):
            success = delete_student(student_id)
            dialog.open = False
            page.update()
            if success:
                page.show_snack_bar(ft.SnackBar(ft.Text("تم حذف الطالب بنجاح"), open=True))
                # Refresh the search results
                search()
            else:
                page.show_snack_bar(ft.SnackBar(ft.Text("فشل في حذف الطالب"), open=True))
        print("I am here right before dialoge start", student.id)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("تأكيد الحذف"),
            content=ft.Text(f"هل أنت متأكد من حذف الطالب: {student.name}؟"),
            actions=[
                ft.TextButton("إلغاء", on_click=close_dialog),
                ft.TextButton("حذف", on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    # --- Search Fields Definition ---
    def search():
        search_attributes['page'] = page_id
        students = get_students(search_attributes)
        rows = []
        for stu in students:
            # action button for this student
            update_button = ft.ElevatedButton(
                data=stu.id,
                text="تعديل",
                bgcolor=ft.colors.ORANGE,
                color=ft.colors.BLACK,
                width=70, height=35,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                tooltip=f"Action for {stu.name}",
                on_click=lambda e: edit_data_click(e.control.data)
            )
            # Note button for this student
            note_button = ft.ElevatedButton(
                data=stu.id,
                text="ملاحظة",
                bgcolor="#C83737",  # Red color 
                color=ft.colors.WHITE,
                width=70, height=35,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                tooltip=f"إضافة ملاحظة لـ {stu.name}",
                on_click=lambda e: add_note_click(e.control.data)
            )
            
            # Delete button for this student - NEW!
            delete_button = ft.ElevatedButton(
                data=stu.id,
                text="حذف",
                bgcolor="#B22222",  # Firebrick color for deletion
                color=ft.colors.WHITE,
                width=70, height=35, 
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                tooltip=f"حذف الطالب {stu.name}",
                on_click=lambda e: delete_student_click(e.control.data)
            )
            
            buttons_row = ft.Row(
                [update_button, note_button, delete_button],  # Added delete button
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER
            )
            # assemble all the cells
            cells = [
                create_data_cell(buttons_row),
                create_data_cell(ft.Text(stu.name)),
                create_data_cell(ft.Text(stu.national_id)),
                create_data_cell(ft.Text(stu.seq_number)),
                create_data_cell(ft.Text(stu.faculty.name if stu.faculty else "-")),
                create_data_cell(ft.Text(stu.phone_number)),
                create_data_cell(ft.Text(stu.location)),
            ]
            rows.append(ft.DataRow(cells=cells))

        results_table.rows = rows
        results_table.update()
        
    def update_attribute(name, value):
        global page_id
        page_id = 0
        print('=' * 80)
        
        # Special handling for gender filter
        if name == "is_male":
            if value is None:
                # Remove the filter if None
                search_attributes.pop(name, None)
            else:
                # Ensure the value is explicitly set as a boolean (not None)
                search_attributes[name] = bool(value)
        else:
            # Regular attribute handling for other fields
            if not value:
                search_attributes.pop(name, None)
            else:
                # Normalize Arabic fields so search matches storage
                if name in ("name", "faculty", "qr_code", "national_id"):
                    value = normalize_arabic(value)
                search_attributes[name] = value
        
        # Print debug info to confirm values
        print(f"Search attributes after update:")
        for k, v in search_attributes.items():
            print(f"  {k}: {v} (type: {type(v)})")
            
        search()

    national_id_field = create_search_field("البحث باستخدام الرقم القومي", expand=True, update=update_attribute,
                                            name="national_id")
    name_field = create_search_field("البحث باستخدام الاسم", expand=True, update=update_attribute, name="name")

    search_field_row1 = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[name_field, national_id_field]
    )
    phone_field = create_search_field("البحث باستخدام رقم الهاتف", expand=True, update=update_attribute,
                                      name="phone_number")
    serial_field = create_search_field("البحث باستخدام رقم المسلسل", width=200, update=update_attribute, name="seq_num")

    # Add gender dropdown
    gender_field = ft.Dropdown(
    label="النوع",
    width=200,
    options=[
        ft.dropdown.Option(key="male", text="ذكر"),
        ft.dropdown.Option(key="female", text="انثى")
    ],
    value=None,
    border_color="#B58B18",
    focused_border_color="#B58B18",
    text_style=ft.TextStyle(color="#000000"),
    border_radius=8,
    content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    on_change=lambda e: update_attribute(
        "is_male",
        True if e.control.value == "male" else 
        (False if e.control.value == "female" else None)
        )
    )

    faculty_field = ft.Dropdown(
        label="البحث باستخدام الكلية",
        width=200,
        options=[
            ft.dropdown.Option(key=str(f.id), text=f.name)
            for f in faculties
        ],
        value=None,  # no initial selection
        border_color="#B58B18",
        focused_border_color="#B58B18",
        text_style=ft.TextStyle(color="#000000"),  # Dark font color
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        on_change=lambda e: update_attribute(
            "faculty_id",
            int(e.control.value) if e.control.value else None
        )
    )

    search_field_row2 = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[phone_field, serial_field, faculty_field, gender_field]
    )
    location_field = create_search_field("بحث باستخدام محل السكن", expand = True, update = update_attribute, name = "location")
    search_field_row3 = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[location_field]
    )
    search_fields_container = ft.Column(
        controls=[search_field_row1, ft.Container(height=10), search_field_row2, search_field_row3],
        spacing=0  # Let Rows handle internal spacing
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

    def edit_data_click(student_id: int = 1):
        # This button navigates to the edit page
        print("Edit Student Data Clicked - Navigating to Edit Page")
        # In a real app, consider passing student ID: page.go(f"/edit_student/{student_id}")
        page.student_id = student_id
        page.go(f"/login/edit_student")  # Navigate to the edit student view route

    def add_note_click(student_id: int):
        """Navigate to add note view with selected student ID"""
        print(f"Add Note Clicked for student ID: {student_id}")
        page.student_id = student_id
        page.go("/add_note")  # Navigate to the add note view
        
    def delete_student_click(student_id: int):
        """Navigate to login page before deletion."""
        print(f"Delete Student Clicked for student ID: {student_id}")
        page.student_id = student_id
        page.go("/login/delete_student")  # Navigate to login with delete_student as target

    # Button Styling
    button_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    button_height = 45

    # Button Controls
    add_student_btn = ft.ElevatedButton(
        text="اضافة طالب", icon=ft.icons.PERSON_ADD_ALT_1, bgcolor="#6FA03C", color=ft.Colors.WHITE,
        height=button_height, style=button_style, on_click=add_student_click, tooltip="إضافة طالب جديد بشكل فردي"
    )
    add_file_btn = ft.ElevatedButton(
        text="اضافه ملف طلبه", icon=ft.icons.UPLOAD_FILE, bgcolor="#6FA03C", color=ft.Colors.WHITE,
        height=button_height, style=button_style, on_click=add_file_click,
        tooltip="إضافة مجموعة طلاب من ملف (Excel, CSV)"
    )
    # Layout for Action Buttons
    action_buttons_row = ft.Row(
        [add_student_btn, add_file_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        wrap=True,  # Allow wrapping on small screens
        run_spacing=10
    )
    action_buttons_container = ft.Container(
        content=action_buttons_row,
        padding=ft.padding.only(top=25, bottom=15)  # Spacing around buttons
    )

    # --- Results DataTable Definition ---
    # Define Columns
    columns = [
        create_header_cell("اجراء"),  # Action
        create_header_cell("الاسم"),  # Name
        create_header_cell("الرقم القومي"),  # National ID
        create_header_cell("رقم المسلسل"),  # Serial
        create_header_cell("الكلية"),  # Faculty
        create_header_cell("رقم الهاتف"),  # Phone
        create_header_cell("محل السكن"),  # Misc/Notes
    ]

    # Placeholder Data Rows (Replace with dynamic data later)
    rows = []
    results_table = ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.colors.with_opacity(0.5, "#B58B18")),  # Subtle gold border
        border_radius=ft.border_radius.all(10),
        vertical_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.2, ft.colors.BLACK)),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.2, ft.colors.BLACK)),
        column_spacing=10,  # Adjust spacing
        expand=True  # Make table fill horizontal space
    )

    # Create the DataTable widget

    # --- Get Banner ---
    banner_control = create_banner(page.width)
        # --- Pagination Buttons ---
    def next_page(e):
        global page_id
        page_id += 1
        search()

    def prev_page(e):
        global page_id
        if page_id > 0:
            page_id -= 1
        search()

    pagination_buttons = ft.Row(
        [
            ft.ElevatedButton(text="التالي", on_click=next_page, bgcolor="#B58B18", color=ft.colors.WHITE),
            ft.ElevatedButton(text="السابق", on_click=prev_page, bgcolor="#B58B18", color=ft.colors.WHITE),            
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
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
            pagination_buttons,
            # DataTable Area (in an expanding container)
            ft.Container(
                padding=ft.padding.symmetric(horizontal=30, vertical=20),
                alignment=ft.alignment.top_center,  # Align table within container
                content=results_table,
                expand=True  # Allow container to expand vertically
            ),
        ],
        expand=True, # Allow column to fill vertical page space
        scroll=ft.ScrollMode.ALWAYS, # Enable scrolling for the whole content column
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Stretch children horizontally
    )
    # --- View Definition ---
    return ft.View(
        route="/search_student",  # Route for this view
        padding=0,
        bgcolor="#E3DCCC",  # Background color
        controls=[
            ft.Column(  # Main page structure: Banner + Content
                [
                    banner_control,
                    content_column
                ],
                expand=True,  # Fill page height
                spacing=0  # No space between banner and content
            )
        ]
    )