# views/register_course_options_view.py
import flet as ft
from components.banner import create_banner
# Import necessary icons and asset helper
from utils.assets import (ft_asset, ICON_TRASH, ICON_FOLDER_UPLOAD, ICON_CAMERA_QR)


attributes = {}

# --- Reusable Card Function (Adapt from previous views) ---
def create_option_card(page: ft.Page, icon_src: str, text: str, button_bgcolor: str, action_data: str):
    """Creates a single card for course registration options."""
    # Card Styling
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 80 # Adjust size as needed
    CARD_WIDTH = 220 # Adjust width for three cards

    gender = page.route.split('=')[-1]
    if gender == 'male':
        attributes['is_male'] = '1'
    else:
        attributes['is_male'] = '0'

    def card_clicked(e):
        action = e.control.data
        print(f"Register option card clicked: {action}")
        # --- NAVIGATION & ACTION LOGIC ---
        target = ''
        if action == "qr_imaging": # Check if the QR/Camera card was clicked
            target = "/camera_qr" # <<< Navigate to the camera page
        elif action == "clear_data":
            page.show_snack_bar(ft.SnackBar(ft.Text("سيتم مسح البيانات الحالية... (تحتاج لتأكيد)"), open=True))
        elif action == "add_file":
            target = "/course_file_upload"
        else:
            # Fallback for any unexpected action
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Action: {action}"), open=True))
        target += '?male=' + attributes['is_male']
        page.go(target)


    return ft.Container(
        width=CARD_WIDTH,
        bgcolor=CARD_BGCOLOR,
        border_radius=CARD_BORDER_RADIUS,
        padding=ft.padding.symmetric(vertical=25, horizontal=15),
        ink=True, # Add ripple effect
        on_click=card_clicked, # Assign click handler
        data=action_data, # Store action identifier
        content=ft.Column(
            [
                # Icon
                ft.Image(
                    src=ft_asset(icon_src),
                    width=ICON_SIZE, height=ICON_SIZE,
                    fit=ft.ImageFit.CONTAIN,
                ),
                # Spacer
                ft.Container(height=20),
                # Button-like area
                ft.Container(
                    height=50,
                    bgcolor=button_bgcolor, # Use passed color
                    border_radius=BUTTON_BORDER_RADIUS,
                    padding=ft.padding.symmetric(horizontal=10),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        text, color=TEXT_COLOR,
                        weight=ft.FontWeight.W_600, size=16, # Adjust text size if needed
                        text_align=ft.TextAlign.CENTER # Center text in button
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
    )


def create_register_course_options_view(page: ft.Page):
    """Creates the Flet View for the Register Course Options screen."""

    # --- Controls ---
    # Back button navigation
    def go_back(e):
        page.go("/register_course") # Go back to gender selection view

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # RTL back arrow
        icon_color="#B58B18",
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    # Page Title (same as previous step)
    page_title = ft.Text(
        "تسجيل دورة جديدة",
        size=32, weight=ft.FontWeight.BOLD, color="#B58B18"
    )

    # --- Card Data for this specific page ---
    # Ensure action data matches keys in card_clicked handler
    card_data = [
        {"icon": ICON_TRASH,         "text": "مسح البيانات الحالية", "color": "#C83737", "action": "clear_data"}, # Red
        {"icon": ICON_FOLDER_UPLOAD, "text": "اضافة ملف الدورة الجديدة", "color": "#B58B18", "action": "add_file"},   # Gold
        {"icon": ICON_CAMERA_QR,     "text": "تصوير و QR",        "color": "#B58B18", "action": "qr_imaging"},  # Gold, action triggers navigation
    ]

    # --- Create Card Controls ---
    option_items = [
        create_option_card(page, item["icon"], item["text"], item["color"], item["action"])
        for item in card_data
    ]

    # --- Arrange Cards ---
    cards_row = ft.Container(
        padding=ft.padding.only(top=20), # Padding above cards
        alignment = ft.alignment.center, # Center the Row itself
        content=ft.Row(
            controls=option_items,
            wrap=True, # Allow wrapping for responsiveness
            spacing=30, # Horizontal space between cards
            run_spacing=20, # Vertical space if cards wrap
            alignment=ft.MainAxisAlignment.CENTER, # Center cards horizontally within the row
        )
    )

    # --- Get Banner ---
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
            # Row containing the option cards
             cards_row,
        ],
        expand=True, # Fill available vertical space
        scroll=ft.ScrollMode.ADAPTIVE, # Enable scrolling if content overflows
        horizontal_alignment=ft.CrossAxisAlignment.CENTER # Center the content (cards row)
    )

    # --- View Definition ---
    return ft.View(
        route="/register_course_options", # Route for this view
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