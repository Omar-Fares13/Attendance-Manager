# views/edit_student_view.py
import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset # Not strictly needed here, but good practice

# --- Helper Function for Form TextFields ---
def create_form_field(label: str):
    """Creates a styled TextField for the edit form."""
    return ft.TextField(
        label=label,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color="#B58B18", size=14), # Gold label
        border_color="#B58B18", # Gold border
        focused_border_color="#B58B18", # Gold focus border
        bgcolor=ft.Colors.WHITE, # White background
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45, # Consistent height
        # Expand is handled by column/row layout
    )

# --- Main View Creation Function ---
def create_edit_student_view(page: ft.Page):
    """Creates the Flet View for the Edit Student Data screen."""

    # --- Controls ---
    def go_back(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18",
        tooltip="العودة", on_click=go_back, icon_size=30
    )

    page_title = ft.Text(
        "تعديل بيانات الطالب", # Edit Student Data
        size=32, weight=ft.FontWeight.BOLD, color="#B58B18"
    )

    # --- Form Fields ---
    # Define fields (later you'll populate these with actual student data)
    name_field = create_form_field("الاسم")
    department_field = create_form_field("القسم")
    national_id_field = create_form_field("الرقم القومي")

    serial_no_field = create_form_field("رقم المسلسل")
    faculty_field = create_form_field("الكلية")
    level_field = create_form_field("الفرقة") # Academic Year/Level
    phone_field = create_form_field("رقم الهاتف")

    # --- Save Button ---
    def save_data(e):
        print("Save button clicked!")
        # Add logic here to:
        # 1. Read values from all text fields (e.g., name_field.value)
        # 2. Validate the data
        # 3. Send data to backend/database for update
        # 4. Show success/error message (e.g., SnackBar)
        # 5. Optionally navigate back (page.go("/search_student"))
        page.show_snack_bar(ft.SnackBar(ft.Text("تم حفظ التعديلات (محاكاة)"), open=True))
        go_back(None) # Simulate going back after save

    save_button = ft.ElevatedButton(
        text="حفظ",
        icon=ft.icons.SAVE_OUTLINED,
        bgcolor="#B58B18", # Gold
        color=ft.Colors.WHITE,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Form Layout using ResponsiveRow ---
    form_layout = ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.START, # Align columns to the start
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20, # Horizontal space between columns
        run_spacing=15, # Vertical space between rows within columns
        controls=[
            # Left Column (md=6 means it takes half width on medium screens and up)
            ft.Column(
                col={"xs": 12, "md": 6}, # Full width on extra small, half on medium+
                spacing=15,
                controls=[
                    name_field,
                    department_field,
                    national_id_field,
                ]
            ),
            # Right Column
            ft.Column(
                 col={"xs": 12, "md": 6},
                 spacing=15,
                 controls=[
                     # Special row for Serial No and Faculty to be side-by-side
                     ft.Row(
                         spacing=10,
                         controls=[
                             ft.Container(content=serial_no_field, width=150), # Fixed width for serial
                             ft.Container(content=faculty_field, expand=True), # Faculty takes remaining space
                         ]
                     ),
                     level_field,
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
        route="/edit_student", # Define route for this view
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column( # Main structure: Banner on top, content below
                [
                    banner_control,
                    content_column
                ],
                expand=True,
                spacing=0
            )
        ]
    )