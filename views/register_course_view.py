# views/register_course_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset, ICON_FEMALE, ICON_MALE

# --- Reusable Card Function ---
def create_gender_card(page: ft.Page, icon_src: str, text: str, button_bgcolor: str, action_data: str):
    """Creates a single card for gender selection."""
    # Card Styling (remain the same)
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 90
    CARD_WIDTH = 200

    def card_clicked(e):
        action = e.control.data # 'male' or 'female'
        print(f"Gender card clicked: {action}")
        # --- NAVIGATION LOGIC ---
        # Navigate to the next step regardless of gender selected
        page.go("/register_course_options") # <<< Navigate to the new options page
        # ---

    # Return Container (structure remains the same)
    return ft.Container(
        width=CARD_WIDTH, bgcolor=CARD_BGCOLOR, border_radius=CARD_BORDER_RADIUS,
        padding=ft.padding.symmetric(vertical=30, horizontal=15), ink=True,
        on_click=card_clicked, data=action_data,
        content=ft.Column(
            [
                ft.Image(src=ft_asset(icon_src), width=ICON_SIZE, height=ICON_SIZE, fit=ft.ImageFit.CONTAIN),
                ft.Container(height=25),
                ft.Container(
                    height=45, bgcolor=button_bgcolor, border_radius=BUTTON_BORDER_RADIUS,
                    padding=ft.padding.symmetric(horizontal=10), alignment=ft.alignment.center,
                    content=ft.Text(text, color=TEXT_COLOR, weight=ft.FontWeight.W_600, size=18)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
        )
    )

# --- View Creation Function ---
def create_register_course_view(page: ft.Page):
    """Creates the Flet View for the Register New Course screen."""

    # ... (back button, title remain the same) ...
    def go_back(e): page.views.pop(); top_view = page.views[-1]; page.go(top_view.route)
    back_button = ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18", tooltip="العودة", on_click=go_back, icon_size=30)
    page_title = ft.Text("تسجيل دورة جديدة", size=32, weight=ft.FontWeight.BOLD, color="#B58B18")

    # --- Card Data (remain the same) ---
    card_data = [
        {"icon": ICON_FEMALE, "text": "إناث", "color": "#EF5350", "action": "female"},
        {"icon": ICON_MALE,   "text": "ذكور", "color": "#42A5F5", "action": "male"},
    ]

    # ... (Rest of the function remains the same: create items, layout row, get banner, return View) ...
    selection_items = [ create_gender_card(page, item["icon"], item["text"], item["color"], item["action"]) for item in card_data ]
    cards_row = ft.Container(
        padding=ft.padding.only(top=30), alignment = ft.alignment.center,
        content=ft.Row( controls=selection_items, spacing=40, alignment=ft.MainAxisAlignment.CENTER )
    )
    banner_control = create_banner(page.width)
    content_column = ft.Column(
        [ ft.Container(padding=ft.padding.only(top=20, bottom=10, left=30, right=30), content=ft.Row([page_title, back_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)), cards_row ],
        expand=True, scroll=ft.ScrollMode.ADAPTIVE, horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    return ft.View(
        route="/register_course", padding=0, bgcolor="#E3DCCC",
        controls=[ ft.Column([ banner_control, content_column ], expand=True, spacing=0 ) ]
    )