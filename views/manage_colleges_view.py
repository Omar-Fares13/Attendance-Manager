import flet as ft
from components.banner import create_banner
import functools  # Import functools for partial
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
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
FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"
BORDER_RADIUS = 8
TABLE_ROW_TEXT = TEXT_COLOR_DARK
DELETE_BUTTON_COLOR = ft.colors.RED_700
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, ft.colors.BLACK45)
SEARCH_ICON_COLOR = "#6B6B6B"

class ManageCollegesState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.search_term = ""

        self.back_button = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_OUTLINED,
            icon_color=TEXT_COLOR_GOLD,
            tooltip="العودة",
            on_click=self.go_back,
            icon_size=30,
        )

        # Initialize these first
        self.total_males_text = ft.Text(
            "إجمالي الطلاب (ذكور): 0", font_family=FONT_FAMILY_BOLD, color=TEXT_COLOR_DARK, size=16
        )
        self.total_females_text = ft.Text(
            "إجمالي الطالبات (إناث): 0", font_family=FONT_FAMILY_BOLD, color=TEXT_COLOR_DARK, size=16
        )

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
                    ft.Text("اسم الكلية", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.RIGHT),
                    numeric=False,
                ),
                ft.DataColumn(
                    ft.Text("طلاب (ذكور)", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.CENTER),
                    numeric=True,
                ),
                ft.DataColumn(
                    ft.Text("طالبات (إناث)", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.CENTER),
                    numeric=True,
                ),
                ft.DataColumn(
                    ft.Text("إجراءات", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.CENTER),
                    numeric=False,
                ),
            ],
            rows=self.build_data_rows(),
            expand=True,
        )

    def go_back(self, e):
        self.page.go("/dashboard")

    def save_college(self, e):
        college_name = self.college_name_field.value.strip()
        if not college_name:
            self.college_name_field.error_text = "اسم الكلية مطلوب"
            self.college_name_field.update()
            # CORRECTED: Properly set the snack_bar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("يرجى تصحيح الأخطاء", font_family=FONT_FAMILY_REGULAR),
                bgcolor=ft.colors.RED_100
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        try:
            new_faculty = create_faculty(college_name) # Assumes this function adds an empty students list by default
            self.college_name_field.value = ""
            self.college_name_field.error_text = None
            self.college_name_field.update()
            self.update_table()
            # CORRECTED: Properly set the snack_bar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"تم حفظ الكلية: {new_faculty.name}", font_family=FONT_FAMILY_REGULAR),
                bgcolor=ft.colors.GREEN_100
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            # CORRECTED: Properly set the snack_bar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"خطأ في حفظ الكلية: {ex}", font_family=FONT_FAMILY_REGULAR),
                bgcolor=ft.colors.RED_100
            )
            self.page.snack_bar.open = True
            self.page.update()

    def delete_college(self, e, college_id_to_delete):
        # delete_faculty in your logic should check if faculty.students is empty
        success = delete_faculty(college_id_to_delete)
        if success:
            self.update_table()
            # CORRECTED: Properly set the snack_bar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("تم حذف الكلية بنجاح", font_family=FONT_FAMILY_REGULAR),
                bgcolor=ft.colors.AMBER_100
            )
            self.page.snack_bar.open = True
            self.page.update()
        else:
            # CORRECTED: Properly set the snack_bar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("خطأ: لا يمكن حذف كلية يتواجد بها طلبة أو حدث خطأ آخر", font_family=FONT_FAMILY_REGULAR),
                bgcolor=ft.colors.RED_100
            )
            self.page.snack_bar.open = True
            self.page.update()

    def search_colleges(self, e):
        self.search_term = self.search_field.value.strip()
        self.update_table()

    def build_data_rows(self):
        rows = []
        total_males_all_faculties = 0
        total_females_all_faculties = 0

        if self.search_term:
            faculties = get_faculties(self.search_term)
        else:
            faculties = get_all_faculties()

        for faculty in faculties:
            num_males_in_faculty = 0
            num_females_in_faculty = 0

            # Ensure faculty.students exists and is iterable
            if hasattr(faculty, 'students') and faculty.students is not None:
                for student in faculty.students:
                    # Ensure student.isMale exists
                    if hasattr(student, 'is_male'):
                        if student.is_male: # Assumes isMale is boolean True for male
                            num_males_in_faculty += 1
                        else: # Assumes isMale is boolean False for female
                            num_females_in_faculty += 1
                    else:
                        print(f"Warning: Student object in faculty '{faculty.name}' missing 'isMale' attribute.")
            else:
                print(f"Warning: Faculty '{faculty.name}' missing 'students' attribute or it is None.")

            total_males_all_faculties += num_males_in_faculty
            total_females_all_faculties += num_females_in_faculty

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(faculty.name, font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.RIGHT, color=TEXT_COLOR_TABLE_DATA)),
                        ft.DataCell(ft.Text(str(num_males_in_faculty), font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.CENTER, color=TEXT_COLOR_TABLE_DATA)),
                        ft.DataCell(ft.Text(str(num_females_in_faculty), font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.CENTER, color=TEXT_COLOR_TABLE_DATA)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE,
                                        icon_color=DELETE_BUTTON_COLOR,
                                        tooltip="حذف الكلية",
                                        on_click=functools.partial(self.delete_college, college_id_to_delete=faculty.id),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER, spacing=0,
                            )
                        ),
                    ]
                )
            )

        self.total_males_text.value = f"إجمالي الطلاب (ذكور): {total_males_all_faculties}"
        self.total_females_text.value = f"إجمالي الطالبات (إناث): {total_females_all_faculties}"

        return rows

    def update_table(self):
        self.data_table.rows = self.build_data_rows()
        self.data_table.update()
        self.total_males_text.update()
        self.total_females_text.update()

# --- View Creation Function ---
def create_manage_colleges_view(page: ft.Page):
    
    view_state = ManageCollegesState(page)
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            view_state.go_back(None)  # Fixed to use the instance method
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event

    banner_control = create_banner()

    page_title = ft.Container(
        content=ft.Row(
            [
                ft.Text("ادارة الكليات", size=36, font_family=FONT_FAMILY_BOLD, color=TEXT_COLOR_GOLD),
                view_state.back_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(top=20, left=30, right=30),
    )

    save_button = ft.Container(
        content=ft.Text("حفظ", color=BUTTON_TEXT_COLOR, weight=ft.FontWeight.W_600, size=16, font_family=FONT_FAMILY_BOLD),
        bgcolor=BUTTON_BGCOLOR, border_radius=BORDER_RADIUS,
        padding=ft.padding.symmetric(horizontal=30, vertical=13),
        alignment=ft.alignment.center, on_click=view_state.save_college,
        tooltip="حفظ الكلية الجديدة", width=120, height=50,
    )

    add_input_row = ft.Row(
        [save_button, view_state.college_name_field],
        alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, spacing=15,
    )

    search_button = ft.IconButton(
        icon=ft.icons.SEARCH, icon_color=BUTTON_TEXT_COLOR, bgcolor=BUTTON_BGCOLOR,
        tooltip="بحث", on_click=view_state.search_colleges, height=50, width=55,
    )

    search_row = ft.Row(
        [search_button, view_state.search_field],
        alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, spacing=15,
    )

    input_container = ft.Container(
        content=ft.Column([add_input_row, ft.Divider(height=10, color=ft.colors.TRANSPARENT), search_row], spacing=5),
        padding=ft.padding.symmetric(horizontal=50, vertical=15), alignment=ft.alignment.top_center,
    )

    table_container = ft.Container(
        content=ft.Column([view_state.data_table], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
        padding=ft.padding.symmetric(horizontal=50, vertical=10), expand=True,
    )

    summary_container = ft.Container(
        content=ft.Row(
            [view_state.total_males_text, view_state.total_females_text],
            alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=20,
        ),
        padding=ft.padding.symmetric(horizontal=50, vertical=15),
        alignment=ft.alignment.center,
    )

    main_column = ft.Column(
        [
            page_title,
            input_container,
            ft.Divider(height=5, color=ft.colors.BLACK12),
            table_container,
            ft.Divider(height=5, color=ft.colors.BLACK12),
            summary_container,
        ],
        expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.View(
        route="/manage_colleges",
        padding=0,
        bgcolor=PAGE_BGCOLOR,
        controls=[
            ft.Column([banner_control, main_column], expand=True, spacing=0)
        ],
    )