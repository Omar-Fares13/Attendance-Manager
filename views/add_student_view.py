# views/add_student_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset
from logic.students import create_student_from_dict
from logic.faculties import get_all_faculties
from logic.course import get_all_courses
from utils.camera_utils import CameraManager, create_camera_view
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
import uuid
import os
import cv2
from sqlalchemy.orm import sessionmaker
from db import get_session
import numpy as np
import threading
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from logic.qr_generator import generate_qr_code
from PyQt5.QtCore import Qt

# Using a class to better manage the component state
class AddStudentForm:
    def __init__(self):
        self.attributes = {}
        self.faculty_lookup = {}
        self.course_lookup = {}
        self.male_courses = []
        self.female_courses = []
        self.course_dropdown = None
        
    def update_field(self, name, value):
        """Update form field in the attributes dictionary"""
        if value is None or value == "":
            self.attributes.pop(name, None)
        else:
            self.attributes[name] = value
            
            # Special handling for gender selection
            if name == "is_male":
                self.update_course_options(value)
    
    def update_course_options(self, gender_value):
        """Update course dropdown options based on gender selection"""
        if self.course_dropdown:
            # Clear current options
            self.course_dropdown.options.clear()
            
            # Add appropriate courses based on gender
            if gender_value == "1":  # Male
                self.course_dropdown.options = [
                    ft.dropdown.Option(key=str(course_id), text=course_name)
                    for course_id, course_name in self.male_courses
                ]
            else:  # Female
                self.course_dropdown.options = [
                    ft.dropdown.Option(key=str(course_id), text=course_name)
                    for course_id, course_name in self.female_courses
                ]
                
            # Update dropdown and disable if no options
            if not self.course_dropdown.options:
                self.course_dropdown.disabled = True
                self.course_dropdown.hint_text = "لا يوجد دورات متاحة لهذا النوع"
            else:
                self.course_dropdown.disabled = False
                self.course_dropdown.hint_text = None
                self.course_dropdown.value = str(self.course_dropdown.options[0].key)
                self.update_field("course_id", self.course_dropdown.value)
            
            self.course_dropdown.update()


# --- Helper Function for Form TextFields ---
def create_form_field(label: str, name: str, form: AddStudentForm):
    """Creates a styled TextField for the edit form."""
    return ft.TextField(
        data=name,
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
        on_change=lambda e: form.update_field(e.control.data, e.control.value)
    )

    


# --- Main View Creation Function ---
def create_add_student_view(page: ft.Page):
    """Creates the Flet View for adding a new student."""
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    # Initialize form state
    form = AddStudentForm()
    
    # Load faculties for dropdown
    faculties = get_all_faculties()
    for fac in faculties:
        form.faculty_lookup[fac.id] = fac.name
    
    # Load courses and separate by gender
    courses = get_all_courses()
    for course in courses:
        course_name = f"دورة {course.start_date.strftime('%Y-%m-%d')}"
        if course.is_male_type:
            form.male_courses.append((course.id, course_name))
        else:
            form.female_courses.append((course.id, course_name))
    
    # --- Controls ---
    def go_back(e):
        page.go("/manage_students")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18",
        tooltip="العودة", on_click=go_back, icon_size=30
    )

    page_title = ft.Text(
        "ادخال بيانات الطالب",  # Add Student Data
        size=32, weight=ft.FontWeight.BOLD, color="#B58B18"
    )
    
    name_field = create_form_field("الاسم", "name", form)
    national_id_field = create_form_field("الرقم القومي", "national_id", form)
    phone_field = create_form_field("رقم الهاتف", "phone_number", form)
    address_field = create_form_field("عنوان محل الاقامة", "location", form)
    

    
    # Create success message with QR button
    def show_qr_click(student):
        buf = generate_qr_code(student.qr_code)
        data = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            print("Failed to decode QR image")
            return

        # Convert BGR to RGB for PyQt
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        threading.Thread(
            target=show_qr_window,
            args=(img_rgb, student.name, student.national_id),
            daemon=True
        ).start()

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

    # Initialize camera manager
    camera_manager = CameraManager()
    
    # Create camera UI
    camera_container = camera_manager.create_camera_ui()


    def capture_click(e):
        print("Capture Clicked")
        if camera_manager.latest_frame is not None and not camera_manager.stop_camera_event.is_set():
            try:
                # Generate a temporary QR code for the filename
                temp_qr = str(uuid.uuid4())
                form.update_field("temp_qr", temp_qr)
                
                # Use the AppData path for saving images
                from db import images_dir
                
                filename = f"{temp_qr}.jpg"
                filepath = os.path.join(images_dir, filename)
                
                if camera_manager.latest_frame.size == 0:
                    print("Error: Captured frame empty.")
                    snackbar = ft.SnackBar(
                        content=ft.Text("خطأ: الإطار الملتقط فارغ.", color=ft.colors.RED_700),
                        bgcolor=ft.colors.RED_100
                    )
                    page.overlay.append(snackbar)
                    page.update()
                    snackbar.open = True
                    snackbar.update()
                    return
                    
                success = cv2.imwrite(filepath, camera_manager.latest_frame)
                if success:
                    print(f"Image saved: {filepath}")
                    form.update_field("photo_path", filepath)
                    snackbar = ft.SnackBar(
                        content=ft.Column([
                            ft.Text("تم حفظ الصورة بنجاح", color=ft.colors.GREEN_700, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"تم حفظ الصورة في: {filepath}", color=ft.colors.GREEN_700, size=14)
                        ]),
                        bgcolor=ft.colors.GREEN_100,
                        duration=5000
                    )
                    page.overlay.append(snackbar)
                    page.update()
                    snackbar.open = True
                    snackbar.update()
                else:
                    print(f"Error saving image.")
                    snackbar = ft.SnackBar(
                        content=ft.Text("حدث خطأ أثناء حفظ الصورة (فشل OpenCV).", color=ft.colors.RED_700),
                        bgcolor=ft.colors.RED_100
                    )
                    page.overlay.append(snackbar)
                    page.update()
                    snackbar.open = True
                    snackbar.update()
            except cv2.error as cv_err:
                print(f"OpenCV Error: {cv_err}")
                snackbar = ft.SnackBar(
                    content=ft.Text(f"خطأ OpenCV: {cv_err}", color=ft.colors.RED_700),
                    bgcolor=ft.colors.RED_100
                )
                page.overlay.append(snackbar)
                page.update()
                snackbar.open = True
                snackbar.update()
            except Exception as ex:
                print(f"Error saving: {ex}")
                snackbar = ft.SnackBar(
                    content=ft.Text(f"خطأ: {ex}", color=ft.colors.RED_700),
                    bgcolor=ft.colors.RED_100
                )
                page.overlay.append(snackbar)
                page.update()
                snackbar.open = True
                snackbar.update()
        elif camera_manager.stop_camera_event.is_set():
            print("Error: Camera stopped.")
            snackbar = ft.SnackBar(
                content=ft.Text("لا يمكن الالتقاط، الكاميرا متوقفة.", color=ft.colors.AMBER_700),
                bgcolor=ft.colors.AMBER_100
            )
            page.overlay.append(snackbar)
            page.update()
            snackbar.open = True
            snackbar.update()
        else:
            print("Error: No frame available.")
            snackbar = ft.SnackBar(
                content=ft.Text("لا يوجد إطار من الكاميرا للالتقاط.", color=ft.colors.AMBER_700),
                bgcolor=ft.colors.AMBER_100
            )
            page.overlay.append(snackbar)
            page.update()
            snackbar.open = True
            snackbar.update()


    

    show_qr_btn = ft.ElevatedButton("عرض QR", icon=ft.icons.QR_CODE_2,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), bgcolor="#B58B18",
                                    color=ft.colors.WHITE, height=40, on_click=show_qr_click)

    # Create capture button
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
    
    # Faculty dropdown
    faculty_field = ft.Dropdown(
        label="الكلية",
        data="faculty_id",
        color="#000000",
        options=[
            ft.dropdown.Option(key=str(faculty_id), text=faculty_name)
            for faculty_id, faculty_name in form.faculty_lookup.items()
        ],
        on_change=lambda e: form.update_field(e.control.data, e.control.value),
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )
    
    # Gender dropdown
    gender_field = ft.Dropdown(
        label="النوع",
        data="is_male",
        color="#000000",
        options=[
            ft.dropdown.Option(key="1", text="ذكر"),
            ft.dropdown.Option(key="0", text="انثى")
        ],
        on_change=lambda e: form.update_field(e.control.data, e.control.value),
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )
    
    # Course dropdown (initially empty, will be populated based on gender)
    course_field = ft.Dropdown(
        label="الدورة",
        data="course_id",
        color="#000000",
        options=[],  # Will be populated after gender selection
        on_change=lambda e: form.update_field(e.control.data, e.control.value),
        border_color="#B58B18",
        focused_border_color="#B58B18",
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        disabled=True,  # Initially disabled until gender is selected
        hint_text="يرجى اختيار النوع أولاً"
    )
    
    # Store reference to course dropdown in form for updating
    form.course_dropdown = course_field
    
    # --- Save Button ---
    def save_data(e):
        print("Save button clicked!")
        
        # Validation
        required_fields = ["name", "faculty_id", "is_male", "course_id", "location", "photo_path"]
        missing_fields = [field for field in required_fields if field not in form.attributes]
        
        if missing_fields:
            snackbar = ft.SnackBar(
                content=ft.Text(f"يرجى إدخال جميع البيانات المطلوبة: {', '.join(missing_fields)}"),
                bgcolor=ft.colors.RED_100
            )
            page.overlay.append(snackbar)
            page.update()
            snackbar.open = True
            snackbar.update()
            return
            
        # Create student
        student = create_student_from_dict(form.attributes)
        
        if student:
            try:
                # Rename the photo file to use the student's QR code
                if "photo_path" in form.attributes:
                    old_path = form.attributes["photo_path"]
                    new_filename = f"{student.qr_code}.jpg"
                    new_path = os.path.join(os.path.dirname(old_path), new_filename)
                    
                    # Rename the file
                    os.rename(old_path, new_path)
                    
                    # Update the student's photo_path
                    with next(get_session()) as session:
                        student.photo_path = new_path
                        session.add(student)
                        session.commit()
                        
                        # Store necessary data for QR code
                        qr_data = {
                            'qr_code': student.qr_code,
                            'name': student.name,
                            'national_id': student.national_id
                        }
                        
                        def show_qr_click(e):
                            try:
                                buf = generate_qr_code(qr_data['qr_code'])
                                data = np.frombuffer(buf.getvalue(), dtype=np.uint8)
                                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                                if img is None:
                                    print("Failed to decode QR image")
                                    return

                                # Convert BGR to RGB for PyQt
                                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                threading.Thread(
                                    target=show_qr_window,
                                    args=(img_rgb, qr_data['name'], qr_data['national_id']),
                                    daemon=True
                                ).start()
                            except Exception as ex:
                                print(f"Error showing QR: {ex}")

                        # Create QR button
                        qr_button = ft.ElevatedButton(
                            "عرض QR",
                            icon=ft.icons.QR_CODE_2,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            bgcolor="#B58B18",
                            color=ft.colors.WHITE,
                            height=45,
                            on_click=show_qr_click
                        )

                        # Create success message with QR button
                        success_content = ft.Column([
                            ft.Text("تم إضافة الطالب بنجاح", size=16, weight=ft.FontWeight.BOLD),
                            qr_button
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

                        # Create and show snackbar
                        snackbar = ft.SnackBar(
                            content=success_content,
                            bgcolor=ft.colors.GREEN_100,
                            duration=10000  # Show for 10 seconds to give time to click QR button
                        )
                        page.overlay.append(snackbar)
                        page.update()
                        snackbar.open = True
                        snackbar.update()
                        print("Student added successfully")
                        
            except Exception as ex:
                print(f"Error updating photo path: {ex}")
                snackbar = ft.SnackBar(
                    content=ft.Text(f"خطأ في تحديث مسار الصورة: {ex}", color=ft.colors.RED_700),
                    bgcolor=ft.colors.RED_100
                )
                page.overlay.append(snackbar)
                page.update()
                snackbar.open = True
                snackbar.update()
        else:
            snackbar = ft.SnackBar(
                content=ft.Text("حدث خطأ أثناء إضافة الطالب", color=ft.colors.RED_700),
                bgcolor=ft.colors.RED_100
            )
            page.overlay.append(snackbar)
            page.update()
            snackbar.open = True
            snackbar.update()

    # Add back button for after QR viewing
    back_button = ft.ElevatedButton(
        text="العودة",
        icon=ft.icons.ARROW_BACK,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#5C544A",
        color=ft.colors.WHITE,
        height=45,
        on_click=go_back
    )

    save_button = ft.ElevatedButton(
        text="حفظ",
        icon=ft.icons.SAVE_OUTLINED,
        bgcolor="#B58B18",  # Gold
        color=ft.Colors.WHITE,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Form Layout using ResponsiveRow ---
    form_layout = ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.START,  # Align columns to the start
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,  # Horizontal space between columns
        run_spacing=15,  # Vertical space between rows within columns
        controls=[
            # Left Column
            ft.Column(
                col={"xs": 12, "md": 6},  # Full width on extra small, half on medium+
                spacing=15,
                controls=[
                    name_field,
                    national_id_field,
                    address_field,
                    course_field,  # Added course field
                    camera_container,  # Add camera container
                    capture_button    # Add capture button
                ]
            ),
            # Right Column
            ft.Column(
                col={"xs": 12, "md": 6},
                spacing=15,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(content=gender_field, expand=True),
                            ft.Container(content=faculty_field, expand=True),
                        ]
                    ),
                    phone_field,
                ]
            )
        ]
    )

    # Get banner
    banner_control = create_banner(page.width)

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            # Top row: Title and Back button
            ft.Container(
                padding=ft.padding.only(top=20, bottom=10, left=30, right=30),
                content=ft.Row(
                    [page_title, back_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            # Form Area
            ft.Container(
                padding=ft.padding.symmetric(horizontal=50, vertical=20),
                content=form_layout
            ),
            # Save Button Area (Centered)
            ft.Container(
                content=save_button,
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20, bottom=30)
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        # Center content horizontally within the column
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- View Definition ---
    return ft.View(
        route="/add_student",  # Define route for this view
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(  # Main structure: Banner on top, content below
                [
                    banner_control,
                    content_column
                ],
                expand=True,
                spacing=0
            )
        ]
    )


