import asyncio
import flet as ft
# --- Splash Screen View Creation Function ---
def create_main_screen_view(page: ft.Page):
    """Creates the 'Splash Screen' view: shows a logo then navigates to dashboard."""

    # Load splash image from assets
    splash_image = ft.Image(
        src="assets/splash.png",  # Ensure this file exists in your assets folder
        fit=ft.ImageFit.CONTAIN,
        width=page.window_width if page.window_width else 1440,
        height=page.window_height if page.window_height else 1080,
    )

    # Timer to navigate after 3 seconds (3000 ms)
    async def _go_dashboard():
        print("wait")
        await asyncio.sleep(1.0)
        page.routes = []
        page.go("/dashboard")
    page.run_task(_go_dashboard)

    # Build the view
    view = ft.View(
        route="/splash",  # will be used by main app routing
        padding=0,
        controls=[
            ft.Column(
                [splash_image],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
        ]
    )

    return view
