import flet as ft
from datetime import datetime
import os
from components.banner import create_banner
from logic.file_reader import read_pdf
from logic.students import create_students_from_file
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


file_students = {}

def add_students(e):
    students = file_students['students']
    is_male = file_students['is_male']
    file_students['students'] = ''
    print(file_students)
    faculty = file_students['faculty']
    course_date = file_students['date']
    create_students_from_file(students, faculty, course_date, is_male)

def create_table_cell(text_content):
    return ft.DataCell(ft.Text(str(text_content), color=CELL_TEXT_COLOR, text_align=ft.TextAlign.RIGHT, size=13))

def create_upload_course_file_view(page: ft.Page):
    file_path_field_ref = ft.Ref[ft.TextField]()
    date_field_ref = ft.Ref[ft.TextField]()
    file_picker_ref = ft.Ref[ft.FilePicker]()
    date_picker_ref = ft.Ref[ft.DatePicker]()
    confirmation_dialog_ref = ft.Ref[ft.AlertDialog]()
    selected_file_full_path = ft.Ref[str]()
    data_table_ref = ft.Ref[ft.DataTable]()  # Ref for our datatable

    print(page.route)
    print(page.route.split('=')[-1])
    file_students['is_male'] = page.route.split('=')[-1]
    ismale = file_students['is_male']
    # --- Table Columns ---
    columns = [
        ft.DataColumn(ft.Text("الرقم المسلسل", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), numeric=True),
        ft.DataColumn(ft.Text("الاسم", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
        ft.DataColumn(ft.Text("الرقم القومي", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
        ft.DataColumn(ft.Text("الكليه", color=HEADER_TEXT_COLOR, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
    ]

    # Initially, table is empty
    rows = []
    data_table = ft.DataTable(
        ref=data_table_ref,
        columns=columns,
        rows=rows,
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

    # --- Handlers ---
    def handle_confirm_upload(e):
        if confirmation_dialog_ref.current:
            confirmation_dialog_ref.current.open = False
        file_path = selected_file_full_path.current
        file_name_display = file_path_field_ref.current.value if file_path_field_ref.current else "الملف المحدد"

        if not file_path:
            sb = ft.SnackBar(ft.Text("خطأ: لم يتم تحديد مسار الملف."), open=True, bgcolor=ft.colors.RED)
            page.snack_bar = sb
            page.snack_bar.open = True
            page.update()
            return

        page.go("/register_course")  # Go to next view after confirm

    def handle_cancel_upload(e):
        if confirmation_dialog_ref.current:
            confirmation_dialog_ref.current.open = False
            page.update()

    def go_back(e):
        selected_file_full_path.current = None
        page.go("/register_course_options?male=" + file_students['is_male'])

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            selected_file = e.files[0]
            if file_path_field_ref.current:
                file_path_field_ref.current.value = selected_file.name
                selected_file_full_path.current = selected_file.path
                file_path_field_ref.current.error_text = None

                # ---- Main PDF parsing Logic ----
                students, faculty = read_pdf(selected_file.path, ismale)
                file_students['students'] = students
                file_students['faculty'] = faculty
                new_rows = [
                    ft.DataRow(cells=[
                        create_table_cell(student['seq_number']),
                        create_table_cell(student['name']),
                        create_table_cell(student['national_id']),
                        create_table_cell(faculty),
                    ])
                    for student in students
                ]
                data_table_ref.current.rows = new_rows
                page.update()
        else:
            selected_file_full_path.current = None
            if file_path_field_ref.current:
                file_path_field_ref.current.value = None
        page.update()

    def pick_file(e):
        if file_picker_ref.current:
            file_picker_ref.current.pick_files(
                dialog_title="اختر ملف بيانات الدورة",
                allow_multiple=False,
                allowed_extensions=["pdf"]  # Only PDF!
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
            first_date=datetime(2020, 1, 1), last_date=datetime(2030, 12, 31),
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
    confirmation_dialog = ft.AlertDialog(
        ref=confirmation_dialog_ref, modal=True, bgcolor=DIALOG_BG_COLOR, shape=ft.RoundedRectangleBorder(radius=10),
        content=ft.Column(
            [
                ft.Text(
                    "هل أنت متأكد من صحة بيانات ملف الدورة\nوترغب في تأكيد رفع الملف؟",
                    text_align=ft.TextAlign.CENTER, size=16, weight=ft.FontWeight.BOLD, color=TEXT_COLOR_DARK
                ),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                ft.Text(
                    "سيتم نقلك إلى شاشة المراجعة والتعديل.",
                    text_align=ft.TextAlign.CENTER, size=14, color=TEXT_COLOR_DARK, weight=ft.FontWeight.W_500
                ),
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5
        ),
        content_padding=ft.padding.symmetric(horizontal=25, vertical=20),
        actions=[
            ft.ElevatedButton("تأكيد", on_click=handle_confirm_upload, style=confirm_button_style),
            ft.ElevatedButton("الرجوع", on_click=handle_cancel_upload, style=cancel_button_style),
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        actions_padding=ft.padding.only(bottom=20, left=20, right=20),
    )

    # --- UI controls ---
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color=PRIMARY_COLOR,
        tooltip="العودة", on_click=go_back, icon_size=30
    )
    title1 = ft.Text("تسجيل دورة جديدة", size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR, text_align=ft.TextAlign.CENTER)
    title2 = ft.Text("اضافة ملف وتاريخ الدورة", size=20, weight=ft.FontWeight.W_500, color=TEXT_COLOR_DARK, text_align=ft.TextAlign.CENTER)

    file_path_field = ft.TextField(
        ref=file_path_field_ref,
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
        bgcolor=PRIMARY_COLOR, color=WHITE_COLOR, height=50, width=200,
        on_click=add_students,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(vertical=10))
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
            ft.Container(height=15),
            ft.Row([next_step_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([info_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            ft.Row(
                [ft.Container(content=data_table)],
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