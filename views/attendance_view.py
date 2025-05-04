# views/attendance_view.py
import flet as ft
from components.banner import create_banner
# Import necessary icons and asset helper
# Make sure your utils.assets module and the constants are defined correctly
try:
    from utils.assets import (ft_asset, ICON_ATTENDANCE, ICON_DEPARTURE,
                               ICON_STUDENT_DATA)
except ImportError:
    # Provide dummy paths if utils.assets is not available (for standalone testing)
    print("Warning: utils.assets not found. Using placeholder paths.")
    def ft_asset(path): return path # Pass path directly
    ICON_ATTENDANCE = "icons/attendance_icon.png" # Example placeholder path
    ICON_DEPARTURE = "icons/departure_icon.png"   # Example placeholder path
    ICON_STUDENT_DATA = "icons/student_data_icon.png" # Example placeholder path


# --- Reusable Card Function ---
def create_action_card(page: ft.Page, icon_src: str, text: str, button_bgcolor: str, action_data: str):
    """Creates a single card for action pages like Attendance/Departure."""
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 80
    CARD_WIDTH = 220 # Keep original width or adjust if needed

    def card_clicked(e):
        action = e.control.data
        print(f"Action card clicked: {action}")

        # --- NAVIGATION LOGIC ---
        if action == "manage_students":
            page.go("/manage_students")
        elif action == "mark_attendance":   # <<< UPDATED THIS
            page.go("/mark_attendance")     # <<< Navigate to attendance marking view
        elif action == "mark_departure":    # <<< UPDATED THIS
            page.go("/mark_departure")      # <<< Navigate to departure marking view
        else:
            # Default placeholder action for any other undefined actions
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Action: {action} (Navigation Not Defined Yet)"), open=True))
        # --- END NAVIGATION LOGIC ---

    # Return the card Container
    return ft.Container(
        width=CARD_WIDTH,
        bgcolor=CARD_BGCOLOR,
        border_radius=CARD_BORDER_RADIUS,
        padding=ft.padding.symmetric(vertical=25, horizontal=15),
        ink=True, # Enable ink effect on click
        on_click=card_clicked,
        data=action_data, # Store the action identifier
        content=ft.Column(
            [
                ft.Image(
                    # Use ft_asset helper if you have one, otherwise pass src directly
                    src=ft_asset(icon_src) if 'ft_asset' in globals() else icon_src,
                    width=ICON_SIZE, height=ICON_SIZE,
                    fit=ft.ImageFit.CONTAIN,
                    # Add error_content if image fails to load
                    error_content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED, size=ICON_SIZE, color=ft.colors.BLACK26)
                ),
                ft.Container(height=20), # Spacer
                ft.Container( # Button-like area at the bottom of the card
                    height=50,
                    bgcolor=button_bgcolor,
                    border_radius=BUTTON_BORDER_RADIUS,
                    padding=ft.padding.symmetric(horizontal=10),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        text, color=TEXT_COLOR,
                        weight=ft.FontWeight.W_600, size=16,
                        text_align=ft.TextAlign.CENTER # Ensure text inside button is centered
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0, # No extra space added by the column itself
        )
    )


def create_attendance_view(page: ft.Page):
    """Creates the Flet View for the Attendance/Departure selection screen."""

    # --- Back Button Logic ---
    def go_back(e):
        # Assuming the previous view is the dashboard or main menu
        # Adjust the target route if necessary
        page.go("/dashboard") # Explicitly navigate back to dashboard

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # RTL back arrow
        icon_color="#B58B18", # Gold color
        tooltip="العودة إلى لوحة التحكم", # Tooltip in Arabic
        on_click=go_back,
        icon_size=30
    )

    # --- Page Title ---
    # Use the title from the original image if it differs, otherwise keep this
    page_title = ft.Text(
        "إدارة دورة جارية", # Title text
        size=28, # Adjust size as needed
        weight=ft.FontWeight.BOLD,
        color="#B58B18" # Gold color
    )

    # --- Card Data for THIS specific page ---
    # Keys in dict should match arguments for create_action_card
    # 'action' values must match those checked in card_clicked
    card_data = [
        {"icon": ICON_ATTENDANCE,     "text": "حضور",              "color": "#6FA03C", "action": "mark_attendance"}, # Green color for attendance
        {"icon": ICON_DEPARTURE,      "text": "انصراف",             "color": "#C83737", "action": "mark_departure"}, # Red color for departure
        {"icon": ICON_STUDENT_DATA,   "text": "إدارة بيانات الطلبة", "color": "#B58B18", "action": "manage_students"}, # Gold color for student mgmt
    ]

    # --- Create Card Controls ---
    action_items = [
        create_action_card(page, item["icon"], item["text"], item["color"], item["action"])
        for item in card_data
    ]

    # --- Arrange Cards ---
    # Use a Container to allow centering and padding for the Row of cards
    cards_row_container = ft.Container(
        # padding=ft.padding.symmetric(horizontal=30, vertical=20),
        alignment = ft.alignment.center, # Center the Row itself within the container
        expand=True, # Allow the container to take available vertical space if needed
        content=ft.Row(
            controls=action_items,
            wrap=True, # Allow cards to wrap to the next line on smaller screens
            spacing=40, # Horizontal space between cards
            run_spacing=30, # Vertical space between rows if cards wrap
            alignment=ft.MainAxisAlignment.CENTER, # Center cards horizontally within the row
            vertical_alignment=ft.CrossAxisAlignment.CENTER # Center cards vertically if they wrap
        )
    )

    # --- Get Banner ---
    # Ensure create_banner function is available and imported correctly
    try:
        banner_control = create_banner(page.width)
    except NameError:
        print("Warning: create_banner function not found. Using placeholder.")
        banner_control = ft.Container(height=80, bgcolor="#5C5341", content=ft.Text("Mock Banner", color=ft.colors.WHITE))


    # --- Page Content Layout (Below Banner) ---
    content_column = ft.Column(
        [
            # Top row with Title and Back button
            ft.Container(
                padding=ft.padding.only(top=15, left=30, right=30, bottom=10),
                content=ft.Row(
                    [
                        # Empty container to push title towards center (if needed)
                        # ft.Container(expand=True),
                        page_title,
                        # Use alignment instead of spacers for better control
                        # ft.Container(expand=True),
                        back_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Puts space between title and button
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            ft.Divider(height=10, color=ft.colors.TRANSPARENT), # Small spacer
            # Row containing the cards (wrapped in its container)
             cards_row_container,
             # Add padding at the bottom if needed
             ft.Container(height=20)
        ],
        expand=True, # Fill available vertical space below the banner
        scroll=ft.ScrollMode.ADAPTIVE, # Enable scrolling if content overflows
        horizontal_alignment=ft.CrossAxisAlignment.CENTER # Center content horizontally
    )

    # --- View Definition ---
    return ft.View(
        route="/attendance", # Route for this specific view
        padding=0, # No padding on the view itself
        bgcolor="#E3DCCC", # Consistent background color
        controls=[
            # Main structure: Banner + Content Column
            ft.Column(
                [
                    banner_control,
                    content_column # The column containing title, cards, etc.
                ],
                expand=True, # Make this main column fill the page height
                spacing=0 # No space between banner and content column
            )
        ]
    )

# --- Example Usage (for testing this view file standalone) ---
if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Attendance/Departure Selection"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 900
        page.window_height = 700
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Mock banner if the real one isn't available
        # global create_banner
        # def create_mock_banner(width):
        #     return ft.Container(height=80, bgcolor="#5C5341", content=ft.Row([ft.Text("Mock Banner", color=ft.colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER))
        # create_banner = create_mock_banner

        # Define routes for testing navigation
        def route_change(route):
            print(f"Navigating to: {route}")
            page.views.clear() # Simple navigation: clear all views
            if route == "/attendance":
                page.views.append(create_attendance_view(page))
            elif route == "/mark_attendance":
                page.views.append(ft.View(route, [ft.Text("Mock Attendance Mark Page"), ft.ElevatedButton("Back", on_click=lambda _: page.go("/attendance"))]))
            elif route == "/mark_departure":
                page.views.append(ft.View(route, [ft.Text("Mock Departure Mark Page"), ft.ElevatedButton("Back", on_click=lambda _: page.go("/attendance"))]))
            elif route == "/manage_students":
                page.views.append(ft.View(route, [ft.Text("Mock Manage Students Page"), ft.ElevatedButton("Back", on_click=lambda _: page.go("/attendance"))]))
            elif route == "/dashboard":
                 page.views.append(ft.View(route, [ft.Text("Mock Dashboard Page"), ft.ElevatedButton("Go to Attendance", on_click=lambda _: page.go("/attendance"))]))
            else:
                 # Default to dashboard or attendance view if route is unknown
                 page.views.append(create_attendance_view(page))

            if not page.views: # Ensure there's always at least one view
                 page.views.append(create_attendance_view(page))

            page.update()

        page.on_route_change = route_change
        page.go("/attendance") # Start at the attendance selection view

    # Make sure assets are found if running standalone
    # Adjust assets_dir path relative to where you run the script
    # E.g., if run from project root and views/ is a subfolder:
    # ft.app(target=main, assets_dir="assets")
    # If run directly from views/ folder:
    # ft.app(target=main, assets_dir="../assets")
    ft.app(target=main) # Run without explicit assets_dir if paths are absolute or handled by utils.assets