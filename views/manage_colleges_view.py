import flet as ft
from components.banner import create_banner  # Assuming your banner component is here
import functools  # Import functools for partial

# Import CRUD operations
from logic.faculties import (
    create_faculty,
    get_all_faculties,
    get_faculties,
    delete_faculty,
)

# --- Constants ---
PAGE_BGCOLOR = "#E3DCCC"
INPUT_BGCOLOR = ft.colors.WHITE
INPUT_BORDER_COLOR = "#B58B18"  # Gold
BUTTON_BGCOLOR = "#B58B18"  # Gold
BUTTON_TEXT_COLOR = ft.colors.WHITE
TEXT_COLOR_GOLD = "#B58B18"  # Gold
TEXT_COLOR_DARK = "#262626"  # Slightly darker text for better contrast
TEXT_COLOR_TABLE_DATA = ft.colors.BLACK  # Explicitly black for table data cells
FONT_FAMILY_REGULAR = "Tajawal"  # Reference the font name defined in main.py
FONT_FAMILY_BOLD = "Tajawal-Bold"
BORDER_RADIUS = 8
TABLE_ROW_TEXT = TEXT_COLOR_DARK  # Ensure this contrasts well with both row colors (Used for headers)
DELETE_BUTTON_COLOR = ft.colors.RED_700
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, ft.colors.BLACK45)
SEARCH_ICON_COLOR = "#6B6B6B"  # Greyish color for search icon

class ManageCollegesState:
    def __init__(self, page: ft.Page):
        self.page = page  # Store page reference if needed for updates elsewhere
        self.search_term = ""  # State to hold the current search term

        # --- Back Button Logic ---
        def go_back(e):
            self.page.go("/dashboard")

        self.back_button = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_OUTLINED,  # RTL back arrow
            icon_color=TEXT_COLOR_GOLD,
            tooltip="العودة",
            on_click=go_back,
            icon_size=30,
        )

        # --- Input Fields ---
        self.college_name_field = ft.TextField(
            label="اسم الكلية",
            text_align=ft.TextAlign.RIGHT,
            bgcolor=INPUT_BGCOLOR,
            border_color=INPUT_BORDER_COLOR,
            border_radius=BORDER_RADIUS,
            border_width=1.5,
            height=50,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            text_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR, color=TEXT_COLOR_DARK),
            label_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR),
            expand=2,
        )

        self.search_field = ft.TextField(
            label="بحث عن كلية...",
            text_align=ft.TextAlign.RIGHT,
            bgcolor=INPUT_BGCOLOR,
            border_color=INPUT_BORDER_COLOR,
            border_radius=BORDER_RADIUS,
            border_width=1.5,
            height=50,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            text_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR, color=TEXT_COLOR_DARK),
            label_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR),
            prefix_icon=ft.icons.SEARCH,
            on_submit=self.search_colleges,
            expand=True,
        )

        # --- Data Table ---
        self.data_table = ft.DataTable(
            border=ft.border.all(1, TABLE_BORDER_COLOR),
            border_radius=ft.border_radius.all(BORDER_RADIUS),
            vertical_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
            horizontal_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
            heading_row_color=ft.colors.with_opacity(0.05, ft.colors.BLACK12),
            heading_row_height=45,
            data_row_max_height=55,
            column_spacing=20,
            columns=[
                ft.DataColumn(
                    ft.Text(
                        "اسم الكلية",
                        weight=ft.FontWeight.BOLD,
                        font_family=FONT_FAMILY_BOLD,
                        color=TABLE_ROW_TEXT,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    numeric=False,
                ),
                ft.DataColumn(
                    ft.Text(
                        "إجراءات",
                        weight=ft.FontWeight.BOLD,
                        font_family=FONT_FAMILY_BOLD,
                        color=TABLE_ROW_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    numeric=False,
                ),
            ],
            rows=self.build_data_rows(),
            expand=True,
        )

    # --- Action Handlers ---
    def save_college(self, e):
        college_name = self.college_name_field.value.strip()

        # Validation
        if not college_name:
            self.college_name_field.error_text = "اسم الكلية مطلوب"
            self.college_name_field.update()
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("يرجى تصحيح الأخطاء", font_family=FONT_FAMILY_REGULAR),
                    open=True,
                    bgcolor=ft.colors.RED_100,
                )
            )
            return

        # Create in DB
        new_faculty = create_faculty(college_name)

        # Clear input and refresh
        self.college_name_field.value = ""
        self.college_name_field.error_text = None
        self.college_name_field.update()

        self.update_table()
        self.page.show_snack_bar(
            ft.SnackBar(
                ft.Text(f"تم حفظ الكلية: {new_faculty.name}", font_family=FONT_FAMILY_REGULAR),
                open=True,
                bgcolor=ft.colors.GREEN_100,
            )
        )

    def delete_college(self, e, college_id_to_delete):
        success = delete_faculty(college_id_to_delete)
        if success:
            self.update_table()
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("تم حذف الكلية بنجاح", font_family=FONT_FAMILY_REGULAR),
                    open=True,
                    bgcolor=ft.colors.AMBER_100,
                )
            )
        else:
            self.page.show_snack_bar(
                ft.SnackBar(
                    ft.Text("خطأ: لا يمكن حذف كلية يتواجد بها طلبة", font_family=FONT_FAMILY_REGULAR),
                    open=True,
                    bgcolor=ft.colors.RED_100,
                )
            )

    def search_colleges(self, e):
        self.search_term = self.search_field.value.strip()
        self.update_table()

    # --- Helper to build/update table ---
    def build_data_rows(self):
        rows = []
        # Fetch from DB based on search term
        if self.search_term:
            faculties = get_faculties(self.search_term)
        else:
            faculties = get_all_faculties()

        for faculty in faculties:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                faculty.name,
                                font_family=FONT_FAMILY_REGULAR,
                                text_align=ft.TextAlign.RIGHT,
                                color=TEXT_COLOR_TABLE_DATA,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE,
                                        icon_color=DELETE_BUTTON_COLOR,
                                        tooltip="حذف الكلية",
                                        on_click=functools.partial(
                                            self.delete_college,
                                            college_id_to_delete=faculty.id,
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        return rows

    def update_table(self):
        self.data_table.rows = self.build_data_rows()
        self.data_table.update()

# --- View Creation Function ---
def create_manage_colleges_view(page: ft.Page):
    """Creates the Flet View for the Manage Colleges screen using DataTable."""

    view_state = ManageCollegesState(page)
    banner_control = create_banner()

    page_title = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "ادارة الكليات",
                    size=36,
                    font_family=FONT_FAMILY_BOLD,
                    color=TEXT_COLOR_GOLD,
                ),
                view_state.back_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(top=20, left=30, right=30),
    )

    save_button = ft.Container(
        content=ft.Text(
            "حفظ",
            color=BUTTON_TEXT_COLOR,
            weight=ft.FontWeight.W_600,
            size=16,
            font_family=FONT_FAMILY_BOLD,
        ),
        bgcolor=BUTTON_BGCOLOR,
        border_radius=BORDER_RADIUS,
        padding=ft.padding.symmetric(horizontal=30, vertical=13),
        alignment=ft.alignment.center,
        on_click=view_state.save_college,
        tooltip="حفظ الكلية الجديدة",
        width=120,
        height=50,
    )

    add_input_row = ft.Row(
        [
            save_button,
            view_state.college_name_field,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=15,
    )

    search_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        icon_color=BUTTON_TEXT_COLOR,
        bgcolor=BUTTON_BGCOLOR,
        tooltip="بحث",
        on_click=view_state.search_colleges,
        height=50,
        width=55,
    )

    search_row = ft.Row(
        [
            search_button,
            view_state.search_field,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=15,
    )

    input_container = ft.Container(
        content=ft.Column(
            [
                add_input_row,
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                search_row,
            ],
            spacing=5,
        ),
        padding=ft.padding.symmetric(horizontal=50, vertical=15),
        alignment=ft.alignment.top_center,
    )

    table_container = ft.Container(
        content=ft.Column(
            [view_state.data_table],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        ),
        padding=ft.padding.symmetric(horizontal=50, vertical=10),
        expand=True,
    )

    main_column = ft.Column(
        [
            page_title,
            input_container,
            ft.Divider(height=5, color=ft.colors.BLACK12),
            table_container,
        ],
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.View(
        route="/manage_colleges",
        padding=0,
        bgcolor=PAGE_BGCOLOR,
        controls=[
            ft.Column(
                [
                    banner_control,
                    main_column,
                ],
                expand=True,
                spacing=0,
            )
        ],
    )
