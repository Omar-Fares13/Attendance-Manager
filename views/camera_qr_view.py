# views/camera_qr_view.py
# Final version with correct SnackBar display, ImageFit.COVER, and corrected indentation.

import flet as ft
import os
import cv2
import base64
import threading
import time
import numpy as np
from logic.students import get_student_by_id
from logic.qr_generator import generate_qr_code
student_id = 1

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
                        ft.Text("التربية العسكرية - جامعة عين شمس", color=ft.colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                height=60,
                bgcolor="#5C544A",
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )
        def ft_asset(path):
            assets_dir = getattr(ft.app, "assets_dir", "assets") # Default to 'assets' subdir
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

# --- Helper to display student data lines ---
def create_data_row(label: str, value: str):
    return ft.Row(
        [
            ft.Text(value, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.W_500, size=14, color=ft.colors.BLACK87, selectable=True),
            ft.Text(label, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD, size=14, color="#B58B18"),
        ],
        alignment=ft.MainAxisAlignment.END, spacing=5
    )

# --- Helper to show SnackBar ---
def show_snackbar(page_ref: ft.Page, message: str, color: str = ft.colors.BLACK):
    """Helper function to display a SnackBar."""
    try:
        if page_ref is None:
            print("Error: Cannot show snackbar, page reference is None.")
            return

        snackbar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.RIGHT), # Align text right for RTL
            bgcolor=color,
            open=False # Start closed
        )
        page_ref.overlay.append(snackbar)
        page_ref.update() # Register the overlay addition
        time.sleep(0.05) # Small delay might help ensure registration before opening
        snackbar.open = True
        snackbar.update() # Open the snackbar
    except Exception as e:
        print(f"Error showing snackbar: {e}")

# --- Main View Creation Function ---
def create_camera_qr_view(page: ft.Page):
    """Creates the Flet View for the Camera/QR screen with live camera feed."""

    student['id'] = page.student_id
    student_data = get_student_by_id(student['id'])
    if not page.rtl:
        print("WARNING: page.rtl is not set to True.")

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

    # Image control for the camera feed
    camera_feed_image = ft.Image(
        fit=ft.ImageFit.COVER, # Fill the container area, cropping aspect ratio differences
        expand=True, # Crucial: Allows the image to expand within its parent
        border_radius=ft.border_radius.all(10), # Match container's inner radius slightly
        visible=False
    )

    # Stack for overlaying error message on the image area
    camera_stack = ft.Stack(
        [
            camera_feed_image, # The image itself, will expand
            ft.Container( # Container to center the error message within the stack
                content=camera_error_message,
                border_radius=12,  # Outer border radius
                alignment=ft.alignment.center,
                expand=True, # Ensure this container also tries to expand if needed,

    )
        ],
        expand=True,
        fit=ft.ImageFit.COVER # Stack should expand to fill its parent container
    )

    # Main container for the camera feed area (holds the Stack)
    camera_display_container = ft.Container(
        content=camera_stack, # Place the Stack inside the container
        #border=ft.border.all(0, "#B58B18")
        expand = True,
        border_radius=12, # Outer border radius
        clip_behavior=ft.ClipBehavior.HARD_EDGE, # Clip contents (like the image) to the rounded border
        alignment=ft.alignment.center, # Center the Stack within the container (though Stack expands)
    )

    # --- Camera Thread Function ---
    def update_camera_feed():
        nonlocal cap, latest_frame, camera_error_message, camera_feed_image
        print("Camera thread started.")
        try:
            if stop_camera_event.is_set():
                return

            cap = cv2.VideoCapture(0)
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

                stop_camera_event.wait(0.03) # Approx 33 FPS pause

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

    # --- Cleanup function ---
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

    # --- Controls Definitions ---
    def go_back(e):
        print(student['id'])
        page.go("/search_qr_student")
        
    back_button_top_left = ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18", tooltip="العودة", on_click=go_back, icon_size=30)
    page_title = ft.Text("الصورة", size=32, weight=ft.FontWeight.BOLD, color="#B58B18", text_align=ft.TextAlign.CENTER)
    student_data_column = ft.Column(
        spacing=8,
        controls=[
            ft.Row([ft.Text("بيانات الطالب", size=18, weight=ft.FontWeight.BOLD, color="#B58B18")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=1, color=ft.colors.with_opacity(0.5, "#B58B18")),
            create_data_row("الاسم:", student_data.name),
            create_data_row("ID الطالب:", student_data.id),
            create_data_row("الرقم القومي:", student_data.national_id),
            create_data_row("الكلية:", student_data.faculty.name),
            create_data_row("مسلسل:", student_data.seq_number),
            create_data_row("ملاحظات:", "واحد اثنان ثلاثة اربعة"),
        ]
    )

    # --- Button Click Handlers ---
    def show_qr_click(e):
        # 1) Generate in-memory QR
        buf = generate_qr_code(student_data.qr_code)
        data = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        img  = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            print("Failed to decode QR image")
            return

        # 2) Launch daemon thread, passing img + student name
        threading.Thread(
            target=_show_qr_window,
            args=(img, student_data.national_id),
            daemon=True
        ).start()


    def _show_qr_window(img, student_info):
        """
        Runs on a background thread:
        - Upscales the QR image
        - Adds a text area below
        - Displays student name + instruction
        - Waits for any key to close
        """
        # 1) Enlarge the image (2×)
        scale = 1
        h, w = img.shape[:2]
        img_large = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)

        # 2) Prepare the text
        text = f"{student_info} - Press any key to close"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

        # 3) Create a white padded canvas below the image
        padding = 10
        canvas_h = img_large.shape[0] + text_h + padding * 3
        canvas_w = max(img_large.shape[1] + padding * 2, text_w + padding * 2)
        canvas = np.full((canvas_h, canvas_w, 3), 255, dtype=np.uint8)

        # 4) Center the QR on the canvas
        x_offset = (canvas_w - img_large.shape[1]) // 2
        y_offset = padding
        canvas[y_offset:y_offset + img_large.shape[0],
            x_offset:x_offset + img_large.shape[1]] = img_large

        # 5) Put the text centered below
        text_x = (canvas_w - text_w) // 2
        text_y = img_large.shape[0] + padding * 2 + text_h
        cv2.putText(
            canvas,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (0, 0, 0),        # black text
            thickness,
            cv2.LINE_AA
        )

        # 6) Show in its own window until any key is pressed
        window_name = f"QR Code - {student_info}"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        while True:
            cv2.imshow(window_name, canvas)
            if cv2.waitKey(100) >= 0:
                break
        cv2.destroyWindow(window_name)

        
    def retake_photo_click(e):
        print("Retake Photo Clicked")
        if not camera_thread or not camera_thread.is_alive():
             print("Camera thread not running. Restarting...")
             camera_error_message.value = "جاري تشغيل الكاميرا..."
             camera_error_message.color = ft.colors.BLACK54
             camera_error_message.visible = True
             camera_feed_image.visible = False
             camera_error_message.update()
             camera_feed_image.update()
             stop_camera_event.clear()
             start_camera_thread()
        else:
             print("Feed is live.")
             show_snackbar(page, "الكاميرا تعرض البث المباشر بالفعل.", ft.colors.BLUE_GREY_500)

    def capture_click(e):
        nonlocal latest_frame
        print("Capture Clicked")
        current_frame = latest_frame
        if current_frame is not None and not stop_camera_event.is_set():
            try:
                save_dir = "captured_images"
                os.makedirs(save_dir, exist_ok=True)
                filename = f"{student_data.qr_code}.jpg"
                filepath = os.path.join(save_dir, filename)
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

    # --- Buttons ---
    show_qr_btn = ft.ElevatedButton("عرض QR", icon=ft.icons.QR_CODE_2, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), bgcolor="#B58B18", color=ft.colors.WHITE, height=40, on_click=show_qr_click)
    retake_photo_btn = ft.ElevatedButton("اعادة الصورة", icon=ft.icons.REFRESH, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), bgcolor="#C83737", color=ft.colors.WHITE, height=40, on_click=retake_photo_click)
    return_button_main = ft.ElevatedButton("الرجوع", icon=ft.icons.ARROW_BACK, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), bgcolor="#5C544A", color=ft.colors.WHITE, height=45, on_click=go_back)
    capture_button = ft.ElevatedButton("التقاط", icon=ft.icons.CAMERA_ALT, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), bgcolor="#6FA03C", color=ft.colors.WHITE, height=45, on_click=capture_click)

    # --- Panel Layouts ---
    left_panel = ft.Container(
        content=ft.Column(
            [
                student_data_column,
                ft.Container(expand=True), # Spacer
                ft.Row([show_qr_btn, retake_photo_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
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
            camera_display_container, # This container holds the Stack and Image
            ft.Container(height=15), # Spacer
            ft.Row([capture_button], alignment=ft.MainAxisAlignment.CENTER) # Capture Button
        ],
        expand=True, # Ensure the column itself expands vertically
        spacing=0
    )

    main_panels_layout = ft.ResponsiveRow(
        [
            ft.Container(
                content=left_panel,
                col={"xs": 12, "sm": 12, "md": 5, "lg": 4}, # Left panel column settings
                padding=ft.padding.only(bottom=10)
            ),
            ft.Container(
                content=right_panel_column, # Right panel contains the camera
                col={"xs": 12, "sm": 12, "md": 7, "lg": 8}, # Right panel column settings
                padding=ft.padding.only(bottom=10)
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30, # Horizontal space between columns
        run_spacing=20 # Vertical space when columns wrap
    )

    # --- Banner ---
    banner_control = None
    try:
        banner_control = create_banner()
    except Exception as e:
        print(f"ERROR creating banner: {e}")
        banner_control = ft.Container(height=60, bgcolor=ft.colors.RED, content=ft.Text(f"Banner Error: {e}", color=ft.colors.WHITE))
    if banner_control is None:
        print("ERROR: banner_control is None!")
        banner_control = ft.Container(height=60, bgcolor="#5C544A", content=ft.Text("Banner Placeholder", color=ft.colors.WHITE))

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            ft.Container(content=ft.Row([back_button_top_left]), padding=ft.padding.only(top=10, left=20, right=20)),
            ft.Container(content=ft.Row([page_title], alignment=ft.MainAxisAlignment.CENTER), padding=ft.padding.only(bottom=15)),
            ft.Container(
                content=main_panels_layout,
                padding=ft.padding.symmetric(horizontal=30),
                expand=True # Crucial for the row and its contents to take space
            ),
            ft.Container(content=ft.Row([return_button_main]), padding=ft.padding.only(left=30, bottom=20, top=10, right=30))
        ],
        expand=True, # Make this main column fill the vertical space
        spacing=0
    )

    # --- Start Camera Thread ---
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

    # --- View Definition ---
    view = ft.View(
        route="/camera_qr",
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column( # Root column for the view
                [banner_control, content_column], # Banner + Main content area
                expand=True, # Ensure root column fills height
                spacing=0
            )
        ]
    )
    view.on_disconnect = cleanup_camera # Assign cleanup handler correctly

    return view

# --- Example Usage (for testing this view directly) ---
if __name__ == "__main__":
    assets_folder = "assets"
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
    dummy_logo_path = os.path.join(assets_folder, "logo.png")
    if not os.path.exists(dummy_logo_path):
         try:
             from PIL import Image, ImageDraw
             img = Image.new('RGB', (100, 40), color = (240, 240, 240))
             d = ImageDraw.Draw(img)
             d.rectangle([(5,5), (95,35)], fill=(100,100,180))
             d.text((30,15), "LOGO", fill=(255,255,255))
             img.save(dummy_logo_path)
             print(f"Created dummy logo: {dummy_logo_path}")
         except ImportError:
             print("PIL not found, cannot create dummy logo.")
         except Exception as e:
             print(f"Error creating dummy logo: {e}")

    def main(page: ft.Page):
        page.title = "Camera QR View Test"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.rtl = True # Enable Right-to-Left

        def route_change(route): # route is a RouteInfo object
            current_route = page.route # page.route contains the target route string
            print(f"Route changing to: {current_route}")
            page.views.clear()
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("Test Home"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Text("Press button to go to Camera View", size=20),
                        ft.ElevatedButton("Go to Camera", on_click=lambda _: page.go("/camera_qr"))
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            if current_route == "/camera_qr":
                print("Creating and adding Camera QR View")
                page.views.append(create_camera_qr_view(page))

            print(f"Views stack size: {len(page.views)}")
            page.update()

        def view_pop(e: ft.ViewPopEvent):
            print(f"View popped: {e.view.route}") # on_disconnect should handle cleanup
            page.views.pop()
            if page.views:
                top_view = page.views[-1]
                print(f"Navigating back to: {top_view.route}")
                page.go(top_view.route)
            else:
                print("No views left.")

        page.on_route_change = route_change
        page.on_view_pop = view_pop
        print("Setting initial route to /")
        page.go("/")

    # Pass assets_dir to ft.app
    ft.app(target=main, assets_dir=assets_folder)