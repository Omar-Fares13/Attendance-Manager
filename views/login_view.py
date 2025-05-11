import os
import bcrypt
import flet as ft
from components.banner import create_banner
from logic.delete_all import delete_all_data
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Locate or create .env at project root
_env_path = find_dotenv()
if not _env_path:
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    _env_path.touch(exist_ok=True)

# Load environment variables
load_dotenv(dotenv_path=str(_env_path))


def create_login_view(page: ft.Page):
    """Creates the Flet View for the Login screen with secure password handling and reset mechanism."""
    target = "/" + page.route.split("/")[-1]

    # --- Login logic ---
    def do_login(e):
        load_dotenv(dotenv_path=str(_env_path), override=True)

        raw_hash = os.getenv("APP_PASSWORD_HASH", "").strip().strip('\"').strip("'")
        pwd = pwd_field.value.encode('utf-8')
        try:
            if raw_hash and bcrypt.checkpw(pwd, raw_hash.encode('utf-8')):
                page.snack_bar = ft.SnackBar(ft.Text("تم تسجيل الدخول بنجاح"), bgcolor=ft.Colors.GREEN)
                page.snack_bar.open = True
                page.update()
                page.go(target)
                return
        except ValueError:
            pwd_field.error_text = "حدث خطأ داخلي. حاول إعادة تعيين كلمة السر."
            pwd_field.value = ""
            pwd_field.focus()
            page.update()
            return
        pwd_field.error_text = "كلمة المرور غير صحيحة"
        pwd_field.value = ""
        pwd_field.focus()
        page.update()

    # --- Reset logic ---
    def confirm_reset(e):
        _close_dialog()
        delete_all_data()
        page.snack_bar = ft.SnackBar(
            ft.Text("تمت إعادة ضبط البيانات. الرجاء إعداد كلمة مرور جديدة."),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
        page.go("/setup")

    def open_reset_dialog(e):
        dialog.open = True
        page.update()

    # --- Controls ---
    pwd_field = ft.TextField(
        label="كلمة السر",
        password=True,
        border_color="#B58B18",
        color="#000000",
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

    reset_btn = ft.TextButton(
        text="نسيت كلمة السر؟",
        on_click=open_reset_dialog,
        style=ft.ButtonStyle()
    )

    back_btn = ft.TextButton(
        text="رجوع",
        icon=ft.icons.ARROW_BACK,
        on_click=lambda e: page.go("/dashboard"),
        style=ft.ButtonStyle()
    )

    # Confirmation dialog
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("تأكيد إعادة ضبط البيانات"),
        content=ft.Text("هل أنت متأكد أنك تريد حذف جميع البيانات وإعادة ضبط كلمة المرور؟"),
        actions=[
            ft.TextButton("إلغاء", on_click=lambda e: _close_dialog()),
            ft.ElevatedButton("تأكيد", on_click=confirm_reset)
        ]
    )

    def _close_dialog():
        dialog.open = False
        page.update()

    # Login card layout
    login_card = ft.Container(
        width=440,
        bgcolor=ft.colors.with_opacity(0.95, ft.Colors.WHITE),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=30, vertical=40),
        content=ft.Column(
            [
                pwd_field,
                ft.Container(height=20),
                login_btn,
                reset_btn,
                back_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=5,
            tight=True
        )
    )

    banner_control = create_banner(page.width)

    # Combine back button, banner, and login card
    header = ft.Row([ ft.Container()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    return ft.View(
        route="/login",
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            dialog,
            ft.Column([
                header,
                banner_control,
                ft.Container(
                    content=login_card,
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=50),
                )
            ], expand=True, spacing=0)
        ]
    )