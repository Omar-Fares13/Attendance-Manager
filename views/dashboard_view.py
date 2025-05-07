# views/dashboard_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import (ft_asset, ICON_REGISTER, ICON_MANAGE,
                           ICON_REPORT, ICON_COLLEGE)

# --- Dashboard Card Function ---
def create_dashboard_card(page: ft.Page, icon_src: str, text: str, action_data: str):
    """Creates a single dashboard card."""
    # Card Styling constants
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    BUTTON_BGCOLOR = "#B58B18" # Default button color (gold)
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 80
    CARD_WIDTH = 220

    # Click handler specific to each card instance
    def card_clicked(e):
        action = e.control.data # Get the action data ('register', 'manage', 'reports', etc.)
        print(f"Dashboard card clicked: {action}")
        page.routes.append('/dashboard')
        # --- NAVIGATION LOGIC ---
        if action == "manage":
            page.go("/attendance")
        elif action == "register":
            page.go("/register_course")
        elif action == "reports":  # <<< ADD THIS CONDITION
            page.go("/report_course") # <<< Navigate to the course report page
        # Add elif for "colleges" later if needed
        elif action == "colleges": 
            page.go("/colleges")
        else:
            # Default behavior: show a snackbar
            page.routes.pop()
            page.show_snack_bar(ft.SnackBar(ft.Text(f"تم النقر على: {text} (No Action Yet)"), open=True))
        # --- END NAVIGATION LOGIC ---

    # Return the card Container (Structure remains the same)
    return ft.Container(
        width=CARD_WIDTH, bgcolor=CARD_BGCOLOR, border_radius=CARD_BORDER_RADIUS,
        padding=ft.padding.symmetric(vertical=25, horizontal=15), ink=True,
        on_click=card_clicked, data=action_data,
        content=ft.Column(
            [
                ft.Image(src=ft_asset(icon_src), width=ICON_SIZE, height=ICON_SIZE, fit=ft.ImageFit.CONTAIN),
                ft.Container(height=20),
                ft.Container(
                    height=50, bgcolor=BUTTON_BGCOLOR, border_radius=BUTTON_BORDER_RADIUS,
                    padding=ft.padding.symmetric(horizontal=10), alignment=ft.alignment.center,
                    content=ft.Text(text, color=TEXT_COLOR, weight=ft.FontWeight.W_600, size=16)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
        )
    )


# --- View Creation Function ---
def create_dashboard_view(page: ft.Page):
    """Creates the Flet View for the Dashboard screen."""

    # --- Define data for each card ---
    # Ensure the 'action' for "استخراج تقارير" is 'reports'
    card_data = [
        {"icon": ICON_REGISTER, "text": "تسجيل دورة جديدة", "action": "register"},
        {"icon": ICON_MANAGE,   "text": "إدارة دورة",        "action": "manage"},
        {"icon": ICON_REPORT,   "text": "استخراج تقارير",   "action": "reports"},   # <<< Action is 'reports'
        {"icon": ICON_COLLEGE,  "text": "إدارة كليات",      "action": "colleges"},  # Placeholder action
    ]

    # Create the dashboard items using the updated card function
    dashboard_items = [ create_dashboard_card(page, item["icon"], item["text"], item["action"]) for item in card_data ]

    # Layout the grid
    dashboard_grid = ft.Container(
        alignment=ft.alignment.center, padding=ft.padding.symmetric(horizontal=30, vertical=40),
        content=ft.Row( controls=dashboard_items, wrap=True, spacing=30, run_spacing=30, alignment=ft.MainAxisAlignment.CENTER, )
    )

    # Get the banner
    banner_control = create_banner(page.width)

    # Return the View
    return ft.View(
        route="/dashboard", padding=0, bgcolor="#E3DCCC",
        controls=[ ft.Column([ banner_control, ft.Container(content=dashboard_grid, expand=True, alignment=ft.alignment.center,) ], expand=True, spacing=0) ]
    )