# views/manage_course_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import (ft_asset, ICON_ATTENDANCE, ICON_COLLEGE_MANAGE,
                           ICON_STUDENT_DATA)

# --- Reusable Card Function for this page ---
def create_management_card(page: ft.Page, icon_src: str, text: str, button_bgcolor: str, action_data: str):
    """Creates a single card for the course management page."""
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 80
    CARD_WIDTH = 220

    def card_clicked(e):
        action = e.control.data
        print(f"Management card clicked: {action}")

        # --- NAVIGATION LOGIC ---
        if action == "attendance":
            page.go("/attendance")
        elif action == "manage_students": # Check for the student management action
            page.go("/manage_students")  # <<< Navigate to the student management view
        # Add elif for "manage_colleges" if needed later
        # elif action == "manage_colleges":
        #     page.go("/college_management")
        else:
            # Default placeholder action for unhandled actions (like manage_colleges for now)
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Action: {action} (Not Implemented Yet)"), open=True))
        # --- END NAVIGATION LOGIC ---

    # Return the card Container
    return ft.Container(
        width=CARD_WIDTH,
        bgcolor=CARD_BGCOLOR,
        border_radius=CARD_BORDER_RADIUS,
        padding=ft.padding.symmetric(vertical=25, horizontal=15),
        ink=True,
        on_click=card_clicked,
        data=action_data,
        content=ft.Column(
             [
                ft.Image(
                    src=ft_asset(icon_src),
                    width=ICON_SIZE, height=ICON_SIZE,
                    fit=ft.ImageFit.CONTAIN
                ),
                ft.Container(height=20), # Spacer
                ft.Container( # Button-like area
                    height=50,
                    bgcolor=button_bgcolor,
                    border_radius=BUTTON_BORDER_RADIUS,
                    padding=ft.padding.symmetric(horizontal=10),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        text, color=TEXT_COLOR,
                        weight=ft.FontWeight.W_600, size=16
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
    )


def create_manage_course_view(page: ft.Page):
    """Creates the Flet View for the Manage Course screen."""

    # --- Back Button Logic ---
    def go_back(e):
        page.go("/dashboard")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # RTL back arrow
        icon_color="#B58B18",
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    # --- Page Title ---
    page_title = ft.Text(
        "إدارة دورة جارية",
        size=28,
        weight=ft.FontWeight.BOLD,
        color="#B58B18"
    )

    # --- Card Data for THIS page ---
    # Ensure the 'action' data matches the keys used in the card_clicked handler
    card_data = [
        {"icon": ICON_ATTENDANCE,     "text": "حضور/انصراف",    "color": "#6FA03C", "action": "attendance"},
        {"icon": ICON_COLLEGE_MANAGE, "text": "إدارة كليات",      "color": "#5C544A", "action": "manage_colleges"}, # Placeholder action
        {"icon": ICON_STUDENT_DATA,   "text": "إدارة بيانات الطلبة", "color": "#B58B18", "action": "manage_students"}, # <<< Action triggers navigation
    ]

    # --- Create Card Controls ---
    management_items = [
        create_management_card(page, item["icon"], item["text"], item["color"], item["action"])
        for item in card_data
    ]

    # --- Arrange Cards ---
    cards_row = ft.Container(
        padding=ft.padding.symmetric(horizontal=30, vertical=20),
        alignment = ft.alignment.center, # Center the Row itself
        content=ft.Row(
            controls=management_items,
            wrap=True, # Allow wrapping if needed
            spacing=30,
            run_spacing=30,
            alignment=ft.MainAxisAlignment.CENTER, # Center cards within the row
        )
    )

    # --- Get Banner ---
    banner_control = create_banner(page.width)

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            # Top row with Title and Back button
            ft.Container(
                padding=ft.padding.only(top=20, left=30, right=30),
                content=ft.Row(
                    [
                        page_title,
                        back_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            # Row containing the cards
             cards_row,
        ],
        expand=True, # Fill available vertical space
        scroll=ft.ScrollMode.ADAPTIVE, # Enable scrolling if content overflows
        horizontal_alignment=ft.CrossAxisAlignment.CENTER # Center content horizontally
    )

    # --- View Definition ---
    return ft.View(
        route="/manage_course", # Route for this specific view
        padding=0,
        bgcolor="#E3DCCC", # Consistent background
        controls=[
            # Main structure: Banner + Content Column
            ft.Column(
                [
                    banner_control,
                    content_column
                ],
                expand=True, # Fill page height
                spacing=0 # No space between banner and content
            )
        ]
    )