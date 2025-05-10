# views/edit_student_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset # Not strictly needed here, but good practice
from logic.students import get_student_by_id, update_student
from logic.faculties import get_all_faculties
edit_attributes = {}
faculty_lookup = {}

def update_field(name : str, value : str):
    if not value:
        edit_attributes.pop(name, None)
    else:
        edit_attributes[name] = value

# --- Helper Function for Form TextFields ---
def create_form_field(label: str, name : str, value : str):
    """Creates a styled TextField for the edit form."""
    return ft.TextField(
        data = name,
        value = value,
        label=label,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18", size=14), # Gold label
        border_color="#B58B18", # Gold border
        color="#000000",
        focused_border_color="#B58B18", # Gold focus border
        bgcolor=ft.Colors.WHITE, # White background
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45, 
        on_change = lambda e : update_field(e.control.data, value = e.control.value)
    )

# --- Main View Creation Function ---
def create_edit_student_view(page: ft.Page):
    """Creates the Flet View for the Edit Student Data screen."""
    faculties = get_all_faculties()
    for fac in faculties:
        faculty_lookup[fac.id] = fac.name
    # --- Controls ---
    def go_back(e):
        page.go("/search_student")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18",
        tooltip="العودة", on_click=go_back, icon_size=30
    )

    page_title = ft.Text(
        "تعديل بيانات الطالب", # Edit Student Data
        size=32, weight=ft.FontWeight.BOLD, color="#B58B18"
    )
    student_id = page.student_id
    edit_attributes["id"] = student_id
    student = get_student_by_id(student_id)
    # --- Form Fields ---
    # --- inside create_edit_student_view, right after you fetch `student` ---
    name_field = create_form_field(
        label="الاسم",
        name="name",
        value=student.name
    )
    national_id_field = create_form_field(
        label="الرقم القومي",
        name="national_id",
        value=student.national_id
    )
    serial_no_field = create_form_field(
        label="رقم المسلسل",
        name="seq_number",
        value=student.seq_number
    )
    faculty_field = ft.Dropdown(
    label="الكلية",
    data="faculty_id",
    options=[
        ft.dropdown.Option(key=str(faculty_id), text=faculty_name)
        for faculty_id, faculty_name in faculty_lookup.items()
    ],
    value=str(student.faculty_id),  # default to the student’s current faculty
    on_change=lambda e: update_field(name=e.control.data, value=e.control.value),
    # optional styling to match your other fields:
    border_color="#B58B18",
    focused_border_color="#B58B18",
    border_radius=8,
    content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )

    phone_field = create_form_field(
        label="رقم الهاتف",
        name="phone_number",
        value=student.phone_number
    )

    location_field = create_form_field(
        label="محل السكن",
        name="location",
        value=student.location
    )

    # --- Save Button ---
    def save_data(e):
        print("Save button clicked!")
        update_student(edit_attributes)
        page.open(ft.SnackBar(ft.Text("تم حفظ التعديلات")))
        page.update()
        print(edit_attributes)
        go_back(None) # Simulate going back after save

    save_button = ft.ElevatedButton(
        text="حفظ",
        icon=ft.icons.SAVE_OUTLINED,
        bgcolor="#B58B18", # Gold
        color=ft.Colors.WHITE,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Form Layout using ResponsiveRow ---
    form_layout = ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.START, # Align columns to the start
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20, # Horizontal space between columns
        run_spacing=15, # Vertical space between rows within columns
        controls=[
            # Left Column (md=6 means it takes half width on medium screens and up)
            ft.Column(
                col={"xs": 12, "md": 6}, # Full width on extra small, half on medium+
                spacing=15,
                controls=[
                    name_field,
                    national_id_field,
                    location_field,
                ]
            ),
            # Right Column
            ft.Column(
                 col={"xs": 12, "md": 6},
                 spacing=15,
                 controls=[
                     # Special row for Serial No and Faculty to be side-by-side
                     ft.Row(
                         spacing=10,
                         controls=[
                             ft.Container(content=serial_no_field, width=150), # Fixed width for serial
                             ft.Container(content=faculty_field, expand=True), # Faculty takes remaining space
                         ]
                     ),
                     phone_field,
                 ]
            )
        ]
    )

    # Get banner
    banner_control = create_banner(page.width)

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            # Top row: Title and Back button
            ft.Container(
                padding=ft.padding.only(top=20, bottom=10, left=30, right=30),
                content=ft.Row(
                    [page_title, back_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            # Form Area
            ft.Container(
                padding=ft.padding.symmetric(horizontal=50, vertical=20),
                content=form_layout
            ),
            # Save Button Area (Centered)
            ft.Container(
                content=save_button,
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20, bottom=30)
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        # Center content horizontally within the column
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- View Definition ---
    return ft.View(
        route="/edit_student", # Define route for this view
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column( # Main structure: Banner on top, content below
                [
                    banner_control,
                    content_column
                ],
                expand=True,
                spacing=0
            )
        ]
    )