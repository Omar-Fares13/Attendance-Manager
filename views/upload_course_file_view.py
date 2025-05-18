import flet as ft
from datetime import datetime
import math
from collections import defaultdict
from components.banner import create_banner
from logic.file_reader import read_pdf
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# Colors and style constants
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18"
TEXT_COLOR_DARK = "#333333"
WHITE_COLOR = ft.colors.WHITE
HEADER_TEXT_COLOR = ft.colors.WHITE
CELL_TEXT_COLOR = "#404040"
PLACEHOLDER_DARK_HEADER = "#6D6D6D"
CONFIRM_BUTTON_COLOR = ft.colors.LIME_700
CANCEL_BUTTON_COLOR = ft.colors.RED_600
DIALOG_BG_COLOR = ft.colors.WHITE
STATS_CARD_COLOR = "#F5F5F5"

file_students = {}


def create_table_cell(text_content):
    return ft.DataCell(ft.Text(str(text_content), color=CELL_TEXT_COLOR, text_align=ft.TextAlign.RIGHT, size=13))


def create_stats_card(title, value, icon):
    return ft.Container(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(title, size=14, color=TEXT_COLOR_DARK, weight=ft.FontWeight.W_500),
                        ft.Icon(icon, color=PRIMARY_COLOR, size=18),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        ),
        padding=ft.padding.all(15),
        border_radius=8,
        bgcolor=STATS_CARD_COLOR,
        border=ft.border.all(1, ft.colors.with_opacity(0.2, TEXT_COLOR_DARK)),
        expand=True,
    )


def create_faculty_row(faculty, count):
    return ft.Row(
        [
            ft.Text(faculty, size=14, color=TEXT_COLOR_DARK, expand=True, text_align=ft.TextAlign.RIGHT),
            ft.Container(
                ft.Text(str(count), size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                width=60,
                alignment=ft.alignment.center_left
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=10
    )


def create_upload_course_file_view(page: ft.Page):
    
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event
    
    def inputs_are_complete() -> bool:
        """
        Return True only when BOTH a file path and a date were selected.
        """
        return (
            bool(selected_file_full_path.current)           # at least one pdf
            and bool(file_students.get("date"))              # a date was picked
        )

    def show_error(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg), open=True, bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

    def update_next_button_state():
        next_step_button.disabled = not inputs_are_complete()
        page.update()
    # ------------------------------------------------------------------
    # Pagination state & helpers
    # ------------------------------------------------------------------
    ROWS_PER_PAGE = 25               # tweak as you like
    current_page  = 0
    total_pages   = 1                # will be updated after rows are loaded
    all_rows      = []               # full list of DataRow objects

    def slice_rows(idx: int):
        start = idx * ROWS_PER_PAGE
        end   = start + ROWS_PER_PAGE
        return all_rows[start:end]

    def refresh_table():
        nonlocal current_page
        if not all_rows:
            data_table_ref.current.rows = []
            nav_bar.visible = False
        else:
            current_page = max(0, min(current_page, total_pages - 1))
            data_table_ref.current.rows = slice_rows(current_page)
            page_label.value = f"{current_page+1} / {total_pages}"
            nav_bar.visible = True
        page.update()

    def next_page(e):
        nonlocal current_page
        if current_page < total_pages - 1:
            current_page += 1
            refresh_table()

    def prev_page(e):
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            refresh_table()
    # ------------------------------------------------------------------

    # ---------- (all your refs and constants stay unchanged) ----------
    file_path_field_ref = ft.Ref[ft.TextField]()
    date_field_ref      = ft.Ref[ft.TextField]()
    file_picker_ref     = ft.Ref[ft.FilePicker]()
    date_picker_ref     = ft.Ref[ft.DatePicker]()
    confirmation_dialog_ref = ft.Ref[ft.AlertDialog]()
    selected_file_full_path = ft.Ref[str]()
    data_table_ref      = ft.Ref[ft.DataTable]()
    stats_container_ref = ft.Ref[ft.Container]()
    faculty_stats_ref   = ft.Ref[ft.Column]()
    progress_ring_ref = ft.Ref[ft.ProgressRing]()
    progress_container_ref = ft.Ref[ft.Container]()

    file_students['is_male'] = page.is_male
    ismale = file_students['is_male']

    # --- Table Columns ---
    columns = [
        ft.DataColumn(ft.Text("الرقم المسلسل", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD,
                              text_align=ft.TextAlign.CENTER), numeric=True),
        ft.DataColumn(
            ft.Text("الاسم", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
        ft.DataColumn(
            ft.Text("الرقم القومي", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
        ft.DataColumn(
            ft.Text("الكليه", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
    ]

    # Initially, table is empty
    rows = []
    data_table = ft.DataTable(
        ref=data_table_ref,
        columns=columns,
        rows=[],        # starts empty – will be filled by refresh_table()
        column_spacing=25,
        heading_row_color=PLACEHOLDER_DARK_HEADER,
        heading_row_height=45,
        data_row_color={"hovered": ft.colors.with_opacity(0.1, PRIMARY_COLOR)},
        data_row_min_height=40,
        border=ft.border.all(1, ft.colors.with_opacity(0.3, ft.colors.BLACK)),
        border_radius=ft.border_radius.all(8),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.15, ft.colors.BLACK)),
        expand=False,
    )

    # ------------------------------------------------------------------
    # Pagination navigation bar
    # ------------------------------------------------------------------
    page_label = ft.Text("1 / 1", weight=ft.FontWeight.BOLD, size=16)
    nav_bar = ft.Row(
        [
            ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="السابق", on_click=prev_page),
            page_label,
            ft.IconButton(icon=ft.icons.CHEVRON_LEFT, tooltip="التالي", on_click=next_page),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False   # hidden until rows exist
    )
    # ------------------------------------------------------------------

    # Faculty stats column
    faculty_stats = ft.Column(
        ref=faculty_stats_ref,
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
    )

    # --- Stats Container ---
    stats_container = ft.Container(
        ref=stats_container_ref,
        content=ft.Column(
            [
                ft.Text("إحصائيات الملفات", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                ft.Row(
                    [
                        create_stats_card("عدد الملفات المرفوعة", "0", ft.icons.INSERT_DRIVE_FILE),
                        create_stats_card("إجمالي الطلاب", "0", ft.icons.PEOPLE_ALT),
                        create_stats_card("عدد الكليات", "0", ft.icons.SCHOOL),
                    ],
                    spacing=15,
                    width=700
                ),
                ft.Container(height=10),
                ft.Container(
                    ft.Column(
                        [
                            ft.Text("توزيع الطلاب حسب الكلية:", size=16, weight=ft.FontWeight.BOLD,
                                    color=PRIMARY_COLOR),
                            ft.Container(
                                faculty_stats,
                                padding=ft.padding.symmetric(vertical=10, horizontal=15),
                                bgcolor=STATS_CARD_COLOR,
                                border_radius=8,
                                width=700
                            ),
                        ],
                        spacing=8
                    ),
                    visible=False
                )
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        visible=False,
        padding=ft.padding.only(bottom=15)
    )

    def update_stats():
        students = file_students.get('students', [])
        if not students:
            stats_container_ref.current.visible = False
            return

        # Count faculties and students per faculty
        faculty_counts = defaultdict(int)
        for student in students:
            faculty_counts[student['faculty']] += 1

        # Update stats cards
        stats_content = stats_container_ref.current.content
        stats_content.controls[1].controls[0].content.controls[1].value = str(
            len(selected_file_full_path.current) if isinstance(selected_file_full_path.current, list) else 1)
        stats_content.controls[1].controls[1].content.controls[1].value = str(len(students))
        stats_content.controls[1].controls[2].content.controls[1].value = str(len(faculty_counts))

        # Update faculty breakdown
        faculty_stats_ref.current.controls = []
        if faculty_counts:
            stats_content.controls[3].visible = True
            # Sort faculties by student count (descending)
            sorted_faculties = sorted(faculty_counts.items(), key=lambda x: x[1], reverse=True)
            for faculty, count in sorted_faculties:
                faculty_stats_ref.current.controls.append(create_faculty_row(faculty, count))
        else:
            stats_content.controls[3].visible = False

        stats_container_ref.current.visible = True
        page.update()

    # --- Handlers ---
    def handle_confirm_upload(e):
        # Close dialog if it is open
        if confirmation_dialog_ref.current:
            confirmation_dialog_ref.current.open = False

        # VALIDATE
        if not inputs_are_complete():
            show_error("يجب اختيار الملف وتاريخ الدورة قبل المتابعة.")
            return

        # Everything is OK – continue
        page.file_students = file_students
        page.go("/edit_course_data")

    def handle_cancel_upload(e):
        if confirmation_dialog_ref.current:
            confirmation_dialog_ref.current.open = False
            page.update()

    def go_back(e):
        selected_file_full_path.current = None
        page.is_male = file_students['is_male']
        page.go("/register_course_options")

     # --------------------  on_file_picked()  --------------------------
    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal total_pages, all_rows, current_page
        if not e.files:
            return
        
        # Show loading indicator
        progress_container_ref.current.visible = True
        page.update()
        
        try:
            all_students = []
            selected_file_full_path.current = []
            for file in e.files:
                selected_file_full_path.current.append(file.path)
                if file_path_field_ref.current:
                    file_path_field_ref.current.value = file.name
                    file_path_field_ref.current.error_text = None

                students, faculty = read_pdf(file.path, ismale)
                all_students.extend(students)

            file_students['students'] = all_students

            # Build ALL rows once
            all_rows = [
                ft.DataRow(cells=[
                    create_table_cell(stu['seq_number']),
                    create_table_cell(stu['name']),
                    create_table_cell(stu['national_id']),
                    create_table_cell(stu['faculty']),
                ])
                for stu in all_students
            ]

            # Compute pagination stats & refresh
            total_pages = max(1, math.ceil(len(all_rows) / ROWS_PER_PAGE))
            current_page = 0
            update_stats()
            refresh_table()
            update_next_button_state()
        finally:
            # Hide loading indicator when done (whether success or error)
            progress_container_ref.current.visible = False
            page.update()

    # ------------------------------------------------------------------

    def pick_file(e):
        if file_picker_ref.current:
            file_picker_ref.current.pick_files(
                dialog_title="اختر ملف بيانات الدورة",
                allow_multiple=True,
                allowed_extensions=["pdf"]
            )
        else:
            sb = ft.SnackBar(ft.Text("خطأ في أداة اختيار الملفات"), open=True, bgcolor=ft.colors.RED)
            page.snack_bar = sb
            page.snack_bar.open = True
            page.update()

    def pick_date(e):
        if date_picker_ref.current:
            page.dialog = date_picker_ref.current
            date_picker_ref.current.open = True
            page.update()
        else:
            sb = ft.SnackBar(ft.Text("خطأ في أداة اختيار التاريخ"), open=True, bgcolor=ft.colors.RED)
            page.snack_bar = sb
            page.snack_bar.open = True
            page.update()

    def on_date_picked(e):
        file_students['date'] = e.control.value
        picker_instance = date_picker_ref.current
        if picker_instance and picker_instance.value:
            selected_date = picker_instance.value
            formatted_date = selected_date.strftime("%Y/%m/%d")
            if date_field_ref.current:
                date_field_ref.current.value = formatted_date
                date_field_ref.current.error_text = None
        if picker_instance:
            picker_instance.open = False
            if page.dialog == picker_instance:
                page.dialog = None
            page.update()
        update_next_button_state()

    # --- Picker setup ---
    fp_exists = any(isinstance(ctrl, ft.FilePicker) for ctrl in page.overlay)
    if not fp_exists:
        new_fp = ft.FilePicker(ref=file_picker_ref, on_result=on_file_picked)
        page.overlay.append(new_fp)
    else:
        for ctrl in page.overlay:
            if isinstance(ctrl, ft.FilePicker):
                file_picker_ref.current = ctrl
                ctrl.on_result = on_file_picked
                break

    dp_exists = any(isinstance(ctrl, ft.DatePicker) for ctrl in page.overlay)
    if not dp_exists:
        new_dp = ft.DatePicker(
            ref=date_picker_ref,
            on_change=on_date_picked,
            first_date=datetime(2000, 1, 1), last_date=datetime(2030, 12, 31),
            help_text="اختر تاريخ بداية الدورة", cancel_text="إلغاء", confirm_text="تأكيد"
        )
        page.overlay.append(new_dp)
    else:
        for ctrl in page.overlay:
            if isinstance(ctrl, ft.DatePicker):
                date_picker_ref.current = ctrl
                ctrl.on_change = on_date_picked
                break
    page.update()

    # --- Confirmation Dialog ---
    confirm_button_style = ft.ButtonStyle(
        color=WHITE_COLOR, bgcolor=CONFIRM_BUTTON_COLOR, padding=ft.padding.symmetric(vertical=12, horizontal=40),
        shape=ft.RoundedRectangleBorder(radius=8)
    )
    cancel_button_style = ft.ButtonStyle(
        color=WHITE_COLOR, bgcolor=CANCEL_BUTTON_COLOR, padding=ft.padding.symmetric(vertical=12, horizontal=40),
        shape=ft.RoundedRectangleBorder(radius=8)
    )

    # --- UI controls ---
    # Create the progress container itself
    progress_container = ft.Container(
        ref=progress_container_ref,
        content=ft.Column([
            ft.ProgressRing(ref=progress_ring_ref, width=40, height=40, stroke_width=3, color=PRIMARY_COLOR),
            ft.Text("جاري قراءة الملفات...", color=PRIMARY_COLOR, size=14, weight=ft.FontWeight.BOLD),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        padding=10,
        bgcolor=ft.colors.with_opacity(0.9, WHITE_COLOR),
        border_radius=10,
        width=200,
        height=100,
        visible=False,  # Hidden by default
    )
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color=PRIMARY_COLOR,
        tooltip="العودة", on_click=go_back, icon_size=30
    )
    title1 = ft.Text("تسجيل دورة جديدة", size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR,
                     text_align=ft.TextAlign.CENTER)
    title2 = ft.Text("اضافة ملف وتاريخ الدورة", size=20, weight=ft.FontWeight.W_500, color=TEXT_COLOR_DARK,
                     text_align=ft.TextAlign.CENTER)

    file_path_field = ft.TextField(
        ref=file_path_field_ref,
        color="#000000",
        hint_text="اختر ملف بيانات الطلاب (PDF)...", read_only=True,
        text_align=ft.TextAlign.RIGHT, height=55, border_color=PRIMARY_COLOR,
        border_radius=8, border_width=1.5, content_padding=ft.padding.only(right=15, left=5, top=5),
        suffix=ft.IconButton(
            icon=ft.icons.UPLOAD_FILE_OUTLINED, icon_color=PRIMARY_COLOR,
            tooltip="اختيار ملف", on_click=pick_file,
        ),
        expand=True
    )
    date_field = ft.TextField(
        ref=date_field_ref,
        color="#000000",
        hint_text="YYYY/MM/DD",
        read_only=True,
        text_align=ft.TextAlign.CENTER,
        height=55,
        width=200,
        border_color=PRIMARY_COLOR,
        border_radius=8,
        border_width=1.5,
        content_padding=ft.padding.only(right=5, left=5, top=5),
        suffix=ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH_OUTLINED,
            icon_color=PRIMARY_COLOR,
            tooltip="اختيار تاريخ الدورة",
            on_click=pick_date,
        ),
    )
    next_step_button = ft.ElevatedButton(
    text="تأكيد",
    bgcolor=PRIMARY_COLOR, color=WHITE_COLOR,
    height=50, width=200,
    on_click=handle_confirm_upload,
    disabled=True,                         # <── initially disabled
    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                         padding=ft.padding.symmetric(vertical=10)),
    )
    info_text = ft.Row(
        [
            ft.Text(
                "هذا النموذج يُمثل الشكل والترتيب المثاليين لملف بيانات الطلاب في الدورة، وأي تعديل على هذا التنسيق قد يؤدي إلى حدوث أخطاء في عمل البرنامج.",
                text_align=ft.TextAlign.RIGHT, color=TEXT_COLOR_DARK, size=14, expand=True),
            ft.Icon(name=ft.icons.VISIBILITY_OUTLINED, color=PRIMARY_COLOR, size=24),
        ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        run_spacing=5, width=700,
    )

    banner_control = create_banner()

    content_column = ft.Column(
        [
            ft.Container(
                ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(top=15, left=30, right=30, bottom=5)
            ),
            title1,
            title2,
            ft.Container(height=20),
            ft.Row(
                [date_field, file_path_field],
                alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, spacing=20,
            ),
            progress_container,
            ft.Container(height=15),
            ft.Row([next_step_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([info_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            stats_container,
            nav_bar,
            ft.Row(
                [ft.Container(content=data_table, width=700)],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(height=30),
        ],
        expand=True, scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.View(
        route="/upload_course_file",
        bgcolor=BG_COLOR,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    content_column
                ],
                expand=True, spacing=0
            )
        ]
    )