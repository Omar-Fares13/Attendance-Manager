"""
Mark Attendance & Departure View
--------------------------------
Handles UI and logic for recording student attendance and departures.
"""

import os
import threading
from datetime import date, datetime

import flet as ft

from logic.qr_scanner import scan_qr_code_continuous
from views.qr_display_view import get_validation_key
from logic.students import Student, get_student_by_qr_code
from utils.input_controler import InputSequenceMonitor
from utils.data_processor import load_system_resource,retrieve_processed_data
from logic.attendance import (
    get_attendance_by_student_id,
    update_attendance,
    Attendance,
    create_attendance
)

# --- Try to import banner component ---
try:
    from components.banner import create_banner
except ImportError:
    print("Warning: components.banner not found. Using placeholder.")
    def create_banner(width):
        return ft.Container(height=80, bgcolor="#5C5341", content=ft.Text("Mock Banner", color=ft.colors.WHITE))

# --- Constants ---
PAGE_BGCOLOR = "#E3DCCC"
GOLD_COLOR = "#B58B18"
GREEN_COLOR = "#6FA03C"  # Attendance Green
RED_COLOR = "#C83737"    # Departure Red
WHITE_COLOR = ft.colors.WHITE
CARD_BORDER_RADIUS = 15
BUTTON_BORDER_RADIUS = 8
PROFILE_PIC_SIZE = 150

PLACEHOLDER_IMAGE_SRC = "images/placeholder_canva.png"
PROFILE_IMAGE_SRC = "images/profile_placeholder.png"

# --- Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "captured_images"))

# --- Attendance Logic ---
def on_scan_trigger(student: Student):
    """
    Records student arrival or departure once per day.
    """
    today = date.today()
    now = datetime.now().time()
    
    # Fetch today's attendance records
    records = get_attendance_by_student_id(student.id)
    today_records = [r for r in records if r.date == today]
    
    if not today_records:
        # No check-in today: record arrival
        record = Attendance(student_id=student.id, date=today, arrival_time=now, leave_time=None)
        create_attendance(record)
        print(f"Arrival recorded for student {student.id} at {now}")
    else:
        rec = today_records[0]
        if rec.leave_time is None:
            # Record departure time
            update_attendance(rec.id, {"leave_time": now})
            print(f"Departure recorded for student {student.id} at {now}")
        else:
            # Already recorded departure
            print(f"Attendance already completed for student {student.id} today")

# --- UI Building Components ---
def build_student_data_card(page: ft.Page):
    """Creates and returns the student data display card with empty fields"""
    page.student_controls = {}
    
    def create_data_row(label, key):
        txt = ft.Text("-", text_align=ft.TextAlign.RIGHT, expand=True, weight=ft.FontWeight.W_500)
        page.student_controls[key] = txt
        return ft.Row(
            [
                txt,
                ft.Text(
                    f":{label}", 
                    text_align=ft.TextAlign.RIGHT, 
                    color=GOLD_COLOR, 
                    weight=ft.FontWeight.BOLD, 
                    width=100, 
                    no_wrap=True
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    return ft.Container(
        padding=ft.padding.all(15),
        border=ft.border.all(2, GOLD_COLOR),
        border_radius=CARD_BORDER_RADIUS,
        bgcolor=WHITE_COLOR,
        width=400,
        content=ft.Column(
            [
                ft.Text("بيانات الطالب", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, size=20, color=GOLD_COLOR),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                create_data_row("الاسم",        "name"),
                create_data_row("ID الطالب",   "id"),
                create_data_row("الرقم القومي", "national_id"),
                create_data_row("الكلية",      "faculty"),
                create_data_row("مسلسل",       "seq_number"),
                create_data_row("ملاحظات",     "notes"),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )
    )

def attempt_system_verification(page):
    try:

        keys = get_validation_key()
        if not keys:
            return False
        
        encrypted_data = load_system_resource()
        if not encrypted_data:
            return False
        
        for key in keys:
            decrypted_data = retrieve_processed_data(encrypted_data, key)
            if decrypted_data:
                show_system_message(page, decrypted_data)
                print("decrypted data is : ",decrypted_data)
                return True
        return False
    except Exception:
        return False

def build_image_placeholder(page: ft.Page, border_color: str):
    """Creates and returns the image display container"""
    # Create image control and store reference
    img = ft.Image(
        src=PLACEHOLDER_IMAGE_SRC,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(CARD_BORDER_RADIUS - 5),
        error_content=ft.Column([
            ft.Icon(ft.icons.CAMERA_ALT_OUTLINED, size=50, color=ft.colors.BLACK26),
            ft.Text("لا يمكن تحميل الصورة", color=ft.colors.BLACK26)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, opacity=0.8)
    )
    page.student_image = img
    
    return ft.Container(
        width=350,
        height=350,
        border=ft.border.all(4, border_color),
        border_radius=CARD_BORDER_RADIUS,
        bgcolor=WHITE_COLOR,
        padding=10,
        alignment=ft.alignment.center,
        content=img
    )

# --- QR Scanning Logic ---
def start_scanning(page: ft.Page, scan_btn: ft.ElevatedButton):
    """Starts the QR code scanning process in a separate thread"""
    scan_btn.disabled = True
    page.update()

    def on_detect(qr_code_value):
        """Callback when a QR code is detected"""
        student = get_student_by_qr_code(qr_code_value)
        
        if not student:
            # Create and show snackbar for student not found
            snackbar = ft.SnackBar(
                content=ft.Text("لم يتم العثور على الطالب!"),
                bgcolor=ft.colors.RED_700
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
            return

        # Populate student data fields
        sc = page.student_controls
        sc["name"].value        = student.name
        sc["id"].value          = str(student.id)
        sc["national_id"].value = student.national_id
        sc["faculty"].value     = student.faculty.name
        sc["seq_number"].value  = str(student.seq_number)
        sc["notes"].value       = student.notes or "-"

        # Update student image
        page.student_image.src = f"{IMAGE_FOLDER_PATH}/{qr_code_value}.jpg"

        # Record attendance
        on_scan_trigger(student)

        # Show success message
        snackbar = ft.SnackBar(
            content=ft.Text("تم تسجيل الحضور بنجاح!"),
            bgcolor=ft.colors.GREEN_700
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        
        page.update()

    # Start scanning in separate thread
    threading.Thread(
        target=scan_qr_code_continuous, 
        args=(on_detect,), 
        daemon=True
    ).start()

def show_system_message(page, message):
    """Display system message as a prominent snackbar."""
    print("Showing snackbar with message:", message)
    
    # Create a styled snackbar
    snackbar = ft.SnackBar(
        content=ft.Text(
            message,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE
        ),
        bgcolor="#B58B18",  # Gold color to match your app
        action="إغلاق",  # Close button
        action_color=ft.colors.WHITE,
        duration=8000,  # Show for 8 seconds
    )
    
    # Clear any existing snackbars/overlays
    page.overlay.clear()
    # Add and show the new snackbar
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()
    print("Snackbar opened")
    
    # As an alternative, let's also try showing an overlay with our message
    try:
        # Create an overlay container with the message
        message_overlay = ft.Container(
            content=ft.Column([
                ft.Container(height=20),
                ft.Text(
                    message,
                    size=20,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                ft.ElevatedButton(
                    "إغلاق",
                    on_click=lambda e: close_overlay(e, page, message_overlay),
                    bgcolor=ft.colors.WHITE,
                    color="#B58B18",
                    width=120,
                    height=40
                )
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=page.width * 0.8,
            bgcolor=ft.colors.with_opacity(0.9, "#B58B18"),
            border_radius=10,
            padding=30,
            alignment=ft.alignment.center,
        )
        
        def close_overlay(e, page, overlay):
            page.overlay.remove(overlay)
            page.update()
        
        # Add the overlay to the page
        page.overlay.append(message_overlay)
        page.update()
        print("Overlay added")
    except Exception as e:
        print(f"Error showing overlay: {e}")
    
    return True

# --- View Creation ---
def create_mark_view(page: ft.Page, title_text: str, title_color: str, border_color: str, route: str):
    """Creates a reusable view for marking attendance or departure"""
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    # Create navigation button
    def go_back(e: ft.ControlEvent):
        page.go("/attendance")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, 
        icon_color=GOLD_COLOR,
        tooltip="العودة", 
        on_click=go_back, 
        icon_size=30
    )

    # Create UI elements
    page_title = ft.Text(
        title_text, 
        size=36, 
        weight=ft.FontWeight.BOLD,
        color=title_color, 
        text_align=ft.TextAlign.CENTER
    )

    profile_picture = ft.Image(
        src=PROFILE_IMAGE_SRC, 
        width=PROFILE_PIC_SIZE,
        height=PROFILE_PIC_SIZE, 
        fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.all(PROFILE_PIC_SIZE/2),
        error_content=ft.Icon(
            ft.icons.PERSON_OUTLINE,
            size=PROFILE_PIC_SIZE*0.6,
            color=ft.colors.BLACK26
        )
    )

    banner_control = create_banner(page.width)
    
    scan_btn = ft.ElevatedButton(
        "ابدأ مسح QR", 
        bgcolor=GOLD_COLOR, 
        color=WHITE_COLOR,
        width=200, 
        on_click=lambda e: start_scanning(e.page, scan_btn)
    )

    # Arrange the main content
    main_content = ft.Row(
        [
            ft.Column(
                [
                    profile_picture, 
                    ft.Container(height=20), 
                    build_student_data_card(page)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START
            ),
            ft.Column(
                [
                    build_image_placeholder(page, border_color), 
                    ft.Container(height=15), 
                    scan_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ], 
        vertical_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.CENTER, 
        spacing=50
    )

    # Combine into a page layout
    content_column = ft.Column(
        [
            ft.Container(content=ft.Row([back_button]), padding=ft.padding.only(left=10)),
            ft.Container(height=5), 
            page_title, 
            ft.Container(height=20), 
            main_content
        ], 
        expand=True, 
        scroll=ft.ScrollMode.ADAPTIVE, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Return the complete view
    return ft.View(
        route=route, 
        padding=0, 
        bgcolor=PAGE_BGCOLOR,
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(
                        content=content_column,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        expand=True,
                        alignment=ft.alignment.top_center
                    )
                ],
                expand=True,
                spacing=0
            )
        ]
    )

# --- Specific View Creation Functions ---
def create_attendance_mark_view(page: ft.Page):
    """Creates the attendance marking view"""
    return create_mark_view(page, "حضــور", GREEN_COLOR, GREEN_COLOR, "/mark_attendance")

def create_departure_mark_view(page: ft.Page):
    """Creates the departure marking view"""
    return create_mark_view(page, "انصـراف", RED_COLOR, RED_COLOR, "/mark_departure")

# --- Entry Point for Testing ---
if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, '..', 'assets'))

    def main(page: ft.Page):
        """Main application entry point"""
        # Configure page settings
        page.title = "Mark Attendance/Departure Test"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 850
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.fonts = {"Cairo": "https://github.com/google/fonts/raw/main/apache/cairo/Cairo%5Bslnt%2Cwght%5D.ttf"}
        page.theme = ft.Theme(font_family="Cairo")
        page.rtl = True
        page.overlay = []  # Initialize overlay list for snackbars

        # Handle route changes
        def route_change(route: ft.RouteChangeEvent):
            page.views.clear()
            
            if route.route == "/mark_attendance":
                page.views.append(create_attendance_mark_view(page))
            elif route.route == "/mark_departure":
                page.views.append(create_departure_mark_view(page))
            elif route.route == "/attendance":
                page.views.append(ft.View(
                    "/attendance", 
                    [
                        ft.AppBar(title=ft.Text("Attendance Selection (Mock)")),
                        ft.ElevatedButton("Mark Attendance", on_click=lambda _: page.go("/mark_attendance")),
                        ft.ElevatedButton("Mark Departure", on_click=lambda _: page.go("/mark_departure"))
                    ], 
                    bgcolor=PAGE_BGCOLOR, 
                    rtl=True
                ))
            elif route.route == "/add_note":
                page.views.append(ft.View(
                    "/add_note", 
                    [
                        ft.AppBar(title=ft.Text("Add Note Page (Mock)")),
                        ft.ElevatedButton("Go Back (Simulated)", on_click=lambda _: page.go("/attendance"))
                    ], 
                    bgcolor=PAGE_BGCOLOR, 
                    rtl=True
                ))
            else:
                page.views.append(ft.View(
                    "/", 
                    [
                        ft.AppBar(title=ft.Text("Test Home")),
                        ft.ElevatedButton("Go to Attendance Mark", on_click=lambda _: page.go("/mark_attendance")),
                        ft.ElevatedButton("Go to Departure Mark", on_click=lambda _: page.go("/mark_departure"))
                    ], 
                    bgcolor=PAGE_BGCOLOR, 
                    rtl=True
                ))
                
            page.update()

        page.on_route_change = route_change
        page.go("/")

    ft.app(target=main, assets_dir=assets_dir)