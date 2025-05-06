# views/login_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset # No need for asset_path here directly

# You might move this to a config file later
DUMMY_PASSWORD = "password"
def create_login_view(page: ft.Page):
    """Creates the Flet View for the Login screen."""
    target = "/" + page.route.split("/")[-1]

    def do_login(e):
        """Handles the login button click."""
        if pwd_field.value == DUMMY_PASSWORD:
            print("Login successful!")
            # Navigate to the dashboard view
            page.go(target)
        else:
            print("Login failed")
            pwd_field.error_text = "كلمة المرور غير صحيحة"
            pwd_field.value = "" # Clear password on error
            pwd_field.focus()
            page.update() # Update only the view containing the field
            
    # --- Controls ---
    pwd_field = ft.TextField(
        label="كلمة السر",
        password=True,
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18"),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=15),
        on_submit=do_login
    )

    login_btn = ft.ElevatedButton(
        text="تسجيل الدخول",
        bgcolor="#B58B18",
        color=ft.Colors.WHITE,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=do_login
    )

    login_card = ft.Container(
        # Dynamic width will be handled by on_resize in main.py or here if needed
        width=440, # Default/Max width
        bgcolor=ft.colors.with_opacity(0.95, ft.Colors.WHITE),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=30, vertical=40),
        content=ft.Column(
            [
                pwd_field,
                ft.Container(height=20),
                login_btn,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=0,
            tight=True
        )
    )

    # --- Responsive Handler specific to this view's elements if needed ---
    # Example: Adjust login_card width (can also be done globally in main.py)
    login_card_ref = ft.Ref[ft.Container]() # Create a reference if needed elsewhere
    login_card.ref = login_card_ref

    def on_view_resize(e=None):
        w = page.width or 0
        target_card = login_card # Direct reference works here

        if target_card: # Check if card exists
             if w < 500: target_card.width = w * 0.9
             elif w < 800: target_card.width = w * 0.7
             else: target_card.width = 440
             target_card.update() # Update only the card

    # --- View Definition ---
    # Get banner (pass current page width)
    banner_control = create_banner(page.width)

    return ft.View(
        route="/", # Or "/login"
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(
                        content=login_card,
                        expand=True,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=50),
                    )
                ],
                expand=True,
                spacing=0
            )
        ],
        # Associate the resize handler with this view
        # Note: A global on_resize in main.py might be simpler if resizing affects multiple views similarly (like the banner)
        # on_resize=on_view_resize
    )