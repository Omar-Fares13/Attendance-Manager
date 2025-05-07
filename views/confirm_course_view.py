# views/confirm_course_view.py

import flet as ft
from components.banner import create_banner # Assuming banner component is reusable
import time # Still needed for a brief pause if desired

# Define colors (reuse or adapt from your theme)
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18" # Gold/Brown
TEXT_COLOR_DARK = "#333333" # Dark text
WHITE_COLOR = ft.colors.WHITE
CONFIRM_BUTTON_COLOR = ft.colors.GREEN_700 # Green for final confirmation
CANCEL_BUTTON_COLOR = ft.colors.GREY_700 # Grey/Neutral for going back to dashboard
DONE_BUTTON_COLOR = ft.colors.GREEN_900 # Slightly darker green for 'Done' state

# Define Font Families if needed (ensure they are loaded in main.py)
FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"


def create_confirm_course_view(page: ft.Page):
    """Creates the Flet View for confirming the course details before final registration."""

    # --- Retrieve Data Stored from Previous Step ---
    course_name = page.client_storage.get("pending_course_name") or "اسم الدورة غير محدد"
    course_date = page.client_storage.get("pending_course_date") or "التاريخ غير محدد"

    print(f"[Confirm View] Loaded: Name='{course_name}', Date='{course_date}'")

    # --- UI Controls (Define Refs earlier) ---
    confirm_button_ref = ft.Ref[ft.ElevatedButton]()
    dashboard_button_ref = ft.Ref[ft.ElevatedButton]()


    # --- Event Handlers ---
    def final_confirm_registration(e):
        print("[Confirm View] Final registration confirmed by user.")

        # --- 1. Show Immediate "Done" Feedback ---
        if confirm_button_ref.current and dashboard_button_ref.current:
            confirm_button_ref.current.text = "تم ✓"
            confirm_button_ref.current.icon = None # Remove the original icon
            confirm_button_ref.current.bgcolor = DONE_BUTTON_COLOR # Optional: Subtle color change
            confirm_button_ref.current.disabled = True
            dashboard_button_ref.current.disabled = True # Disable the other button too
            page.update() # Show the change immediately

        # --- Optional: Brief Pause ---
        # Add a small delay so the user can visually register the "Done" state
        # Remove this if you want instant navigation after the backend call (or simulation)
        time.sleep(0.7) # Wait for 0.7 seconds

        # --- === ADD YOUR ACTUAL FINAL REGISTRATION LOGIC HERE === ---
        # This is where you would call your backend.
        # For now, we assume it's successful.
        # try:
        #    success = call_backend_to_register(...)
        #    if not success:
        #        # Handle failure: Show error SnackBar, re-enable buttons
        #        error_snackbar = ft.SnackBar(...)
        #        page.snack_bar = error_snackbar
        #        page.snack_bar.open = True
        #        confirm_button_ref.current.text = "تأكيد التسجيل" # Reset text
        #        confirm_button_ref.current.icon = ft.icons.CHECK_CIRCLE_OUTLINE # Reset icon
        #        confirm_button_ref.current.bgcolor = CONFIRM_BUTTON_COLOR # Reset color
        #        confirm_button_ref.current.disabled = False
        #        dashboard_button_ref.current.disabled = False
        #        page.update()
        #        return # Stop further processing
        # except Exception as ex:
        #     # Handle exception: Show error SnackBar, re-enable buttons (similar to above)
        #     print(f"Error during registration: {ex}")
        #     exception_snackbar = ft.SnackBar(...)
        #     page.snack_bar = exception_snackbar
        #     page.snack_bar.open = True
        #     # Reset buttons...
        #     page.update()
        #     return # Stop further processing
        # --- === END FINAL REGISTRATION LOGIC PLACEHOLDER === ---

        print("[Confirm View] Proceeding after confirmation feedback.")

        # --- 2. Show Success SnackBar ---
        success_snackbar = ft.SnackBar(
            content=ft.Text(f"تم تأكيد تسجيل الدورة '{course_name}' بنجاح.", text_align=ft.TextAlign.RIGHT),
            bgcolor=CONFIRM_BUTTON_COLOR # Use the original confirm color for the snackbar
        )
        page.snack_bar = success_snackbar  # Assign the snackbar to the page attribute
        page.snack_bar.open = True         # Set its open property to True
        # No need for a separate page.update() here if navigation happens immediately after


        # --- 3. Clear Stored Data ---
        page.client_storage.remove("pending_course_name")
        page.client_storage.remove("pending_course_date")
        # page.client_storage.remove("pending_file_path") # Clear path if you stored it

        # --- 4. Navigate ---
        # A slight delay might be needed for the user to see the SnackBar before navigation
        # time.sleep(0.5) # Uncomment and adjust if SnackBar disappears too quickly
        page.routes = []
        page.go("/dashboard") # Navigate to dashboard
        # IMPORTANT: Calling page.go() often implicitly includes a page update.
        # If the snackbar doesn't show reliably, add page.update() BEFORE page.go()


    def go_dashboard(e):
        print("[Confirm View] Navigating back to dashboard, cancelling final confirmation.")
        # Clear stored data if user explicitly goes back without confirming
        page.client_storage.remove("pending_course_name")
        page.client_storage.remove("pending_course_date")
        # page.client_storage.remove("pending_file_path") # Clear path if you stored it
        page.routes = []
        page.go("/dashboard")

    # --- UI Controls ---
    # Back button
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # Assuming RTL, this points back visually
        icon_color=PRIMARY_COLOR,
        tooltip="العودة للوحة التحكم",
        on_click=go_dashboard, # Use the go_dashboard handler
        icon_size=30
    )

    # Title/Subtitle
    title = ft.Text(
        "تأكيد تسجيل الدورة",
        size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR,
        font_family=FONT_FAMILY_BOLD, text_align=ft.TextAlign.CENTER
    )
    subtitle = ft.Text(
        "يرجى مراجعة تفاصيل الدورة قبل التأكيد النهائي",
        size=18, weight=ft.FontWeight.W_500, color=TEXT_COLOR_DARK,
        font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.CENTER
    )

    # Display Course Info
    course_name_display = ft.Row(
        [
            ft.Text(course_name, size=16, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_DARK, font_family=FONT_FAMILY_BOLD, text_align=ft.TextAlign.RIGHT, expand=True),
            ft.Text(":اسم ملف الدورة", size=16, color=PRIMARY_COLOR, font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.RIGHT),
            ft.Icon(ft.icons.DESCRIPTION_OUTLINED, color=PRIMARY_COLOR),
        ], alignment=ft.MainAxisAlignment.END, spacing=10
    )
    course_date_display = ft.Row(
        [
            ft.Text(course_date, size=16, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_DARK, font_family=FONT_FAMILY_BOLD, text_align=ft.TextAlign.RIGHT, expand=True),
            ft.Text(":تاريخ بداية الدورة", size=16, color=PRIMARY_COLOR, font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.RIGHT),
            ft.Icon(ft.icons.CALENDAR_MONTH_OUTLINED, color=PRIMARY_COLOR),
        ], alignment=ft.MainAxisAlignment.END, spacing=10
    )

    # Confirmation Note
    confirmation_note = ft.Text(
        "بالضغط على 'تأكيد التسجيل'، سيتم حفظ بيانات الدورة ولا يمكن التراجع.",
        size=14, color=ft.colors.RED_800, font_family=FONT_FAMILY_REGULAR,
        text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500
    )

    # Action Buttons
    _confirm_button = ft.ElevatedButton(
        ref=confirm_button_ref, # Use the Ref
        text="تأكيد التسجيل",
        bgcolor=CONFIRM_BUTTON_COLOR,
        color=WHITE_COLOR,
        height=50,
        width=200,
        on_click=final_confirm_registration,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        icon=ft.icons.CHECK_CIRCLE_OUTLINE
    )

    _dashboard_button = ft.ElevatedButton(
        ref=dashboard_button_ref, # Use the Ref
        text="العودة للوحة التحكم",
        bgcolor=CANCEL_BUTTON_COLOR,
        color=WHITE_COLOR,
        height=50,
        width=200,
        on_click=go_dashboard,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        icon=ft.icons.ARROW_BACK_OUTLINED # <-- Corrected icon name
    )

    # --- Get Banner ---
    banner_control = create_banner()

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
             ft.Container( # Top row for back button
                 ft.Row([back_button], alignment=ft.MainAxisAlignment.START), # Use the back_button defined above
                 padding=ft.padding.only(top=15, left=30, right=30, bottom=5)
             ),
             ft.Container(height=20), # Spacer
             ft.Column( # Centered Titles
                 [title, subtitle], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
             ),
             ft.Container(height=40), # Spacer

             # Display Info Section
             ft.Container(
                 content=ft.Column(
                     [
                         course_name_display,
                         ft.Divider(height=10, color=ft.colors.with_opacity(0.5, PRIMARY_COLOR)),
                         course_date_display,
                     ], spacing=15
                 ),
                 padding=ft.padding.symmetric(horizontal=50, vertical=20),
                 border=ft.border.all(1, ft.colors.with_opacity(0.5, PRIMARY_COLOR)),
                 border_radius=ft.border_radius.all(8),
                 width=600, # Limit width for better centering
             ),
             ft.Container(height=30), # Spacer

             confirmation_note,
             ft.Container(height=30), # Spacer

             # Action Buttons
             ft.Row(
                 [_dashboard_button, _confirm_button], # Use the actual button variables
                 alignment=ft.MainAxisAlignment.CENTER, spacing=30
             ),

             ft.Container(height=40), # Bottom spacer
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- View Definition ---
    return ft.View(
        route="/confirm_course",
        bgcolor=BG_COLOR,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    content_column
                ],
                expand=True,
                spacing=0
            )
        ]
    )