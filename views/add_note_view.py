# views/add_note_view.py
import flet as ft
from logic.students import get_student_by_id, save_note
import os

# Ensure create_banner is correctly imported
try:
    from components.banner import create_banner
except ImportError:
    print("Warning: components.banner not found. Using placeholder.")
    def create_banner(width): # Mock function if import fails
        return ft.Container(height=80, bgcolor="#5C5341", content=ft.Text("Mock Banner", color=ft.colors.WHITE))

# --- Constants (Copied and adjusted) ---
PAGE_BGCOLOR = "#E3DCCC"
GOLD_COLOR = "#B58B18"
RED_COLOR = "#C83737"  # Departure/Warning Red
GREY_COLOR = "#888888"
WHITE_COLOR = ft.colors.WHITE
CARD_BORDER_RADIUS = 15
BUTTON_BORDER_RADIUS = 8
PROFILE_PIC_SIZE = 150
PROFILE_IMAGE_SRC = "images/profile_placeholder.png"  # Path relative to assets dir
NOTE_BG_COLOR = ft.colors.with_opacity(0.9, WHITE_COLOR) # Slightly off-white for note area

# --- Main View Creation Function ---
def create_add_note_view(page: ft.Page):
    """Creates the 'Add Note' view for adding notes or warnings to a student."""
    
    # --- Create a Ref for the TextField ---
    note_field_ref = ft.Ref[ft.TextField]()
    
    # --- Back Button Logic ---
    def go_back(e):
        page.go("/search_student")

    # --- Save Note Action ---
    def save_note_action(e):
        note_text = note_field_ref.current.value
        if not note_text or note_text.strip() == "":
            # Fix snackbar implementation
            page.snack_bar = ft.SnackBar(
                content=ft.Text("الرجاء إدخال نص الملاحظة"),
                bgcolor=RED_COLOR
            )
            page.snack_bar.open = True
            page.update()
            return
            
        # Get the student ID from page
        student_id = getattr(page, 'student_id', None)
        if student_id:
            save_note(note_text, student_id, False)
            
            # Fix snackbar implementation
            page.snack_bar = ft.SnackBar(
                content=ft.Text("تم حفظ الملاحظة بنجاح"),
                bgcolor=GOLD_COLOR
            )
            page.snack_bar.open = True
            page.update()
            
            # Navigate after showing the snackbar
            page.go('/search_student')

    # --- Save Warning Action ---
    def save_warning_action(e):
        note_text = note_field_ref.current.value
        if not note_text or note_text.strip() == "":
            # Fix snackbar implementation
            page.snack_bar = ft.SnackBar(
                content=ft.Text("الرجاء إدخال نص الإنذار"),
                bgcolor=RED_COLOR
            )
            page.snack_bar.open = True
            page.update()
            return
            
         # Get the student ID from page
        student_id = getattr(page, 'student_id', None)
        if student_id:
            save_note(note_text, student_id, True)
            
            # Fix snackbar implementation
            page.snack_bar = ft.SnackBar(
                content=ft.Text("تم حفظ الإنذار بنجاح"),
                bgcolor=RED_COLOR
            )
            page.snack_bar.open = True
            page.update()
            
            # Navigate after showing the snackbar
            page.go('/search_student')
    
    # Get student data using the ID set on the page
    student_id = getattr(page, 'student_id', None)
    print(f"Loading note view for student ID: {student_id}")
    
    # Initialize with default values in case student data isn't available
    student_name = "غير معروف"
    student_national_id = "-"
    student_faculty = "-" 
    student_seq_number = "-"
    student_qr_code = ""
    
    # Try to fetch student data
    if student_id:
        student = get_student_by_id(student_id)
        print(f"Student loaded: {student}")
        
        if student:
            student_name = student.name
            student_national_id = student.national_id
            student_faculty = student.faculty.name if student.faculty else "-"
            student_seq_number = str(student.seq_number)
            student_qr_code = student.qr_code
    
    # Check for student profile picture
    profile_image_src = PROFILE_IMAGE_SRC
    if student_qr_code:
        # Try different possible paths for the image
        possible_paths = [
            f"pictures/{student_qr_code}.jpg",
            f"assets/pictures/{student_qr_code}.jpg",
            f"assets/images/{student_qr_code}.jpg",
            f"captured_images/{student_qr_code}.jpg"
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                profile_image_src = path
                print(f"Found profile image at: {path}")
                break
    
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED,
        icon_color=GOLD_COLOR,
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    profile_picture = ft.Image(
        src=profile_image_src,
        width=PROFILE_PIC_SIZE,
        height=PROFILE_PIC_SIZE,
        fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.all(PROFILE_PIC_SIZE / 2),
        error_content=ft.Icon(ft.icons.PERSON_OUTLINE, size=PROFILE_PIC_SIZE * 0.6, color=ft.colors.BLACK26)
    )

    banner_control = create_banner(page.width)
    
    # --- Helper function to create a data row ---
    def create_data_row(label, value):
        return ft.Row(
            [
                ft.Text(
                    value if value is not None else "-", 
                    text_align=ft.TextAlign.RIGHT, 
                    expand=True, 
                    weight=ft.FontWeight.W_500,
                    color="#000000"
                ),
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
    
    # --- Student Info Card ---
    student_info_card = ft.Container(
        padding=ft.padding.all(15),
        border=ft.border.all(2, GOLD_COLOR),
        border_radius=CARD_BORDER_RADIUS,
        bgcolor=WHITE_COLOR,
        width=400,
        content=ft.Column(
            [
                ft.Text(
                    "بيانات الطالب",
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=GOLD_COLOR
                ),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                # Display student data
                create_data_row("الاسم", student_name),
                create_data_row("الرقم القومي", student_national_id),
                create_data_row("الكلية", student_faculty),
                create_data_row("مسلسل", student_seq_number),
                ft.Container(height=10)
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )
    )
    
    # --- Note Input Area ---
    note_input_area = ft.Container(
        width=500,
        padding=ft.padding.all(20),
        border=ft.border.all(2.5, GOLD_COLOR),
        border_radius=CARD_BORDER_RADIUS,
        bgcolor=NOTE_BG_COLOR,
        content=ft.Column(
            [
                ft.Text(
                    "تسجيل ملاحظة",
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD,
                    size=30,
                    color=GOLD_COLOR
                ),
                ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                ft.TextField(
                    ref=note_field_ref,
                    hint_text="أدخل الملاحظة هنا...",
                    text_align=ft.TextAlign.RIGHT,
                    multiline=True,
                    min_lines=8,
                    max_lines=10,
                    border_color=GOLD_COLOR,
                    border_radius=CARD_BORDER_RADIUS,
                    bgcolor=NOTE_BG_COLOR,
                    border_width=1.5,
                    focused_border_color=GOLD_COLOR,
                    color="#000000"
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "تسجيل إنذار",
                            bgcolor=RED_COLOR,
                            color=WHITE_COLOR,
                            width=150, height=45,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
                            on_click=save_warning_action
                        ),
                        ft.ElevatedButton(
                            "تسجيل ملاحظة",
                            bgcolor=GOLD_COLOR,
                            color=WHITE_COLOR,
                            width=150, height=45,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
                            on_click=save_note_action
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        )
    )

    # --- Main Content Layout ---
    main_content = ft.Row(
        [
            # Left Section (Profile Pic + Data Card)
            ft.Column(
                [
                    profile_picture,
                    ft.Container(height=20),
                    student_info_card
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
                spacing=0
            ),
            # Right Section (Note Input Area)
            note_input_area
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=50,
        wrap=True
    )

    content_column = ft.Column(
        [
           ft.Container(
                content=ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(left=10, top=5)
           ),
           ft.Container(height=20),
           main_content,
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # --- View Definition ---
    return ft.View(
        route="/add_note",
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