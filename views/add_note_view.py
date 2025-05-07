# views/add_note_view.py
import flet as ft
from logic.students import get_student_by_id, save_note
from logic.file_write import get_notes
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
student = None
note_field = None
# --- Placeholder Button Actions ---
# Re-use show_warning if the action is the same (needs confirmation)


# --- Main View Creation Function ---
def create_add_note_view(page: ft.Page):
    """Creates the 'Add Note' view."""


    # --- Helper: Student Info Card (Display Only) ---
    def _build_student_info_card_display(page: ft.Page):
        """Builds the left-side student data card without action buttons."""

        def create_data_row(label, value):
            return ft.Row(
                [
                    ft.Text(value if value is not None else "-", text_align=ft.TextAlign.RIGHT, expand=True, weight=ft.FontWeight.W_500),
                    ft.Text(f":{label}", text_align=ft.TextAlign.RIGHT, color=GOLD_COLOR, weight=ft.FontWeight.BOLD, width=100, no_wrap=True),
                ],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

        # Same as _build_student_data_card but WITHOUT the final button Row
        return ft.Container(
            padding=ft.padding.all(15),
            border=ft.border.all(2, GOLD_COLOR),
            border_radius=CARD_BORDER_RADIUS,
            bgcolor=WHITE_COLOR,
            width=400,
            # Let height adjust based on content
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
                    # --- Replace with actual dynamic data ---
                    # TODO: Pass student data to this function
                    create_data_row("الاسم", student.name),
                    create_data_row("الرقم القومي", student.national_id),
                    create_data_row("الكلية", student.faculty.name),
                    create_data_row("مسلسل", student.seq_number),
                    create_data_row("ملاحظات", get_notes(student)), # Existing notes display
                    # --- End Dynamic Data Section ---
                    # NO BUTTON ROW HERE
                    ft.Container(height=10) # Add a little space at the bottom
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            )
        )

    # --- Helper: Note Input Area ---
    def _build_note_input_area(page: ft.Page, note_textfield_ref: ft.Ref[ft.TextField]):
        """Builds the right-side note input area."""

        title = ft.Text(
            "تسجيل ملاحظة",
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.BOLD,
            size=30, # Slightly smaller than main titles maybe
            color=GOLD_COLOR
        )
        global note_field
        note_field = ft.TextField(
            ref=note_textfield_ref, # Assign the reference
            hint_text="بسم الله الرحمن الرحيم هذا مجرد نموذج لملاحظة لعرض كيف سيكون المظهر العام...",
            text_align=ft.TextAlign.RIGHT,
            multiline=True,
            min_lines=8,
            max_lines=10, # Adjust height as needed
            border_color=GOLD_COLOR,
            border_radius=CARD_BORDER_RADIUS,
            bgcolor=NOTE_BG_COLOR,
            border_width=1.5,
            focused_border_color=GOLD_COLOR, # Keep border color on focus
            # content_padding=ft.padding.all(15)
        )

        save_button = ft.ElevatedButton(
            "تسجيل",
            bgcolor=GOLD_COLOR,
            color=WHITE_COLOR,
            width=150, height=45,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
            on_click=save_note_action
        )

        warning_button = ft.ElevatedButton(
            "انذار",
            bgcolor=RED_COLOR,
            color=WHITE_COLOR,
            width=150, height=45,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_BORDER_RADIUS)),
            on_click=show_warning_note_page
        )

        # Arrange elements within a Column, inside a styled Container
        return ft.Container(
            width=500, # Adjust width as needed
            padding=ft.padding.all(20),
            border=ft.border.all(2.5, GOLD_COLOR), # Match image border thickness
            border_radius=CARD_BORDER_RADIUS,
            bgcolor=NOTE_BG_COLOR, # Background for the whole card
            content=ft.Column(
                [
                    title,
                    ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                    note_field,
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    ft.Row(
                        [warning_button, save_button], # Order: انذار (left), تسجيل (right)
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0 # Control spacing with Dividers
            )

        )

    def show_warning_note_page(e: ft.ControlEvent):
        note = note_field.value
        save_note(note,student.id, True)
        page.go('/search_student')

    def save_note_action(e: ft.ControlEvent):
        note = note_field.value
        save_note(note, student.id, False)
        page.go('/search_student')

    global PROFILE_IMAGE_SRC
    global student
    # --- Create a Ref for the TextField ---
    note_textfield_ref = ft.Ref[ft.TextField]()
    student = get_student_by_id(page.student_id)
    pic_path = f"pictures/{student.qr_code}.jpg"
    if os.path.isfile(pic_path):
        PROFILE_IMAGE_SRC = pic_path
    # --- Back Button Logic ---
    def go_back(e):
        # This is tricky - where should it go back to?
        # Option 1: Generic back (might lose context if deep navigation)
        # if page.views and len(page.views) > 1:
        #    page.views.pop()
        #    top_view = page.views[-1]
        #    page.go(top_view.route)
        # Option 2: Assume it came from attendance selection
        # page.go("/attendance")
        # Option 3: Assume it came from mark attendance/departure (more likely)
        # We don't know which one without passing data. Let's default to /attendance
        # TODO: Implement passing 'previous_route' for accurate back navigation
        print("Back button clicked on Add Note page, navigating to /attendance (default)")
        page.go("/search_student") # Default back target

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED,
        icon_color=GOLD_COLOR,
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    profile_picture = ft.Image(
        src=PROFILE_IMAGE_SRC,
        width=PROFILE_PIC_SIZE,
        height=PROFILE_PIC_SIZE,
        fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.all(PROFILE_PIC_SIZE / 2),
        error_content=ft.Icon(ft.icons.PERSON_OUTLINE, size=PROFILE_PIC_SIZE * 0.6, color=ft.colors.BLACK26)
    )

    banner_control = create_banner(page.width)

    # --- Main Content Layout ---
    main_content = ft.Row(
        [
            # --- Left Section (Profile Pic + Data Card Display) ---
            ft.Column(
                [
                    profile_picture,
                    ft.Container(height=20),
                    # Use the display-only student card helper
                    _build_student_info_card_display(page) # Pass student data here later
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
                spacing=0
            ),
            # --- Right Section (Note Input Area) ---
            # Pass the ref to the helper
            _build_note_input_area(page, note_textfield_ref)
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=50,
        wrap=False
    )

    content_column = ft.Column(
        [
           ft.Container(
                content=ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(left=10, top=5) # Adjust padding
           ),
           ft.Container(height=20), # Spacer below back button row
           main_content, # The row with student card and note area
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        # alignment=ft.MainAxisAlignment.START # Align content towards top
    )

    # --- View Definition ---
    view = ft.View(
        route="/add_note", # Define route for this view
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
    # Store the ref in the view's data for easier access in the save action (alternative way)
    # view.data = {"note_field_ref": note_textfield_ref}
    return view