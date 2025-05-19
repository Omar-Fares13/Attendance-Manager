# views/dashboard_view.py

import flet as ft
from logic.pdf_generator import generate_qr_pdfs
from components.banner import create_banner
from utils.assets import (ft_asset, ICON_REGISTER, ICON_MANAGE,
                          ICON_REPORT, ICON_COLLEGE,ICON_QR_CODE)

target = None
def set_target(value):
    global target
    target = value


# --- Dashboard Card Function (unchanged) ---
def create_dashboard_card(page: ft.Page, icon_src: str, text: str, action_data: str):
    CARD_BGCOLOR = ft.colors.with_opacity(0.98, ft.Colors.WHITE)
    BUTTON_BGCOLOR = "#B58B18"
    TEXT_COLOR = ft.Colors.WHITE
    CARD_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 8
    ICON_SIZE = 80
    CARD_WIDTH = 220
    def card_clicked(e):
        action = e.control.data
        page.routes.append('/dashboard')
        if action == "manage":
            page.go("/attendance")
        elif action == "register":
            page.go("/register_course")
        elif action == "reports":
            page.go("/report_course")
        elif action == "colleges":
            page.go("/colleges")
        elif action == "generate_qr_pdfs":
            # This is our new action
            generate_qr_pdfs(page)
        else:
            page.routes.pop()
            page.show_snack_bar(ft.SnackBar(ft.Text(f"تم النقر على: {text}"), open=True))

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
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

# --- View Creation Function with Dropdown ---
def create_dashboard_view(page: ft.Page):
    def navigate_target(e):
        page.go(target)
    dropdown = ft.Dropdown(
    options=[
    ft.dropdown.Option(key="/register_course",   text="تسجيل دورة جديدة"),
    ft.dropdown.Option(key="/attendance",        text="قائمة الحضور"),
    ft.dropdown.Option(key="/manage_students",   text="إدارة الطلاب"),
    ft.dropdown.Option(key="/search_student",    text="البحث عن طالب"),
    ft.dropdown.Option(key="/report_course",     text="استخراج التقارير"),
    ],
        value="all",
        hint_text="اختر الفئة",
        width=200,
        on_change=lambda e: set_target(e.control.value),
    )
    dropdown_row = ft.Container(
        content=ft.Row([dropdown], alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(vertical=10, horizontal=30),
    )

    go_button = ft.ElevatedButton(
        text="ذهاب",
        bgcolor=ft.colors.BLACK,
        color=ft.colors.WHITE,
        on_click=navigate_target,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    dropdown_row = ft.Container(
        content=ft.Row(
            [dropdown, ft.Container(width=10), go_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,  # we’re using that spacer for separation
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=30),
    )
    # Dashboard cards
    card_data = [
        {"icon": ICON_REGISTER, "text": "تسجيل دورة جديدة", "action": "register"},
        {"icon": ICON_MANAGE,   "text": "إدارة دورة",        "action": "manage"},
        {"icon": ICON_COLLEGE,  "text": "إدارة كليات",       "action": "colleges"},
        {"icon": ICON_QR_CODE,  "text": "إنشاء ملفات QR",    "action": "generate_qr_pdfs"},
        {"icon": ICON_REPORT,   "text": "استخراج تقارير",    "action": "reports"},
    ]
    dashboard_items = [
        create_dashboard_card(page, item["icon"], item["text"], item["action"])
        for item in card_data
    ]
    dashboard_grid = ft.Row(
        controls=dashboard_items,
        wrap=True,
        spacing=30,
        run_spacing=30,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    banner_control = create_banner(page.width)

    return ft.View(
        route="/dashboard",
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(
                [
                    banner_control,
                    dropdown_row,
                    ft.Container(
                        content=dashboard_grid,
                        expand=True,
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(horizontal=30, vertical=40),
                    )
                ],
                expand=True,
                spacing=30,
            )
        ]
    )
