# views/camera_qr_view.py
# Updated version with PyQt QR window

import flet as ft
import os
import cv2
import base64
import threading
import time
import numpy as np
from logic.students import get_student_by_id, update_student
from logic.qr_generator import generate_qr_code
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# --- Asset and Banner Imports (Keep your original logic) ---
try:
    from ..components.banner import create_banner
    from ..utils.assets import ft_asset
except (ImportError, ValueError):
    print("WARN: Failed to import components/utils relative path. Trying absolute.")
    try:
        from components.banner import create_banner
        from utils.assets import ft_asset
    except ImportError:
        print("ERROR: Failed to import components/utils.")


        # Fallback placeholders if imports fail
        def create_banner():
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Image(src='assets/logo.png' if os.path.exists('assets/logo.png') else '', height=40),
                        ft.Text("التربية العسكرية - جامعة عين شمس", color=ft.colors.WHITE, size=18,
                                weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                height=60,
                bgcolor="#5C544A",
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )


        def ft_asset(path):
            assets_dir = getattr(ft.app, "assets_dir", "assets")  # Default to 'assets' subdir
            # Attempt to construct the path relative to the assets directory
            full_path = os.path.join(assets_dir, path)
            # Basic check if the file might exist using this path
            if os.path.exists(full_path):
                return full_path
            else:
                # Fallback if not found
                print(f"ft_asset Warning: Path not found at {full_path}, returning original path '{path}'")
                return path

student = {}
edit_attributes = {}


def load_by_seq(page: ft.Page, seq_str: str):
    try:
        seq = int(seq_str)
    except:
        show_snackbar(page, "رقم المسلسل غير صالح.", ft.colors.RED_700)
        return

    # assume you have or add a get_student_by_seq_number()
    from logic.students import get_student_by_seq_number
    stu = get_student_by_seq_number(seq)
    if not stu:
        show_snackbar(page, "لم يُعثر على طالب بهذا الرقم.", ft.colors.RED_700)
        return

    # Set page.student_id and force a re-build of the view
    page.student_id = stu.id
    # Remove current view and push a fresh one
    page.views.pop()
    page.views.append(create_camera_qr_view(page))
    page.update()


def update_field(name: str, value: str):
    if not value:
        edit_attributes.pop(name, None)
    else:
        edit_attributes[name] = value


def create_form_field(label: str, name: str, value: str):
    """Creates a styled TextField for the edit form."""
    return ft.TextField(
        data=name,
        value=value,
        label=label,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18", size=14),  # Gold label
        border_color="#B58B18",  # Gold border
        color="#000000",
        focused_border_color="#B58B18",  # Gold focus border
        bgcolor=ft.Colors.WHITE,  # White background
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45,
        on_change=lambda e: update_field(e.control.data, value=e.control.value)
    )


def create_data_row(label: str, value: str):
    return ft.Row(
        [
            ft.Text(value, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.W_500, size=14, color=ft.colors.BLACK87,
                    selectable=True),
            ft.Text(label, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD, size=14, color="#B58B18"),
        ],
        alignment=ft.MainAxisAlignment.END, spacing=5
    )


def show_snackbar(page_ref: ft.Page, message: str, color: str = ft.colors.BLACK):
    """Helper function to display a SnackBar."""
    try:
        if page_ref is None:
            print("Error: Cannot show snackbar, page reference is None.")
            return

        snackbar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.RIGHT),  # Align text right for RTL
            bgcolor=color,
            open=False  # Start closed
        )
        page_ref.overlay.append(snackbar)
        page_ref.update()  # Register the overlay addition
        time.sleep(0.05)  # Small delay might help ensure registration before opening
        snackbar.open = True
        snackbar.update()  # Open the snackbar
    except Exception as e:
        print(f"Error showing snackbar: {e}")


def show_qr_window(image, student_name, student_id):
    """Displays a minimized, always-on-top QR code window with student info and close button"""
    # Convert OpenCV image to QImage
    height, width, channel = image.shape
    bytes_per_line = 3 * width
    qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

    app = QApplication.instance()
    if not app:
        app = QApplication([])

    # Create main window
    window = QWidget()
    window.setWindowTitle(f"QR Code - {student_name} ({student_id})")
    window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint)

    # Create layout
    layout = QVBoxLayout()

    # Add QR code image
    label = QLabel()
    label.setPixmap(QPixmap.fromImage(qimage))
    layout.addWidget(label)

    # Add close button
    close_btn = QPushButton("إغلاق")
    close_btn.clicked.connect(window.close)
    layout.addWidget(close_btn)

    # Set layout and show window
    window.setLayout(layout)
    window.show()  # Still needed to display

    app.exec_()


def create_camera_qr_view(page: ft.Page):
    """Creates the Flet View for the Camera/QR screen with live camera feed."""

    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event


    student['id'] = page.student_id
    edit_attributes['id'] = page.student_id
    student_data = get_student_by_id(student['id'])
    if not page.rtl:
        print("WARNING: page.rtl is not set to True.")

    phone_field = ft.Container(
        content=create_form_field(
            label="رقم الهاتف",
            name="phone_number",
            value=student_data.phone_number
        ),
        width=150
    )

    location_field = create_form_field(
        label="محل السكن",
        name="location",
        value=student_data.location
    )

    def save_data(e):
        print("Save button clicked!")
        update_student(edit_attributes)
        page.open(ft.SnackBar(ft.Text("تم اضافة محل السكن ورقم الهاتف ")))
        page.update()
        print(edit_attributes)

    save_button = ft.ElevatedButton(
        text="حفظ",
        icon=ft.icons.SAVE_OUTLINED,
        bgcolor="#B58B18",  # Gold
        color=ft.Colors.WHITE,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Camera State ---
    cap = None
    camera_thread = None
    latest_frame = None
    stop_camera_event = threading.Event()

    camera_error_message = ft.Text(
        "جاري تشغيل الكاميرا...",
        color=ft.colors.BLACK54, size=16,
        text_align=ft.TextAlign.CENTER, visible=True
    )

    camera_feed_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        border_radius=ft.border_radius.all(10),
        visible=False
    )

    camera_stack = ft.Stack(
        [
            camera_feed_image,
            ft.Container(
                content=camera_error_message,
                border_radius=12,
                alignment=ft.alignment.center,
                expand=True,
            )
        ],
        expand=True,
        fit=ft.ImageFit.COVER
    )

    camera_display_container = ft.Container(
        content=camera_stack,
        expand=True,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        alignment=ft.alignment.center,
    )

    def update_camera_feed():
        nonlocal cap, latest_frame, camera_error_message, camera_feed_image
        print("Camera thread started.")
        try:
            if stop_camera_event.is_set():
                return

            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            time.sleep(1)

            if not cap.isOpened():
                cap = cv2.VideoCapture(0)
                time.sleep(1)

            if not cap.isOpened():
                print("Error: Could not open camera.")
                error_msg = "خطأ: لم يتم العثور على كاميرا أو لا يمكن فتحها."
                camera_error_message.value = error_msg
                camera_error_message.color = ft.colors.RED
                camera_error_message.visible = True
                camera_feed_image.visible = False
                camera_error_message.update()
                camera_feed_image.update()
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            camera_error_message.visible = False
            camera_feed_image.visible = True
            camera_error_message.update()
            camera_feed_image.update()

            while not stop_camera_event.is_set() and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Warning: Failed to grab frame.")
                    time.sleep(0.1)
                    continue

                latest_frame = frame.copy()
                frame_display = cv2.flip(frame, 1)
                _, buffer = cv2.imencode('.jpg', frame_display)
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')

                camera_feed_image.src_base64 = jpg_as_text
                camera_feed_image.update()

                stop_camera_event.wait(0.03)

        except Exception as e:
            print(f"Error in camera thread: {e}")
            error_msg = f"خطأ في الكاميرا: {e}"
            try:
                camera_error_message.value = error_msg
                camera_error_message.color = ft.colors.RED
                camera_error_message.visible = True
                camera_feed_image.visible = False
                camera_error_message.update()
                camera_feed_image.update()
            except Exception as update_err:
                print(f"Error updating UI during exception: {update_err}")
        finally:
            if cap and cap.isOpened():
                cap.release()
                print("Camera released.")
            cap = None
            print("Camera thread finished.")

    def cleanup_camera(*args):
        nonlocal camera_thread, cap
        print("Cleanup initiated...")
        if not stop_camera_event.is_set():
            print("Signaling thread stop...")
            stop_camera_event.set()
        ct = camera_thread
        if ct is not None and ct.is_alive():
            print("Waiting for thread join...")
            ct.join(timeout=1.0)
            camera_thread = None
            print("Thread joined." if not ct.is_alive() else "Warning: Thread didn't join.")
        c = cap
        if c and c.isOpened():
            print("Releasing camera...")
            c.release()
            cap = None
        print("Cleanup finished.")

    def go_back(e):
        print(student['id'])
        page.go("/search_qr_student")

    back_button_top_left = ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18", tooltip="العودة",
                                         on_click=go_back, icon_size=30)
    page_title = ft.Text("الصورة", size=32, weight=ft.FontWeight.BOLD, color="#B58B18", text_align=ft.TextAlign.CENTER)
    student_data_column = ft.Column(
        spacing=8,
        controls=[
            ft.Row([ft.Text("بيانات الطالب", size=18, weight=ft.FontWeight.BOLD, color="#B58B18")],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=1, color=ft.colors.with_opacity(0.5, "#B58B18")),
            create_data_row("الاسم:", student_data.name),
            create_data_row("الرقم القومي:", student_data.national_id),
            create_data_row("الكلية:", student_data.faculty.name),
            create_data_row("مسلسل:", student_data.seq_number),
        ]
    )

    def show_qr_click(e):
        buf = generate_qr_code(student_data.qr_code)
        data = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            print("Failed to decode QR image")
            return

        # Convert BGR to RGB for PyQt
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        threading.Thread(
            target=show_qr_window,
            args=(img_rgb, student_data.name, student_data.national_id),
            daemon=True
        ).start()

    def capture_click(e):
        nonlocal latest_frame
        print("Capture Clicked")
        current_frame = latest_frame
        if current_frame is not None and not stop_camera_event.is_set():
            try:
                # Use the AppData path for saving images
                from db import images_dir  # Import the images_dir from db.py
                
                filename = f"{student_data.qr_code}.jpg"
                filepath = os.path.join(images_dir, filename)
                
                if current_frame.size == 0:
                    print("Error: Captured frame empty.")
                    show_snackbar(page, "خطأ: الإطار الملتقط فارغ.", ft.colors.RED_700)
                    return
                    
                success = cv2.imwrite(filepath, current_frame)
                if success:
                    print(f"Image saved: {filepath}")
                    show_snackbar(page, f"تم حفظ الصورة بنجاح في {filepath}", ft.colors.GREEN_700)
                else:
                    print(f"Error saving image.")
                    show_snackbar(page, "حدث خطأ أثناء حفظ الصورة (فشل OpenCV).", ft.colors.RED_700)
            except cv2.error as cv_err:
                print(f"OpenCV Error: {cv_err}")
                show_snackbar(page, f"خطأ OpenCV: {cv_err}", ft.colors.RED_700)
            except Exception as ex:
                print(f"Error saving: {ex}")
                show_snackbar(page, f"خطأ: {ex}", ft.colors.RED_700)
        elif stop_camera_event.is_set():
            print("Error: Camera stopped.")
            show_snackbar(page, "لا يمكن الالتقاط، الكاميرا متوقفة.", ft.colors.AMBER_700)
        else:
            print("Error: No frame available.")
            show_snackbar(page, "لا يوجد إطار من الكاميرا للالتقاط.", ft.colors.AMBER_700)

    show_qr_btn = ft.ElevatedButton("عرض QR", icon=ft.icons.QR_CODE_2,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), bgcolor="#B58B18",
                                    color=ft.colors.WHITE, height=40, on_click=show_qr_click)
    return_button_main = ft.ElevatedButton("الرجوع", icon=ft.icons.ARROW_BACK,
                                           style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                           bgcolor="#5C544A", color=ft.colors.WHITE, height=45, on_click=go_back)
    
    capture_button = ft.ElevatedButton("التقاط", icon=ft.icons.CAMERA_ALT, autofocus=True,
                                       style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                       bgcolor="#6FA03C", color=ft.colors.WHITE, height=45, on_click=capture_click)

    seq_input = ft.TextField(
        label="رقم المسلسل",
        width=140,
        text_align=ft.TextAlign.RIGHT,
        border_color="#B58B18",
        color="#000000",
        focused_border_color="#B58B18",
        border_radius=8,
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )
    load_btn = ft.ElevatedButton(
        text="تحميل",
        icon=ft.icons.SEARCH,
        bgcolor="#B58B18",
        color=ft.colors.WHITE,
        on_click=lambda e: load_by_seq(e.page, seq_input.value),
    )

    seq_row = ft.Row([seq_input, load_btn], spacing=10, alignment=ft.MainAxisAlignment.CENTER)

    left_panel = ft.Container(
        content=ft.Column(
            [
                student_data_column,
                ft.Row([phone_field, location_field], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([show_qr_btn, save_button], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=15
        ),
        bgcolor=ft.colors.WHITE,
        border=ft.border.all(2, "#B58B18"),
        border_radius=12,
        padding=ft.padding.all(15)
    )

    right_panel_column = ft.Column(
        [
            camera_display_container,
            ft.Container(height=15),
            ft.Row([capture_button], alignment=ft.MainAxisAlignment.CENTER)
        ],
        expand=True,
        spacing=0
    )

    main_panels_layout = ft.ResponsiveRow(
        [
            ft.Container(
                content=left_panel,
                col={"xs": 12, "sm": 12, "md": 6, "lg": 5},
                padding=ft.padding.only(bottom=10)
            ),
            ft.Container(
                content=right_panel_column,
                col={"xs": 12, "sm": 12, "md": 6, "lg": 7},
                padding=ft.padding.only(bottom=10)
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30,
        run_spacing=20
    )

    banner_control = None
    try:
        banner_control = create_banner()
    except Exception as e:
        print(f"ERROR creating banner: {e}")
        banner_control = ft.Container(height=60, bgcolor=ft.colors.RED,
                                      content=ft.Text(f"Banner Error: {e}", color=ft.colors.WHITE))
    if banner_control is None:
        print("ERROR: banner_control is None!")
        banner_control = ft.Container(height=60, bgcolor="#5C544A",
                                      content=ft.Text("Banner Placeholder", color=ft.colors.WHITE))

    content_column = ft.Column(
        [
            ft.Container(content=ft.Row([back_button_top_left]), padding=ft.padding.only(top=10, left=20, right=20)),
            ft.Container(content=ft.Row([page_title], alignment=ft.MainAxisAlignment.CENTER),
                         padding=ft.padding.only(bottom=15)),
            ft.Container(content=seq_row, padding=ft.padding.symmetric(vertical=10)),
            ft.Container(
                content=main_panels_layout,
                padding=ft.padding.symmetric(horizontal=30),
                expand=True
            ),
            ft.Container(content=ft.Row([return_button_main]),
                         padding=ft.padding.only(left=30, bottom=20, top=10, right=30))
        ],
        expand=True,
        spacing=0
    )

    def start_camera_thread():
        nonlocal camera_thread
        if camera_thread is None or not camera_thread.is_alive():
            stop_camera_event.clear()
            camera_thread = threading.Thread(target=update_camera_feed, daemon=True)
            camera_thread.start()
            print("Camera thread initiated.")
        else:
            print("Camera thread already running.")

    start_camera_thread()

    view = ft.View(
        route="/camera_qr",
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(
                [banner_control, content_column],
                expand=True,
                spacing=0
            )
        ]
    )
    view.on_disconnect = cleanup_camera

    return view