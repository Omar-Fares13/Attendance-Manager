# views/report_course_view.py
import flet as ft
from components.banner import create_banner # Assuming your banner is reusable
from logic.faculties import get_all_faculties
from logic.course import get_all_courses
# --- Constants for Styling (Adjusted based on image) ---
PAGE_BGCOLOR = "#E3DCCC" # Light beige/tan background from image
FORM_BORDER_COLOR = "#B58B18" # Gold color from image border/text
FORM_BORDER_RADIUS = 15
FORM_PADDING = 15 # Slightly reduced padding inside form
FIELD_SPACING = 12 # Reduced spacing between fields
FIELD_BGCOLOR = ft.colors.WHITE
FIELD_BORDER_RADIUS = 8
TITLE_COLOR = "#9A7B4F" # Darker gold/brown for title
BUTTON_COLOR = "#8BC34A" # Brighter Green color for button like image
BUTTON_TEXT_COLOR = ft.colors.WHITE

course_lookup = {}
# --- Placeholder Functions ---
# It's better practice to access controls via references instead of deep indexing
# We'll create references in the create_report_course_view function
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
    view = page.views[-1] # Get the current view

    # Access controls using the references stored in the view's data attribute
    controls_dict = view.data
    course_id = controls_dict["course_id"].value
    college = controls_dict["college"].value
    student_name = controls_dict["student_name"].value

    print("Submit Report Request Clicked!")
    print(f"  Course ID: {course_id}")
    print(f"  College: {college}")
    print(f"  Student Name: {student_name}")

    # Add logic here to generate/fetch the report based on selections
    page.course_id = course_id
    if college:
        page.faculty_id = int(college)
    else:
        page.faculty_id = None
    page.student_name = student_name
    page.course_name = course_lookup[course_id]
    page.go('/report')
def go_back_to_dashboard(e: ft.ControlEvent):
    """Navigates back to the dashboard."""
    e.page.go("/dashboard")

# --- View Creation Function ---
def create_report_course_view(page: ft.Page):
    """Creates the Flet View for the Course Report Generation screen."""

    banner_control = create_banner(page.width) # Use the shared banner

    # --- Back Button ---
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK, # Changed to ARROW_BACK for left-pointing arrow
        tooltip="العودة إلى لوحة التحكم",
        icon_color=FORM_BORDER_COLOR,
        icon_size=30,
        on_click=go_back_to_dashboard
    )
    
    # --- Title ---
    title = ft.Text(
        "استخراج تقرير دورة",
        size=36, # Slightly larger title
        weight=ft.FontWeight.BOLD,
        color=TITLE_COLOR,
        text_align=ft.TextAlign.CENTER
    )
    # first, fetch all courses (e.g. sorted however you like)
    courses = get_all_courses()

    for course in courses:
        course_lookup[course.id] = course_title(course)
    # then build a Dropdown instead of a TextField:
    course_dropdown = ft.Dropdown(
        hint_text="تاريخ الدورة",           # your placeholder
        border_color=FORM_BORDER_COLOR,
        color="#000000",
        hint_style=ft.TextStyle(color="#000000"),
        border_radius=FIELD_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR,
        text_align=ft.TextAlign.RIGHT,
        options=[
        ft.dropdown.Option(
            text=course_title(c), 
            key=c.id,
            text_style=ft.TextStyle(color="#000000")   # ← MAKE OPTION TEXT BLACK
        )
        for c in courses
    ],
        # optionally pre‑select the first one (or leave as None)
        value=courses[0].id if courses else None,
    )
    faculties = get_all_faculties()
    college_dropdown = ft.Dropdown(
        hint_text="الكلية (اختياري)", # Use hint_text
        border_color=FORM_BORDER_COLOR,
        border_radius=FIELD_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR,
        color="#000000",
        hint_style=ft.TextStyle(color="#000000"),
        # text_style=ft.TextStyle(text_align=ft.TextAlign.RIGHT), # Alignment for selected item (might not work perfectly cross-platform)
        # hint_style=ft.TextStyle(text_align=ft.TextAlign.RIGHT), # Alignment for hint (might not work perfectly cross-platform)
        options=[
        ft.dropdown.Option(
            text=f.name, 
            key=f.id,
            text_style=ft.TextStyle(color="#000000")   # ← MAKE OPTION TEXT BLACK
        )
        for f in faculties
    ],
    )

    student_name_field = ft.TextField(
        hint_text="اسم طالب (اختياري)", # Use hint_text
        border_color=FORM_BORDER_COLOR,
        border_radius=FIELD_BORDER_RADIUS,
        color="#000000",
        hint_style=ft.TextStyle(color="#000000"),
        bgcolor=FIELD_BGCOLOR,
        text_align=ft.TextAlign.RIGHT,
    )

    # Store controls for easier access in submit function
    controls_dict = {
        "course_id": course_dropdown,
        "college": college_dropdown,
        "student_name": student_name_field,
    }

    # --- Form Container ---
    form_container = ft.Container(
        padding=FORM_PADDING,
        border=ft.border.all(2.5, FORM_BORDER_COLOR), # Slightly thicker border
        border_radius=FORM_BORDER_RADIUS,
        bgcolor=FIELD_BGCOLOR, # Opaque white background
        width=450, # Adjust width as needed
        content=ft.Column(
            [
                course_dropdown,
                college_dropdown,
                student_name_field
            ],
            spacing=FIELD_SPACING,
            # horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Let controls fill width
        )
    )

    # --- Submit Button ---
    submit_button = ft.ElevatedButton(
        text="تأكيـد",
        bgcolor=BUTTON_COLOR,
        color=BUTTON_TEXT_COLOR,
        width=200,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=FIELD_BORDER_RADIUS), # Use same radius as fields
        ),
        on_click=submit_report_request # Assign the placeholder function
    )

    # --- Main Layout Column (Content below Banner) ---
    main_content_column = ft.Column(
        [
            # Row for Back Button alignment (aligned left/start)
            ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
            # title, # Title centered below back button row
            ft.Container(height=10), # Spacer
            title, # Title centered below back button row
            ft.Container(height=20), # Spacer
            form_container,
            ft.Container(height=25), # Spacer
            submit_button,
            # ft.Container(height=20), # Spacer at bottom optional
        ],
        # Removed expand=True here, let the outer container handle expansion
        scroll=ft.ScrollMode.ADAPTIVE, # Allow scrolling if content overflows
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Center items horizontally
        # alignment=ft.MainAxisAlignment.START, # Align content towards the top
        spacing=0 # Control spacing with Containers
    )


    # --- View ---
    view = ft.View(
        route="/report_course",
        bgcolor=PAGE_BGCOLOR,
        padding=0, # No padding on the view itself
        controls=[
             # Add the banner at the top level
             banner_control,
             # Wrap main content in a container for padding and centering
             ft.Container(
                 content=main_content_column,
                 expand=True, # Allow this container to take available space
                 alignment=ft.alignment.center, # Center the column vertically if space allows
                 padding=ft.padding.symmetric(horizontal=30, vertical=10) # Add padding around main content
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