# views/mark_attendance_departure_view.py
import flet as ft
# Ensure create_banner is correctly imported
try:
    from components.banner import create_banner
except ImportError:
    print("Warning: components.banner not found. Using placeholder.")
    def create_banner(width): # Mock function if import fails
        return ft.Container(height=80, bgcolor="#5C5341", content=ft.Text("Mock Banner", color=ft.colors.WHITE))

# --- Constants ---
PAGE_BGCOLOR = "#E3DCCC"
GOLD_COLOR = "#B58B18"
GREEN_COLOR = "#6FA03C" # Attendance Green
RED_COLOR = "#C83737"  # Departure Red
GREY_COLOR = "#888888"  # Notes Button Grey
WHITE_COLOR = ft.colors.WHITE
CARD_BORDER_RADIUS = 15
BUTTON_BORDER_RADIUS = 8
PROFILE_PIC_SIZE = 150
# Make sure these image paths are correct relative to your assets directory
PLACEHOLDER_IMAGE_SRC = "images/placeholder_canva.png" # Path relative to assets dir
PROFILE_IMAGE_SRC = "images/profile_placeholder.png"  # Path relative to assets dir

# --- Button Action Functions ---
# Placeholder action for the 'Warning' button
def show_warning(e: ft.ControlEvent):
    print("Warning button clicked!")
    e.page.show_snack_bar(ft.SnackBar(ft.Text("زر الإنذار - لم يتم التنفيذ بعد", text_align=ft.TextAlign.RIGHT), open=True))

# Navigation action for the 'Note' button
def navigate_to_add_note(e: ft.ControlEvent):
    # TODO: Pass student ID or relevant data if needed for the note page
    # student_id = get_student_id_somehow() # Replace with actual logic to get ID
    # e.page.go(f"/add_note?student_id={student_id}") # Example with query param
    print("Note button clicked, navigating to /add_note")
    e.page.go("/add_note")

# Placeholder action for the 'Accept' button (Attendance/Departure)
def accept_action(e: ft.ControlEvent):
    action_type = e.control.data # 'attendance' or 'departure' stored in button data
    print(f"Accept button clicked for: {action_type}")
    e.page.show_snack_bar(ft.SnackBar(ft.Text(f"زر القبول ({action_type}) - لم يتم التنفيذ بعد", text_align=ft.TextAlign.RIGHT), open=True))
    # TODO: Add logic here to record attendance/departure using student ID, timestamp etc.

# --- Helper to build Student Data Card ---
def _build_student_data_card(page: ft.Page, action_type: str):
    """Builds the left-side student data card."""

    # Inner function to create formatted data rows
    def create_data_row(label, value):
        return ft.Row(
            [
                # Ensure data fields handle potential None values gracefully if needed
                ft.Text(value if value is not None else "-", text_align=ft.TextAlign.RIGHT, expand=True, weight=ft.FontWeight.W_500),
                ft.Text(f":{label}", text_align=ft.TextAlign.RIGHT, color=GOLD_COLOR, weight=ft.FontWeight.BOLD, width=100, no_wrap=True), # Added fixed width for labels
            ],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            # spacing=5
        )

    # The main container for the student data card
    return ft.Container(
        padding=ft.padding.all(15), # Adjusted padding
        border=ft.border.all(2, GOLD_COLOR),
        border_radius=CARD_BORDER_RADIUS,
        bgcolor=WHITE_COLOR,
        width=400, # Fixed width for the card
        content=ft.Column(
            [
                ft.Text(
                    "بيانات الطالب",
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=GOLD_COLOR
                ),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT), # Spacer

                # --- Replace with actual dynamic data ---
                # TODO: Pass student data as an argument to this function
                create_data_row("الاسم", "محمد محمد محمد"),
                create_data_row("ID الطالب", "123456"),
                create_data_row("الرقم القومي", "12345678901234"),
                create_data_row("الكلية", "الهندسة"),
                create_data_row("مسلسل", "123"),
                create_data_row("ملاحظات", "واحد اثنان ثلاثة اربعة خمسة ستة سبعة ثمانية"), # Display existing notes
                # --- End Dynamic Data Section ---

                ft.Divider(height=15, color=ft.colors.TRANSPARENT), # Spacer before buttons

                # Row containing the action buttons
                ft.Row(
                    [
                         # Swapped order to match image (قبول, ملاحظة, انذار from right to left)
                          ft.ElevatedButton(
                            "انذار", # Warning button
                            bgcolor=RED_COLOR,
                            color=WHITE_COLOR,
                            width=100, height=40,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
                            on_click=show_warning # Calls the warning placeholder
                        ),
                         ft.ElevatedButton(
                            "ملاحظة", # Note button
                            bgcolor=GREY_COLOR,
                            color=WHITE_COLOR,
                            width=100, height=40,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
                            on_click=navigate_to_add_note # <<< UPDATED: Calls the navigation function
                        ),
                        ft.ElevatedButton(
                            "قبول", # Accept button (Attendance/Departure)
                            bgcolor=GOLD_COLOR,
                            color=WHITE_COLOR,
                            width=100, height=40,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
                            on_click=accept_action, # Calls the accept placeholder
                            data=action_type # Pass 'attendance' or 'departure' to handler
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY, # Distribute buttons evenly
                )
            ],
            # Column alignment for the card content
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8 # Spacing between elements in the column
        )
    )

# --- Helper to build Image Placeholder ---
def _build_image_placeholder(page: ft.Page, border_color: str):
    """Builds the right-side image placeholder."""
    return ft.Container(
        width=350, # Fixed width
        height=350, # Fixed height
        border=ft.border.all(4, border_color), # Border color depends on view (green/red)
        border_radius=CARD_BORDER_RADIUS,
        bgcolor=WHITE_COLOR,
        padding=10, # Padding inside the border
        alignment=ft.alignment.center, # Center the image within the container
        content=ft.Image(
            src=PLACEHOLDER_IMAGE_SRC, # Path to the placeholder image
            fit=ft.ImageFit.CONTAIN, # Fit image within bounds
            border_radius=ft.border_radius.all(CARD_BORDER_RADIUS - 5), # Inner radius for image
            # Error content if the image fails to load
            error_content=ft.Column(
                [
                    ft.Icon(ft.icons.CAMERA_ALT_OUTLINED, size=50, color=ft.colors.BLACK26),
                    ft.Text("لا يمكن تحميل الصورة", color=ft.colors.BLACK26)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                opacity=0.8
            )
        )
    )

# --- Reusable View Creation Function ---
def create_mark_view(page: ft.Page, title_text: str, title_color: str, border_color: str, route: str, action_type: str):
    """Creates the base view for Attendance or Departure marking."""

    # --- Back Button Logic ---
    def go_back(e: ft.ControlEvent):
        # Navigates back to the attendance selection screen
        print("Back button clicked, navigating to /attendance")
        page.go("/attendance")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # RTL back arrow
        icon_color=GOLD_COLOR,
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    # --- Page Title ---
    page_title = ft.Text(
        title_text, # "حضور" or "انصراف"
        size=36,
        weight=ft.FontWeight.BOLD,
        color=title_color, # Green or Red
        text_align=ft.TextAlign.CENTER
    )

    # --- Profile Picture ---
    profile_picture = ft.Image(
        src=PROFILE_IMAGE_SRC, # Path to profile placeholder
        width=PROFILE_PIC_SIZE,
        height=PROFILE_PIC_SIZE,
        fit=ft.ImageFit.COVER, # Cover the area
        border_radius=ft.border_radius.all(PROFILE_PIC_SIZE / 2), # Make it circular
        # Error content if the image fails to load
        error_content=ft.Icon(ft.icons.PERSON_OUTLINE, size=PROFILE_PIC_SIZE * 0.6, color=ft.colors.BLACK26)
    )

    # --- Get Banner ---
    banner_control = create_banner(page.width) # Assumes create_banner is available

    # --- Main Content Layout (Row containing left and right sections) ---
    main_content = ft.Row(
        [
            # --- Left Section (Profile Pic + Data Card) ---
            ft.Column(
                [
                    profile_picture,
                    ft.Container(height=20), # Spacer
                    # Build the student data card, passing page and action type
                    _build_student_data_card(page, action_type)
                ],
                # Column alignment
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
                spacing=0
            ),

            # --- Right Section (Image Placeholder) ---
            # Build the image placeholder, passing page and border color
            _build_image_placeholder(page, border_color)
        ],
        # Row alignment
        vertical_alignment=ft.CrossAxisAlignment.START, # Align items to the top
        alignment=ft.MainAxisAlignment.CENTER, # Center the two main columns horizontally
        spacing=50, # Space between the left and right columns
        wrap=False # Prevent wrapping
    )

    # --- Column for Page Content (below banner) ---
    content_column = ft.Column(
        [
           # Row for the back button (aligned left)
           ft.Container(
                content=ft.Row(
                    [back_button],
                    alignment=ft.MainAxisAlignment.START
               ),
               padding=ft.padding.only(left=10) # Padding for back button row
           ),
           ft.Container(height=5), # Small spacer
           page_title, # Page title (centered by the column's alignment)
           ft.Container(height=20), # Spacer
           main_content, # The main Row containing the card and image placeholder
        ],
        # Column alignment and behavior
        expand=True, # Allow column to expand
        scroll=ft.ScrollMode.ADAPTIVE, # Enable scrolling if needed
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Center items like title and main_content row
    )


    # --- View Definition ---
    return ft.View(
        route=route, # Route for this view (/mark_attendance or /mark_departure)
        padding=0, # No padding on the view itself
        bgcolor=PAGE_BGCOLOR, # Background color
        controls=[
            # Main column structure: Banner + Content Area
            ft.Column(
                [
                    banner_control,
                    # Container to hold the content column and apply padding
                    ft.Container(
                        content=content_column,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10), # Padding around content
                        expand=True, # Allow content container to expand
                        alignment=ft.alignment.top_center # Align content towards the top center
                    )
                ],
                expand=True, # Make the main column fill the page height
                spacing=0 # No space between banner and content container
            )
        ]
    )

# --- Specific View Creation Functions ---
def create_attendance_mark_view(page: ft.Page):
    """Creates the 'حضور' (Attendance) view."""
    print(f"Creating Attendance Mark View for page: {id(page)}")
    # Calls the reusable function with specific parameters for Attendance
    return create_mark_view(
        page=page,
        title_text="حضــور",
        title_color=GREEN_COLOR,
        border_color=GREEN_COLOR,
        route="/mark_attendance",
        action_type="attendance" # Pass 'attendance' for the accept button data
    )

def create_departure_mark_view(page: ft.Page):
    """Creates the 'انصراف' (Departure) view."""
    print(f"Creating Departure Mark View for page: {id(page)}")
    # Calls the reusable function with specific parameters for Departure
    return create_mark_view(
        page=page,
        title_text="انصـراف",
        title_color=RED_COLOR,
        border_color=RED_COLOR,
        route="/mark_departure",
        action_type="departure" # Pass 'departure' for the accept button data
    )

# --- Example Usage (if running this file directly for testing) ---
if __name__ == "__main__":

    # (Include the mock banner, assets check, dummy file creation from previous example if needed)
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, '..', 'assets'))
    # (Add dummy file creation logic here if needed)


    def main(page: ft.Page):
        page.title = "Mark Attendance/Departure Test"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 850
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # Ensure fonts support Arabic - using Cairo as example
        page.fonts = { "Cairo": "https://github.com/google/fonts/raw/main/apache/cairo/Cairo%5Bslnt%2Cwght%5D.ttf" }
        page.theme = ft.Theme(font_family="Cairo")
        page.rtl = True # <<< Important for layout testing

        # Simple view stack based routing for testing
        def route_change(route: ft.RouteChangeEvent):
            target_route = route.route
            print(f"Route change requested: {target_route}")
            page.views.clear() # Simple navigation: clear all views

            if target_route == "/mark_attendance":
                page.views.append(create_attendance_mark_view(page))
            elif target_route == "/mark_departure":
                page.views.append(create_departure_mark_view(page))
            elif target_route == "/attendance":
                 # Mock view for the previous screen (/attendance)
                 page.views.append(
                     ft.View(
                         "/attendance",
                         [
                             ft.AppBar(title=ft.Text("Attendance Selection (Mock)")),
                             ft.ElevatedButton("Mark Attendance", on_click=lambda _: page.go("/mark_attendance")),
                             ft.ElevatedButton("Mark Departure", on_click=lambda _: page.go("/mark_departure")),
                             # Add a button to simulate coming from a specific action if needed
                         ],
                         bgcolor=PAGE_BGCOLOR, rtl=True
                     )
                 )
            elif target_route == "/add_note":
                 # Mock view for the 'Add Note' screen for testing navigation back
                 page.views.append(
                     ft.View(
                         "/add_note",
                         [
                             ft.AppBar(title=ft.Text("Add Note Page (Mock)")),
                             ft.ElevatedButton("Go Back (Simulated)", on_click=lambda _: page.go("/attendance")), # Test back navigation
                         ],
                          bgcolor=PAGE_BGCOLOR, rtl=True
                     )
                 )
            else:
                 # Default/Initial View
                 page.views.append(
                    ft.View(
                        "/",
                        [
                            ft.AppBar(title=ft.Text("Test Home")),
                            ft.ElevatedButton("Go to Attendance Mark", on_click=lambda _: page.go("/mark_attendance")),
                            ft.ElevatedButton("Go to Departure Mark", on_click=lambda _: page.go("/mark_departure")),
                        ],
                        bgcolor=PAGE_BGCOLOR, rtl=True
                    )
                )
            page.update()

        def view_pop(view_event: ft.ViewPopEvent):
            # Handle back navigation (e.g., browser back button or swipe)
            print(f"View pop requested: Current route {page.route}, Popped view {view_event.view.route}")
            if len(page.views) > 1:
                 page.views.pop()
                 top_view = page.views[-1]
                 # Avoid infinite loop if view_pop triggers another route_change immediately
                 # Check if the target route is different from current displayed route if issues arise
                 print(f"Popped. Navigating back to: {top_view.route}")
                 page.go(top_view.route) # Go to the route of the now top view
            else:
                print("Cannot pop the last view.")


        page.on_route_change = route_change
        page.on_view_pop = view_pop # Handle back button/swipe

        print("Initial page route setup. Navigating to /")
        page.go("/") # Start at the root/test home view

    # --- Run the App ---
    # Ensure the assets_dir path is correct relative to where you RUN python
    print(f"Running Flet app with assets_dir='{assets_dir}'")
    ft.app(
        target=main,
        assets_dir=assets_dir # Pass the calculated assets directory
    )