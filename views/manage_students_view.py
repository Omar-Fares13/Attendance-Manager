# views/manage_students_view.py
import flet as ft
from components.banner import create_banner
# Import necessary icons and asset helper
from utils.assets import (ft_asset, ICON_ADD_STUDENT, ICON_SEARCH_STUDENT)
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# --- Reusable Card Function ---
def create_action_card(page: ft.Page, icon_src: str, text: str, button_bgcolor: str, action_data: str):
    # ... (Styling constants remain the same) ...
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 80
    CARD_WIDTH = 220

    def card_clicked(e):
        action = e.control.data
        print(f"Manage Students card clicked: {action}")

        # --- NAVIGATION LOGIC ---
        if action == "search_student": # Check if the search card was clicked
            page.go("/search_student") # <<< Navigate to the new search view route
        # Add elif for "add_student" later
        elif action == "add_student":
            page.go("/add_student")
        else:
            # Default placeholder action
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Action: {action} (Not Implemented Yet)"), open=True))
        # --- END NAVIGATION LOGIC ---

    # ... (Return ft.Container structure remains the same) ...
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
                ft.Image(src=ft_asset(icon_src),width=ICON_SIZE, height=ICON_SIZE,fit=ft.ImageFit.CONTAIN),
                ft.Container(height=20),
                ft.Container(
                    height=50, bgcolor=button_bgcolor, border_radius=BUTTON_BORDER_RADIUS,
                    padding=ft.padding.symmetric(horizontal=10), alignment=ft.alignment.center,
                    content=ft.Text(text, color=TEXT_COLOR, weight=ft.FontWeight.W_600, size=16)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
        )
    )


# --- Main View Creation Function ---
def create_manage_students_view(page: ft.Page):
    """Creates the Flet View for the Manage Student Data screen."""
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    # ... (Back button and Title remain the same) ...
    def go_back(e):
        page.go("/attendance")
    back_button = ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18", tooltip="العودة", on_click=go_back, icon_size=30)
    page_title = ft.Text("ادارة بيانات الطلبة", size=28, weight=ft.FontWeight.BOLD, color="#B58B18")

    # --- Card Data ---
    # Ensure 'action' for Search card is 'search_student'
    card_data = [
        {"icon": ICON_ADD_STUDENT,     "text": "اضافة طالب جديد", "color": "#6FA03C", "action": "add_student"}, # Placeholder action
        {"icon": ICON_SEARCH_STUDENT,  "text": "بحث",             "color": "#B58B18", "action": "search_student"}, # <<< Action triggers navigation
    ]

    # ... (Rest of the view creation remains the same) ...
    action_items = [ create_action_card(page, item["icon"], item["text"], item["color"], item["action"]) for item in card_data ]
    cards_row = ft.Container(
        padding=ft.padding.symmetric(horizontal=30, vertical=20), alignment = ft.alignment.center,
        content=ft.Row( controls=action_items, spacing=30, run_spacing=30, alignment=ft.MainAxisAlignment.CENTER )
    )
    banner_control = create_banner(page.width)
    content_column = ft.Column([ ft.Container(padding=ft.padding.only(top=20, left=30, right=30), content=ft.Row([page_title, back_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)), cards_row], expand=True, scroll=ft.ScrollMode.ADAPTIVE, horizontal_alignment=ft.CrossAxisAlignment.CENTER )
    return ft.View( route="/manage_students", padding=0, bgcolor="#E3DCCC", controls=[ ft.Column([ banner_control, content_column ], expand=True, spacing=0 ) ] )