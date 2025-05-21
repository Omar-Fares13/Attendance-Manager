import cv2
import base64
import threading
import time
import flet as ft
import numpy as np

class CameraManager:
    def __init__(self):
        self.cap = None
        self.camera_thread = None
        self.latest_frame = None
        self.stop_camera_event = threading.Event()
        self.camera_error_message = None
        self.camera_feed_image = None
        self.camera_stack = None
        self.camera_display_container = None

    def create_camera_ui(self):
        """Creates the camera UI components"""
        self.camera_error_message = ft.Text(
            "جاري تشغيل الكاميرا...",
            color=ft.colors.BLACK54, size=16,
            text_align=ft.TextAlign.CENTER, visible=True
        )

        self.camera_feed_image = ft.Image(
            fit=ft.ImageFit.COVER,
            expand=True,
            border_radius=ft.border_radius.all(10),
            visible=False
        )

        self.camera_stack = ft.Stack(
            [
                self.camera_feed_image,
                ft.Container(
                    content=self.camera_error_message,
                    border_radius=12,
                    alignment=ft.alignment.center,
                    expand=True,
                )
            ],
            expand=True,
            fit=ft.ImageFit.COVER
        )

        self.camera_display_container = ft.Container(
            content=self.camera_stack,
            expand=True,
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            alignment=ft.alignment.center,
        )

        return self.camera_display_container

    def update_camera_feed(self):
        """Updates the camera feed in a separate thread"""
        print("Camera thread started.")
        try:
            if self.stop_camera_event.is_set():
                return

            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            time.sleep(1)

            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                time.sleep(1)

            if not self.cap.isOpened():
                print("Error: Could not open camera.")
                error_msg = "خطأ: لم يتم العثور على كاميرا أو لا يمكن فتحها."
                self.camera_error_message.value = error_msg
                self.camera_error_message.color = ft.colors.RED
                self.camera_error_message.visible = True
                self.camera_feed_image.visible = False
                self.camera_error_message.update()
                self.camera_feed_image.update()
                return

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.camera_error_message.visible = False
            self.camera_feed_image.visible = True
            self.camera_error_message.update()
            self.camera_feed_image.update()

            while not self.stop_camera_event.is_set() and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("Warning: Failed to grab frame.")
                    time.sleep(0.1)
                    continue

                self.latest_frame = frame.copy()
                frame_display = cv2.flip(frame, 1)
                _, buffer = cv2.imencode('.jpg', frame_display)
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')

                self.camera_feed_image.src_base64 = jpg_as_text
                self.camera_feed_image.update()

                self.stop_camera_event.wait(0.03)

        except Exception as e:
            print(f"Error in camera thread: {e}")
            error_msg = f"خطأ في الكاميرا: {e}"
            try:
                self.camera_error_message.value = error_msg
                self.camera_error_message.color = ft.colors.RED
                self.camera_error_message.visible = True
                self.camera_feed_image.visible = False
                self.camera_error_message.update()
                self.camera_feed_image.update()
            except Exception as update_err:
                print(f"Error updating UI during exception: {update_err}")
        finally:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                print("Camera released.")
            self.cap = None
            print("Camera thread finished.")

    def start_camera(self):
        """Starts the camera thread"""
        if self.camera_thread is None or not self.camera_thread.is_alive():
            self.stop_camera_event.clear()
            self.camera_thread = threading.Thread(target=self.update_camera_feed, daemon=True)
            self.camera_thread.start()
            print("Camera thread initiated.")
        else:
            print("Camera thread already running.")

    def cleanup_camera(self):
        """Cleans up camera resources"""
        print("Cleanup initiated...")
        if not self.stop_camera_event.is_set():
            print("Signaling thread stop...")
            self.stop_camera_event.set()
        ct = self.camera_thread
        if ct is not None and ct.is_alive():
            print("Waiting for thread join...")
            ct.join(timeout=1.0)
            self.camera_thread = None
            print("Thread joined." if not ct.is_alive() else "Warning: Thread didn't join.")
        c = self.cap
        if c and c.isOpened():
            print("Releasing camera...")
            c.release()
            self.cap = None
        print("Cleanup finished.")

    def capture_image(self, save_path=None):
        """Captures the current frame and optionally saves it"""
        if self.latest_frame is not None and not self.stop_camera_event.is_set():
            try:
                if save_path:
                    success = cv2.imwrite(save_path, self.latest_frame)
                    if not success:
                        print(f"Error saving image to {save_path}")
                        return None
                return self.latest_frame.copy()
            except Exception as e:
                print(f"Error capturing image: {e}")
                return None
        return None

def create_camera_view(page: ft.Page, on_capture=None):
    """
    Creates a complete camera view with capture functionality
    
    Args:
        page: The Flet page object
        on_capture: Optional callback function that receives the captured image
    
    Returns:
        A tuple containing (camera_container, capture_button)
    """
    camera_manager = CameraManager()
    
    # Create camera UI
    camera_container = camera_manager.create_camera_ui()
    
    # Create capture button
    def capture_click(e):
        if on_capture:
            captured_image = camera_manager.capture_image()
            if captured_image is not None:
                on_capture(captured_image)
    
    capture_button = ft.ElevatedButton(
        "التقاط",
        icon=ft.icons.CAMERA_ALT,
        autofocus=True,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#6FA03C",
        color=ft.colors.WHITE,
        height=45,
        on_click=capture_click
    )
    
    # Start camera
    camera_manager.start_camera()
    
    # Set cleanup handler
    page.on_disconnect = camera_manager.cleanup_camera
    
    return camera_container, capture_button 