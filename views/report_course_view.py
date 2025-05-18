# views/report_course_view.py
import flet as ft
from components.banner import create_banner
from logic.faculties import get_all_faculties
from logic.course import get_all_courses
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# --- Constants for Styling ---
PAGE_BGCOLOR = "#E3DCCC"
FORM_BORDER_COLOR = "#B58B18"
FORM_BORDER_RADIUS = 15
FORM_PADDING = 15
FIELD_SPACING = 12
FIELD_BGCOLOR = ft.colors.WHITE
FIELD_BORDER_RADIUS = 8
TITLE_COLOR = "#9A7B4F"
BUTTON_COLOR = "#8BC34A"
BUTTON_TEXT_COLOR = ft.colors.WHITE

# Global dictionary to store course lookups - modified for string keys
course_lookup = {}

def course_title(course):
    title = "دورة "
    title += str(course.start_date)
    title += " "
    if course.is_male_type:
        title += "ذكور"
    else:
        title += 'اناث'
    return title

def submit_report_request(e: ft.ControlEvent):
    page = e.page
    view = page.views[-1]

    # Access controls using the references stored in the view's data attribute
    controls_dict = view.data
    course_id = controls_dict["course_id"].value
    college = controls_dict["college"].value
    report_type = controls_dict["report_type"].value

    print("Submit Report Request Clicked!")
    print(f"  Course ID: {course_id}")
    print(f"  College: {college}")
    print(f"  Report Type: {report_type}")

    # Store selections in page properties - Fix: Convert course_id to string for lookup
    # This ensures consistent type between dropdown value and lookup key
    page.course_id = course_id  # Store the actual ID (likely an integer)
    
    # Fix: Convert course_id to string when looking up
    course_id_str = str(course_id) if course_id is not None else None
    
    if course_id_str in course_lookup:
        page.course_name = course_lookup[course_id_str]
    else:
        # Fallback message if course not found in lookup
        print(f"Warning: Course ID {course_id} not found in lookup")
        page.course_name = f"Course {course_id}"
    
    # Handle faculty ID
    if college:
        # Ensure faculty_id is an integer
        try:
            page.faculty_id = int(college)
        except (ValueError, TypeError):
            page.faculty_id = None
    else:
        page.faculty_id = None
    

    # Navigate based on report type
    if report_type == "type1":
        page.go("/report")
    else:
        page.go("/report_alt")


def create_report_course_view(page: ft.Page):
    """Creates the Flet View for the Course Report Generation screen."""
    # Clear the global lookup to prevent stale data
    global course_lookup
    course_lookup.clear()
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    banner_control = create_banner(page.width)
    
    def go_back(e):
        page.go("/dashboard")
    
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        tooltip="العودة إلى لوحة التحكم",
        icon_color=FORM_BORDER_COLOR,
        icon_size=30,
        on_click=go_back
    )

    title = ft.Text(
        "استخراج تقرير دورة",
        size=36,
        weight=ft.FontWeight.BOLD,
        color=TITLE_COLOR,
        text_align=ft.TextAlign.CENTER
    )
    
    # Fetch all courses
    courses = get_all_courses()
    
    # FIX: Convert course IDs to strings in the lookup dictionary
    for course in courses:
        course_lookup[str(course.id)] = course_title(course)

    # Build dropdown options with string keys for consistency
    course_options = [
        ft.dropdown.Option(
            text=course_title(c),
            key=str(c.id),  # FIX: Convert ID to string for consistent key type
            text_style=ft.TextStyle(color="#000000")
        )
        for c in courses
    ]
    
    course_dropdown = ft.Dropdown(
        hint_text="تاريخ الدورة",
        border_color=FORM_BORDER_COLOR,
        color="#000000",
        hint_style=ft.TextStyle(color="#000000"),
        border_radius=FIELD_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR,
        text_align=ft.TextAlign.RIGHT,
        options=course_options,
        # Set default value using string key
        value=str(courses[0].id) if courses else None,
    )
    
    faculties = get_all_faculties()
    faculty_options = [
        ft.dropdown.Option(
            text=f.name,
            key=str(f.id),  # FIX: Convert ID to string for consistency
            text_style=ft.TextStyle(color="#000000")
        )
        for f in faculties
    ]
    
    college_dropdown = ft.Dropdown(
        hint_text="الكلية (اختياري)",
        border_color=FORM_BORDER_COLOR,
        border_radius=FIELD_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR,
        color="#000000",
        hint_style=ft.TextStyle(color="#000000"),
        options=faculty_options,
    )

    report_type_dropdown = ft.Dropdown(
        hint_text="نوع التقرير",
        border_color=FORM_BORDER_COLOR,
        border_radius=FIELD_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR,
        color="#000000",
        hint_style=ft.TextStyle(color="#000000"),
        options=[
            ft.dropdown.Option(key="type1", text="تقرير الاسم"),
            ft.dropdown.Option(key="type2", text="تقرير الأيام")
        ],
        value="type1"
    )

    # Store controls for easier access in submit function
    controls_dict = {
        "course_id": course_dropdown,
        "college": college_dropdown,
        "report_type": report_type_dropdown,
    }

    form_container = ft.Container(
        padding=FORM_PADDING,
        border=ft.border.all(2.5, FORM_BORDER_COLOR),
        border_radius=FORM_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR,
        width=450,
        content=ft.Column(
            [
                report_type_dropdown,
                course_dropdown,
                college_dropdown,
            ],
            spacing=FIELD_SPACING,
        )
    )

    submit_button = ft.ElevatedButton(
        text="تأكيـد",
        bgcolor=BUTTON_COLOR,
        color=BUTTON_TEXT_COLOR,
        width=200,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=FIELD_BORDER_RADIUS),
        ),
        on_click=submit_report_request
    )

    main_content_column = ft.Column(
        [
            ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=10),
            title,
            ft.Container(height=20),
            form_container,
            ft.Container(height=25),
            submit_button,
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
    )

    view = ft.View(
        route="/report_course",
        bgcolor=PAGE_BGCOLOR,
        padding=0,
        controls=[
            banner_control,
            ft.Container(
                content=main_content_column,
                expand=True,
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(horizontal=30, vertical=10)
            )
        ]
    )
    
    # Store the controls dictionary in the view's data attribute
    view.data = controls_dict
    return view


# Example Usage (if running this file directly)
if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Report Course View Test"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 800 # Example width
        page.window_height = 700 # Example height
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # --- Mock Banner ---
        def create_mock_banner(width):
            return ft.Container(
                # Use placeholder colors/content if real banner isn't available
                height=80,
                bgcolor="#5C5341", # Dark camo-like color
                padding=ft.padding.symmetric(horizontal=20),
                content=ft.Row(
                    [
                        ft.Image(src="path/to/your/logo.png", height=60, width=60), # Add logo path
                        ft.Column(
                            [
                                ft.Text("التربية العسكرية", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD, size=20),
                                ft.Text("جامعة عين شمس", color=ft.colors.WHITE, size=16),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.END, # Align text right
                            expand=True, # Take remaining space
                            spacing=0
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        # Replace the real banner import with the mock for testing if needed
        global create_banner
        create_banner = create_mock_banner # Comment this line if using the real banner

        # Add the view
        page.views.append(create_report_course_view(page))
        page.update()

        # Add routing logic if needed for back button test
        def route_change(route):
            print(f"Route changed to: {route}")
            # Add logic to navigate if necessary for testing back button
            if route == "/dashboard":
                # Replace with actual dashboard view or placeholder
                page.views.clear()
                page.views.append(ft.View("/", [ft.Text("Mock Dashboard", size=30)]))
                page.update()
            elif route == "/report_course":
                 # Ensure the report view is shown if navigating back to it
                 if not any(v.route == "/report_course" for v in page.views):
                    page.views.append(create_report_course_view(page))
                 page.update()


        page.on_route_change = route_change
        # page.go("/report_course") # Start at the report view

    ft.app(target=main) # Add assets_dir="assets" if logo is in assets folder