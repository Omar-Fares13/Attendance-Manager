# views/report_view_days.py

import flet as ft
import math
from logic import course
from logic.students import create_students_from_file
from components.banner import create_banner
from logic.file_write import extract_xlsx
from datetime import date, timedelta
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
from logic.attendance import get_attendance_data

# Set locale for Arabic weekday names
try:
    locale.setlocale(locale.LC_TIME, 'ar_AE.UTF-8')  # For Unix/Linux
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Arabic')  # For Windows
    except:
        pass  # Fallback - will use hardcoded Arabic day names if locale fails

# --- Define Colors & Fonts ---
BG_COLOR = "#E3DCCC"
PRIMARY_COLOR = "#B58B18"
TEXT_COLOR_DARK = "#333333"
TEXT_COLOR_HEADER = ft.colors.WHITE
TABLE_HEADER_BG = "#5A5A5A"
TABLE_CELL_BG = ft.colors.with_opacity(0.95, ft.colors.WHITE)
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, PRIMARY_COLOR)
BUTTON_CONFIRM_COLOR = ft.colors.GREEN_700
BUTTON_CANCEL_COLOR = ft.colors.GREY_700
BUTTON_TEXT_COLOR = ft.colors.WHITE

TABLE_ALT_ROW_BG = "#EFEFEF"
ATTENDANCE_PRESENT_BG = "#008000"  # Light green
ATTENDANCE_ABSENT_BG = "#FF0000"  # Light red

FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

attribs = {}

content_ref = ft.Ref[ft.Column]()


def get_report_dates(page=None, course_id=None):
    """
    Generate 12 school days (Saturday through Thursday, skipping Fridays) 
    starting from the course start date
    
    Args:
        page: Optional Flet page object that may contain course_id
        course_id: Optional course ID to use directly
        
    Returns:
        List of 12 date objects representing school days
    """
    from logic.course import get_latest_course

    # Get course ID from parameters or page object
    if course_id is None and page is not None:
        course_id = getattr(page, 'course_id', None)

    # Get the course from database
    if course_id:
        from sqlmodel import Session, select
        from models import Course
        from db import get_session

        with next(get_session()) as session:
            stmt = select(Course).where(Course.id == course_id)
            course = session.exec(stmt).one_or_none()
    else:
        # Fallback to latest course if no course_id provided
        course = get_latest_course()

    # Use course start date if available, otherwise use today
    if course and course.start_date:
        start_date = course.start_date
    else:
        # Fallback to today if no course found
        today = date.today()
        days_since_saturday = (today.weekday() + 2) % 7
        start_date = today - timedelta(days=days_since_saturday)

    # Find the first Saturday on or after the start date
    # If start_date is already a Saturday (weekday 5), use it directly
    if start_date.weekday() != 5:  # Not a Saturday
        days_until_saturday = (5 - start_date.weekday()) % 7
        start_date = start_date + timedelta(days=days_until_saturday)

    report_dates = []
    current_date = start_date

    while len(report_dates) < 12:
        if current_date.weekday() != 4:  # Skip Fridays (4 is Friday in Python's weekday)
            report_dates.append(current_date)
        current_date += timedelta(days=1)

    return report_dates


def create_headers(dates):
    """Create header texts for the data table"""
    # Arabic day names (fallback if locale setting fails)
    arabic_days = {
        0: "اثنين",  # Monday
        1: "ثلاثاء",  # Tuesday
        2: "أربعاء",  # Wednesday
        3: "خميس",  # Thursday
        4: "جمعة",  # Friday
        5: "سبت",  # Saturday
        6: "أحد"  # Sunday
    }

    headers = ["م", "الاسم", "الكلية"]  # seq, name, faculty

    for d in dates:
        try:
            # Try to get the Arabic day name using locale
            day_name = d.strftime("%A")
            if not any(c in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي' for c in day_name):
                # Fallback if locale didn't work
                day_name = arabic_days[d.weekday()]
        except:
            # Fallback if locale didn't work
            day_name = arabic_days[d.weekday()]

        date_str = f"{day_name}\n{d.strftime('%d/%m')}"
        headers.append(date_str)

    return headers


def create_data_columns(headers):
    """Create DataColumn objects for the data table"""
    return [
        ft.DataColumn(
            ft.Container(
                content=ft.Text(
                    value=header,
                    color="white",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    size=14
                ),
                bgcolor=TABLE_HEADER_BG,
                padding=ft.padding.all(8),
                alignment=ft.alignment.center,
                border_radius=ft.border_radius.all(4),
                # width=100 if i > 2 else None  # Fixed width for date columns
            ),
            numeric=i == 0  # Only sequence number is numeric
        ) for i, header in enumerate(headers)
    ]


def create_attendance_cell(arrival, departure, attended_days):
    """Create a cell with stacked arrival and departure times"""
    # Determine background color based on attendance
    has_attended = bool(arrival and departure)
    bg_color = ATTENDANCE_PRESENT_BG if has_attended else ATTENDANCE_ABSENT_BG

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    value=arrival or "",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD if arrival else ft.FontWeight.NORMAL,
                ),
                ft.Text(
                    value=departure or "",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD if departure else ft.FontWeight.NORMAL,
                ),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=bg_color,
        border_radius=ft.border_radius.all(4),
        padding=ft.padding.symmetric(vertical=8),
        alignment=ft.alignment.center,
        height=60,
    )


def create_data_rows(dates, processed_data):
    rows = []
    for i, student in enumerate(processed_data):
        attended_days = 0
        cells = [
            ft.DataCell(ft.Text(value=str(student['seq']), text_align=ft.TextAlign.CENTER, color="#000000")),
            ft.DataCell(ft.Text(value=student['name'], text_align=ft.TextAlign.CENTER, color="#000000")),
            ft.DataCell(ft.Text(value=student['faculty'], text_align=ft.TextAlign.CENTER, color="#000000")),
        ]

        for d in dates:
            attendance_data = student['attendance'].get(d, {})
            arrival = attendance_data.get('arrival', '')
            departure = attendance_data.get('departure', '')
            if arrival.strip() and departure.strip():
                attended_days += 1
            cells.append(ft.DataCell(create_attendance_cell(arrival, departure, attended_days)))

        bg_color = TABLE_ALT_ROW_BG if i % 2 == 1 else TABLE_CELL_BG
        rows.append(ft.DataRow(cells=cells, color=bg_color))

    return rows


def create_report_alt_view(page: ft.Page):
    sequence_monitor = InputSequenceMonitor(page)

    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)

    sequence_monitor.register_observer(process_special_sequence)

    page.on_keyboard_event = sequence_monitor.handle_key_event

    # 1) Get dates & headers exactly as before
    report_dates = get_report_dates(page)
    headers = create_headers(report_dates)
    columns = create_data_columns(headers)

    # 2) Get the raw attendance data
    sample_data = get_attendance_data(page, report_dates)

    # 3) Build ALL rows once
    all_rows = create_data_rows(report_dates, sample_data)

    # ------------ Pagination settings -------------
    rows_per_page = 30  # tweak to whatever fits the screen
    total_pages = max(1, math.ceil(len(all_rows) / rows_per_page))
    current_page = 0  # zero-based index

    # ----------------------------------------------

    # Helper that returns the slice for a given page
    def page_rows(page_index: int) -> list[ft.DataRow]:
        start = page_index * rows_per_page
        end = start + rows_per_page
        return all_rows[start:end]

    # 4) Build the DataTable with ONLY page-0 rows
    data_table = ft.DataTable(
        columns=columns,
        rows=page_rows(current_page),
        border=ft.border.all(1, TABLE_BORDER_COLOR),
        border_radius=ft.border_radius.all(8),
        vertical_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        horizontal_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        heading_row_height=80,
        data_row_min_height=60,
        data_row_max_height=80,
        divider_thickness=1,
        column_spacing=10,
    )

    # 5) Navigation bar ------------------------------------------------
    page_number_text = ft.Text(
        f"{current_page + 1} / {total_pages}",
        weight=ft.FontWeight.BOLD,
        size=16
    )

    def refresh_table():
        nonlocal current_page
        # clamp to valid range
        current_page = max(0, min(current_page, total_pages - 1))
        data_table.rows = page_rows(current_page)
        page_number_text.value = f"{current_page + 1} / {total_pages}"
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

    nav_bar = ft.Row(
        [
            ft.IconButton(
                icon=ft.icons.CHEVRON_RIGHT,  # right-to-left UI
                on_click=prev_page,
                tooltip="السابق"
            ),
            page_number_text,
            ft.IconButton(
                icon=ft.icons.CHEVRON_LEFT,
                on_click=next_page,
                tooltip="التالي"
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # ------------------------------------------------------------------

    # (unchanged) Excel export button, back button, etc.
    def go_back(e):
        page.go("/report_course")

    # ... your Excel export handler / banner / title code here …

    excel_button = ft.ElevatedButton(
        key="confirm_section",
        text="استخراج ملف Excel",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50,
        width=220,
        on_click=lambda e: extract_xlsx(
            e, page, report_dates, sample_data, headers
        ),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    scroll_down_fab = ft.FloatingActionButton(
        icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
        tooltip="اذهب إلى الأسفل",
        on_click=lambda e: content_ref.current.scroll_to(
            key="confirm_section",
            duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )
    )

    banner_control = create_banner()

    # 6) Put everything together
    content_column = ft.Column(
        [
            # back button row
            ft.Container(ft.Row([ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED,
                                               tooltip="العودة",
                                               icon_color=PRIMARY_COLOR,
                                               on_click=go_back,
                                               icon_size=30)],
                                alignment=ft.MainAxisAlignment.START),
                         padding=ft.padding.only(top=15, left=30, right=30)),

            # title
            ft.Container(ft.Text("تقرير مفصل بالايام",
                                 size=32,
                                 weight=ft.FontWeight.BOLD,
                                 color=PRIMARY_COLOR,
                                 font_family=FONT_FAMILY_BOLD,
                                 text_align=ft.TextAlign.CENTER),
                         padding=ft.padding.symmetric(horizontal=30),
                         alignment=ft.alignment.center),

            # DATA TABLE
            data_table,

            # pagination navigation bar
            nav_bar,

            ft.Container(height=30),

            # Excel button
            ft.Row([excel_button], alignment=ft.MainAxisAlignment.CENTER),

            ft.Container(height=30),
        ],
        ref=content_ref,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=20
    )

    return ft.View(
        route="/report_alt",
        bgcolor=BG_COLOR,
        floating_action_button=scroll_down_fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(
                        content=content_column,
                        expand=True,
                        padding=ft.padding.only(left=30, right=30, bottom=20)
                    )
                ],
                expand=True,
                spacing=0
            )
        ]
    )
