# views/delete_confirmation_view.py
import flet as ft
from components.banner import create_banner
from logic.delete_all import delete_all_data

def create_delete_confirmation_view(page: ft.Page):
    def on_confirm(e):
        print("Confirmed: Proceeding with data deletion.")
        delete_all_data()
        page.go("/register_course_options")  # Or wherever you want to go after deletion

    def on_cancel(e):
        print("Cancelled deletion.")
        page.go("/register_course_options")  # Or back to a previous screen

    confirm_button = ft.ElevatedButton(
        text="نعم، احذف الكل",
        bgcolor="#C62828",
        color=ft.Colors.WHITE,
        on_click=on_confirm,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        height=50,
    )

    cancel_button = ft.ElevatedButton(
        text="إلغاء",
        bgcolor="#9E9E9E",
        color=ft.Colors.WHITE,
        on_click=on_cancel,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        height=50,
    )

    confirmation_card = ft.Container(
        width=440,
        bgcolor=ft.colors.with_opacity(0.95, ft.Colors.WHITE),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=30, vertical=40),
        content=ft.Column(
            [
                ft.Text("هل أنت متأكد من حذف جميع البيانات؟", size=22, text_align=ft.TextAlign.CENTER),
                ft.Container(height=30),
                confirm_button,
                ft.Container(height=10),
                cancel_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            tight=True,
        )
    )

    return ft.View(
        route="delete_all_data",
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(
                [
                    create_banner(page.width),
                    ft.Container(
                        content=confirmation_card,
                        expand=True,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=50),
                    )
                ],
                expand=True
            )
        ]
    )
