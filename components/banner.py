# components/banner.py
import flet as ft
from utils.assets import asset_path, ft_asset # Use ft_asset for src

def create_banner(page_width):
    """Creates the top banner widget."""
    BANNER_H = 140 # Consistent height
    return ft.Stack(
        height=BANNER_H,
        controls=[
            # 1. Camouflage Background Image
            ft.Image(
                src=ft_asset("camo.png"), # Use relative path for Flet
                width=page_width, # Ensure it spans full width
                height=BANNER_H,
                fit=ft.ImageFit.COVER,
            ),
            # 2. Overlay Content (Logo + Text)
            ft.Container(
                height=BANNER_H,
                padding=ft.padding.symmetric(horizontal=40, vertical=15),
                content=ft.Row(
                    [
                        ft.Image(
                            src=ft_asset("logo.png"), # Use relative path
                            width=80, height=80,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "التربية العسكرية",
                                    size=32, weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    "جامعة عين شمس",
                                    size=18, color=ft.Colors.WHITE
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.END
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ]
    )