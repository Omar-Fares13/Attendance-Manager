import bcrypt
import flet as ft
from dotenv import load_dotenv, find_dotenv, set_key
from pathlib import Path

# Locate or create the .env file at project root
_env_path = find_dotenv()
if not _env_path:
    # Assume project root is two levels up from this file
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    _env_path.touch(exist_ok=True)
else:
    _env_path = Path(_env_path)

# Load environment variables from .env
load_dotenv(dotenv_path=str(_env_path))


def save_password_hash(hash_str: str):
    """Persist the given bcrypt hash to the .env file."""
    set_key(str(_env_path), "APP_PASSWORD_HASH", hash_str)


def create_setup_view(page: ft.Page):
    """Creates the Flet View for setting or resetting the application's password."""
    # --- Handlers ---
    def do_set(e):
        # Clear any previous errors
        pwd1.error_text = None
        pwd2.error_text = None
        page.update()

        # Basic validation
        if not pwd1.value or not pwd2.value:
            if not pwd1.value:
                pwd1.error_text = "الرجاء إدخال كلمة السر"
            if not pwd2.value:
                pwd2.error_text = "الرجاء تأكيد كلمة السر"
            page.update()
            return

        if pwd1.value != pwd2.value:
            pwd2.error_text = "كلمتا السر غير متطابقتين"
            pwd2.value = ""
            pwd2.focus()
            page.update()
            return

        # Hash and save into .env
        raw = pwd1.value.encode("utf-8")
        hash_bytes = bcrypt.hashpw(raw, bcrypt.gensalt())
        hash_str = hash_bytes.decode("utf-8")
        save_password_hash(hash_str)

        # Notify success and redirect to login
        page.snack_bar = ft.SnackBar(
            ft.Text("تم تعيين كلمة السر بنجاح"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
        page.go("/")

    # --- UI Controls ---
    pwd1 = ft.TextField(
        label="كلمة السر الجديدة",
        password=True,
        border_color="#B58B18",
        color="#000000",
        focused_border_color="#B58B18",
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18"),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=15),
        on_submit=do_set
    )

    pwd2 = ft.TextField(
        label="تأكيد كلمة السر",
        password=True,
        border_color="#B58B18",
        color="#000000",
        focused_border_color="#B58B18",
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18"),
        content_padding=ft.padding.symmetric(horizontal=15, vertical=15),
        on_submit=do_set
    )

    set_btn = ft.ElevatedButton(
        text="تعيين كلمة السر",
        bgcolor="#B58B18",
        color=ft.Colors.WHITE,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=do_set
    )

    setup_card = ft.Container(
        width=440,
        bgcolor=ft.colors.with_opacity(0.95, ft.Colors.WHITE),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=30, vertical=40),
        content=ft.Column(
            [
                pwd1,
                ft.Container(height=20),
                pwd2,
                ft.Container(height=20),
                set_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=0,
            tight=True
        )
    )

    # Optionally replace with your banner
    banner_control = ft.Text("", width=0)

    return ft.View(
        route="/setup",
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(
                        content=setup_card,
                        expand=True,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=50),
                    )
                ],
                expand=True,
                spacing=0
            )
        ]
    )
