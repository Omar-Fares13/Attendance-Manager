# views/confirm_course_view.py

import flet as ft
from components.banner import create_banner
import time
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# Theme constants
class Theme:
    BG_COLOR = "#E3DCCC"
    PRIMARY_COLOR = "#B58B18"
    TEXT_COLOR_DARK = "#333333"
    WHITE_COLOR = ft.colors.WHITE
    CONFIRM_BUTTON_COLOR = ft.colors.GREEN_700
    CANCEL_BUTTON_COLOR = ft.colors.GREY_700
    DONE_BUTTON_COLOR = ft.colors.GREEN_900
    FONT_FAMILY_REGULAR = "Tajawal"
    FONT_FAMILY_BOLD = "Tajawal-Bold"


def create_confirm_course_view(page: ft.Page):
    """Creates the Flet View for confirming the course details before final registration."""

    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_dashboard(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    # --- References for interactive controls ---
    confirm_button_ref = ft.Ref[ft.ElevatedButton]()
    dashboard_button_ref = ft.Ref[ft.ElevatedButton]()

    # --- Load pending course data ---
    def load_course_data():
        course_name = page.client_storage.get("pending_course_name") or "اسم الدورة غير محدد"
        course_date = page.client_storage.get("pending_course_date") or "التاريخ غير محدد"
        print(f"[Confirm View] Loaded: Name='{course_name}', Date='{course_date}'")
        return course_name, course_date

    course_name, course_date = load_course_data()

    # --- Event handlers ---
    def final_confirm_registration(e):
        print("[Confirm View] Final registration confirmed by user.")
        
        # Update UI to show "Done" state
        if confirm_button_ref.current and dashboard_button_ref.current:
            confirm_button_ref.current.text = "تم ✓"
            confirm_button_ref.current.icon = None
            confirm_button_ref.current.bgcolor = Theme.DONE_BUTTON_COLOR
            confirm_button_ref.current.disabled = True
            dashboard_button_ref.current.disabled = True
            page.update()
        
        # Brief visual feedback pause
        time.sleep(0.7)
        
        # --- Here is where you would add your actual backend registration call ---
        # Backend registration logic would go here
        
        # Display success message
        success_snackbar = ft.SnackBar(
            content=ft.Text(
                f"تم تأكيد تسجيل الدورة '{course_name}' بنجاح.",
                text_align=ft.TextAlign.RIGHT
            ),
            bgcolor=Theme.CONFIRM_BUTTON_COLOR
        )
        page.snack_bar = success_snackbar
        page.snack_bar.open = True
        
        # Clear stored data
        clear_pending_data()
        
        # Navigate to dashboard
        page.routes = []
        page.go("/dashboard")

    def go_dashboard(e):
        print("[Confirm View] Navigating back to dashboard, cancelling final confirmation.")
        clear_pending_data()
        page.routes = []
        page.go("/dashboard")
    
    def clear_pending_data():
        page.client_storage.remove("pending_course_name")
        page.client_storage.remove("pending_course_date")
        # page.client_storage.remove("pending_file_path")  # Uncomment if needed

    # --- UI Components ---
    def create_back_button():
        return ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_OUTLINED,
            icon_color=Theme.PRIMARY_COLOR,
            tooltip="العودة للوحة التحكم",
            on_click=go_dashboard,
            icon_size=30
        )
    
    def create_header():
        title = ft.Text(
            "تأكيد تسجيل الدورة",
            size=32, 
            weight=ft.FontWeight.BOLD, 
            color=Theme.PRIMARY_COLOR,
            font_family=Theme.FONT_FAMILY_BOLD, 
            text_align=ft.TextAlign.CENTER
        )
        subtitle = ft.Text(
            "يرجى مراجعة تفاصيل الدورة قبل التأكيد النهائي",
            size=18, 
            weight=ft.FontWeight.W_500, 
            color=Theme.TEXT_COLOR_DARK,
            font_family=Theme.FONT_FAMILY_REGULAR, 
            text_align=ft.TextAlign.CENTER
        )
        return ft.Column([title, subtitle], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10)
    
    def create_course_info_display():
        course_name_display = ft.Row(
            [
                ft.Text(course_name, 
                       size=16, 
                       weight=ft.FontWeight.BOLD, 
                       color=Theme.TEXT_COLOR_DARK, 
                       font_family=Theme.FONT_FAMILY_BOLD, 
                       text_align=ft.TextAlign.RIGHT, 
                       expand=True),
                ft.Text(":اسم ملف الدورة", 
                       size=16, 
                       color=Theme.PRIMARY_COLOR, 
                       font_family=Theme.FONT_FAMILY_REGULAR, 
                       text_align=ft.TextAlign.RIGHT),
                ft.Icon(ft.icons.DESCRIPTION_OUTLINED, color=Theme.PRIMARY_COLOR),
            ], 
            alignment=ft.MainAxisAlignment.END, 
            spacing=10
        )
        
        course_date_display = ft.Row(
            [
                ft.Text(course_date, 
                       size=16, 
                       weight=ft.FontWeight.BOLD, 
                       color=Theme.TEXT_COLOR_DARK, 
                       font_family=Theme.FONT_FAMILY_BOLD, 
                       text_align=ft.TextAlign.RIGHT, 
                       expand=True),
                ft.Text(":تاريخ بداية الدورة", 
                       size=16, 
                       color=Theme.PRIMARY_COLOR, 
                       font_family=Theme.FONT_FAMILY_REGULAR, 
                       text_align=ft.TextAlign.RIGHT),
                ft.Icon(ft.icons.CALENDAR_MONTH_OUTLINED, color=Theme.PRIMARY_COLOR),
            ], 
            alignment=ft.MainAxisAlignment.END, 
            spacing=10
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    course_name_display,
                    ft.Divider(height=10, color=ft.colors.with_opacity(0.5, Theme.PRIMARY_COLOR)),
                    course_date_display,
                ], 
                spacing=15
            ),
            padding=ft.padding.symmetric(horizontal=50, vertical=20),
            border=ft.border.all(1, ft.colors.with_opacity(0.5, Theme.PRIMARY_COLOR)),
            border_radius=ft.border_radius.all(8),
            width=600,
        )
    
    def create_action_buttons():
        confirm_button = ft.ElevatedButton(
            ref=confirm_button_ref,
            text="تأكيد التسجيل",
            bgcolor=Theme.CONFIRM_BUTTON_COLOR,
            color=Theme.WHITE_COLOR,
            height=50,
            width=200,
            on_click=final_confirm_registration,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            icon=ft.icons.CHECK_CIRCLE_OUTLINE
        )

        dashboard_button = ft.ElevatedButton(
            ref=dashboard_button_ref,
            text="العودة للوحة التحكم",
            bgcolor=Theme.CANCEL_BUTTON_COLOR,
            color=Theme.WHITE_COLOR,
            height=50,
            width=200,
            on_click=go_dashboard,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            icon=ft.icons.ARROW_BACK_OUTLINED
        )
        
        return ft.Row(
            [dashboard_button, confirm_button],
            alignment=ft.MainAxisAlignment.CENTER, 
            spacing=30
        )
    
    def create_warning_note():
        return ft.Text(
            "بالضغط على 'تأكيد التسجيل'، سيتم حفظ بيانات الدورة ولا يمكن التراجع.",
            size=14, 
            color=ft.colors.RED_800, 
            font_family=Theme.FONT_FAMILY_REGULAR,
            text_align=ft.TextAlign.CENTER, 
            weight=ft.FontWeight.W_500
        )

    # --- Assemble the layout ---
    def create_content():
        return ft.Column(
            [
                ft.Container(  # Top row for back button
                    ft.Row([create_back_button()], alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.only(top=15, left=30, right=30, bottom=5)
                ),
                ft.Container(height=20),  # Spacer
                create_header(),
                ft.Container(height=40),  # Spacer
                create_course_info_display(),
                ft.Container(height=30),  # Spacer
                create_warning_note(),
                ft.Container(height=30),  # Spacer
                create_action_buttons(),
                ft.Container(height=40),  # Bottom spacer
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    # --- Create the view ---
    banner = create_banner()
    
    return ft.View(
        route="/confirm_course",
        bgcolor=Theme.BG_COLOR,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner,
                    create_content()
                ],
                expand=True,
                spacing=0
            )
        ]
    )