# views/add_student_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset
from logic.students import create_student_from_dict
from logic.faculties import get_all_faculties
from logic.course import get_all_courses
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# Using a class to better manage the component state
class AddStudentForm:
    def __init__(self):
        self.attributes = {}
        self.faculty_lookup = {}
        self.course_lookup = {}
        self.male_courses = []
        self.female_courses = []
        self.course_dropdown = None
        
    def update_field(self, name, value):
        """Update form field in the attributes dictionary"""
        if value is None or value == "":
            self.attributes.pop(name, None)
        else:
            self.attributes[name] = value
            
            # Special handling for gender selection
            if name == "is_male":
                self.update_course_options(value)
    
    def update_course_options(self, gender_value):
        """Update course dropdown options based on gender selection"""
        if self.course_dropdown:
            # Clear current options
            self.course_dropdown.options.clear()
            
            # Add appropriate courses based on gender
            if gender_value == "1":  # Male
                self.course_dropdown.options = [
                    ft.dropdown.Option(key=str(course_id), text=course_name)
                    for course_id, course_name in self.male_courses
                ]
            else:  # Female
                self.course_dropdown.options = [
                    ft.dropdown.Option(key=str(course_id), text=course_name)
                    for course_id, course_name in self.female_courses
                ]
                
            # Update dropdown and disable if no options
            if not self.course_dropdown.options:
                self.course_dropdown.disabled = True
                self.course_dropdown.hint_text = "لا يوجد دورات متاحة لهذا النوع"
            else:
                self.course_dropdown.disabled = False
                self.course_dropdown.hint_text = None
                self.course_dropdown.value = str(self.course_dropdown.options[0].key)
                self.update_field("course_id", self.course_dropdown.value)
            
            self.course_dropdown.update()


# --- Helper Function for Form TextFields ---
def create_form_field(label: str, name: str, form: AddStudentForm):
    """Creates a styled TextField for the edit form."""
    return ft.TextField(
        data=name,
        label=label,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18", size=14),  # Gold label
        border_color="#B58B18",  # Gold border
        color="#000000",
        focused_border_color="#B58B18",  # Gold focus border
        bgcolor=ft.Colors.WHITE,  # White background
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45,
        on_change=lambda e: form.update_field(e.control.data, e.control.value)
    )


# --- Main View Creation Function ---
def create_add_student_view(page: ft.Page):
    """Creates the Flet View for adding a new student."""
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    # Initialize form state
    form = AddStudentForm()
    
    # Load faculties for dropdown
    faculties = get_all_faculties()
    for fac in faculties:
        form.faculty_lookup[fac.id] = fac.name
    
    # Load courses and separate by gender
    courses = get_all_courses()
    for course in courses:
        course_name = f"دورة {course.start_date.strftime('%Y-%m-%d')}"
        if course.is_male_type:
            form.male_courses.append((course.id, course_name))
        else:
            form.female_courses.append((course.id, course_name))
    
    # --- Controls ---
    def go_back(e):
        page.go("/manage_students")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18",
        tooltip="العودة", on_click=go_back, icon_size=30
    )

    page_title = ft.Text(
        "ادخال بيانات الطالب",  # Add Student Data
        size=32, weight=ft.FontWeight.BOLD, color="#B58B18"
    )
    
    name_field = create_form_field("الاسم", "name", form)
    national_id_field = create_form_field("الرقم القومي", "national_id", form)
    phone_field = create_form_field("رقم الهاتف", "phone_number", form)
    address_field = create_form_field("عنوان محل الاقامة", "location", form)
    
    # Faculty dropdown
    faculty_field = ft.Dropdown(
        label="الكلية",
        data="faculty_id",
        color="#000000",
        options=[
            ft.dropdown.Option(key=str(faculty_id), text=faculty_name)
            for faculty_id, faculty_name in form.faculty_lookup.items()
        ],
        on_change=lambda e: form.update_field(e.control.data, e.control.value),
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )
    
    # Gender dropdown
    gender_field = ft.Dropdown(
        label="النوع",
        data="is_male",
        color="#000000",
        options=[
            ft.dropdown.Option(key="1", text="ذكر"),
            ft.dropdown.Option(key="0", text="انثى")
        ],
        on_change=lambda e: form.update_field(e.control.data, e.control.value),
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )
    
    # Course dropdown (initially empty, will be populated based on gender)
    course_field = ft.Dropdown(
        label="الدورة",
        data="course_id",
        color="#000000",
        options=[],  # Will be populated after gender selection
        on_change=lambda e: form.update_field(e.control.data, e.control.value),
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        disabled=True,  # Initially disabled until gender is selected
        hint_text="يرجى اختيار النوع أولاً"
    )
    
    # Store reference to course dropdown in form for updating
    form.course_dropdown = course_field
    
    # --- Save Button ---
    def save_data(e):
        print("Save button clicked!")
        
        # Validation
        if not all(k in form.attributes for k in ["name", "faculty_id", "is_male", "course_id", "location"]):
            page.snack_bar = ft.SnackBar(ft.Text("يرجى إدخال جميع البيانات المطلوبة"))
            page.snack_bar.open = True
            page.update()
            return
            
        # Create student
        student = create_student_from_dict(form.attributes)
        
        if student:
            page.snack_bar = ft.SnackBar(ft.Text("تم إضافة الطالب بنجاح"))
            page.snack_bar.open = True
            page.update()
            go_back(None)  # Return to manage students page
        else:
            page.snack_bar = ft.SnackBar(ft.Text("حدث خطأ أثناء إضافة الطالب"))
            page.snack_bar.open = True
            page.update()

    save_button = ft.ElevatedButton(
        text="حفظ",
        icon=ft.icons.SAVE_OUTLINED,
        bgcolor="#B58B18",  # Gold
        color=ft.Colors.WHITE,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Form Layout using ResponsiveRow ---
    form_layout = ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.START,  # Align columns to the start
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,  # Horizontal space between columns
        run_spacing=15,  # Vertical space between rows within columns
        controls=[
            # Left Column
            ft.Column(
                col={"xs": 12, "md": 6},  # Full width on extra small, half on medium+
                spacing=15,
                controls=[
                    name_field,
                    national_id_field,
                    address_field,
                    course_field,  # Added course field
                ]
            ),
            # Right Column
            ft.Column(
                col={"xs": 12, "md": 6},
                spacing=15,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(content=gender_field, expand=True),
                            ft.Container(content=faculty_field, expand=True),
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
        route="/add_student",  # Define route for this view
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(  # Main structure: Banner on top, content below
                [
                    banner_control,
                    content_column
                ],
                expand=True,
                spacing=0
            )
        ]
    )