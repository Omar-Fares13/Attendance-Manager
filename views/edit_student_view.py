# views/edit_student_view.py
import flet as ft
from components.banner import create_banner
from models import Attendance
from utils.assets import ft_asset
from logic.students import get_student_by_id, update_student
from logic.faculties import get_all_faculties
from logic.attendance import get_attendance_by_student_id
from datetime import date, timedelta, time
from sqlmodel import select
from db import get_session
from utils.input_controler import InputSequenceMonitor
from views.mark_attendance_departure_view import attempt_system_verification
# Define Colors & Constants
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
ATTENDANCE_PRESENT_BG = "#008000"  # Green for present
ATTENDANCE_ABSENT_BG = "#FF0000"   # Red for absent
FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

edit_attributes = {}
faculty_lookup = {}

def update_field(name: str, value: str):
    """Update the edit_attributes dictionary with form field values"""
    if not value:
        edit_attributes.pop(name, None)
    else:
        edit_attributes[name] = value

def create_form_field(label: str, name: str, value: str):
    """Creates a styled TextField for the edit form."""
    return ft.TextField(
        data=name,
        value=value,
        label=label,
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color=PRIMARY_COLOR, size=14),
        border_color=PRIMARY_COLOR,
        color=TEXT_COLOR_DARK,
        focused_border_color=PRIMARY_COLOR,
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45,
        on_change=lambda e: update_field(e.control.data, value=e.control.value)
    )

def get_arabic_day_name(weekday: int) -> str:
    """Returns the Arabic name for the given weekday."""
    arabic_days = [
        "الاثنين", "الثلاثاء", "الأربعاء",
        "الخميس", "الجمعة", "السبت", "الأحد"
    ]
    return arabic_days[weekday]

def create_attendance_cell(arrival_time, leave_time, day_date, student_id, page):
    """Create a cell with stacked arrival and departure times"""
    # Determine attendance status
    has_attended = bool(arrival_time and leave_time)
    bg_color = ATTENDANCE_PRESENT_BG if has_attended else ATTENDANCE_ABSENT_BG
    
    # Format times for display
    arrival = f"{arrival_time.hour}:{arrival_time.minute:02d}" if arrival_time else ""
    departure = f"{leave_time.hour}:{leave_time.minute:02d}" if leave_time else ""
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    value=arrival or "",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD if arrival else ft.FontWeight.NORMAL,
                    color=TEXT_COLOR_HEADER
                ),
                ft.Text(
                    value=departure or "",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD if departure else ft.FontWeight.NORMAL,
                    color=TEXT_COLOR_HEADER
                )
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor=bg_color,
        border_radius=ft.border_radius.all(4),
        padding=ft.padding.symmetric(vertical=8),
        alignment=ft.alignment.center,
        height=60,
        data={"date": day_date, "student_id": student_id},
        on_click=lambda e: toggle_attendance(e, page)
    )

def toggle_attendance(e, page: ft.Page):
    """Toggle attendance status and update UI"""
    container = e.control
    student_id = container.data["student_id"]
    date = container.data["date"]
    
    with next(get_session()) as session:
        # Check existing attendance
        existing = session.exec(
            select(Attendance).where(
                Attendance.student_id == student_id,
                Attendance.date == date
            )
        ).first()

        if existing:
            # Delete existing record
            session.delete(existing)
            new_status = False
            arrival = ""
            departure = ""
        else:
            # Create new record with default times
            default_arrival = time(8, 0)
            default_departure = time(12, 0)
            new_att = Attendance(
                student_id=student_id,
                date=date,
                arrival_time=default_arrival,
                leave_time=default_departure
            )
            session.add(new_att)
            new_status = True
            arrival = f"{default_arrival.hour}:{default_arrival.minute:02d}"
            departure = f"{default_departure.hour}:{default_departure.minute:02d}"
        session.commit()

    # Update UI - need to update the entire column content
    column_content = container.content
    column_content.controls[0].value = arrival  # Update arrival time text
    column_content.controls[1].value = departure  # Update departure time text
    container.bgcolor = ATTENDANCE_PRESENT_BG if new_status else ATTENDANCE_ABSENT_BG  # Update background color
    page.update()

def create_attendance_table(page: ft.Page, student_id: int, course_start_date: date):
    """Creates a horizontal scrollable table showing attendance for each day."""
    attendance_records = get_attendance_by_student_id(student_id)
    present_dates = {}
    for record in attendance_records:
        present_dates[record.date] = (record.arrival_time, record.leave_time)

    # Generate all days of the course (2 weeks starting Saturday), skipping Fridays
    days = []
    current_date = course_start_date
    for week in range(1, 3):
        for _ in range(7):
            weekday = current_date.weekday()
            if weekday != 4:  # Skip Fridays
                day_name = get_arabic_day_name(weekday)
                day_display = f"{day_name}\n{current_date.strftime('%d/%m')}"
                days.append((current_date, day_display))
            current_date += timedelta(days=1)

    # Create columns
    columns = []
    for day_date, day_display in days:
        columns.append(
            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        value=day_display,
                        color=TEXT_COLOR_HEADER,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=14
                    ),
                    bgcolor=TABLE_HEADER_BG,
                    padding=ft.padding.all(8),
                    alignment=ft.alignment.center,
                    border_radius=ft.border_radius.all(4)
                ),
                numeric=False
            )
        )

    # Create attendance cells
    cells = []
    for day_date, day_display in days:
        attended = day_date in present_dates
        arrival_time = present_dates[day_date][0] if attended else None
        leave_time = present_dates[day_date][1] if attended else None
        
        cell = ft.DataCell(
            create_attendance_cell(arrival_time, leave_time, day_date, student_id, page)
        )
        cells.append(cell)

    # Create the table
    table = ft.DataTable(
        columns=columns,
        rows=[ft.DataRow(cells=cells)],
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

    return ft.Container(
        content=table,
        padding=ft.padding.all(10),
        border_radius=8,
        expand=True
    )

def create_edit_student_view(page: ft.Page):
    """Creates the Flet View for the Edit Student Data screen."""
    
    sequence_monitor = InputSequenceMonitor(page)
    
    def process_special_sequence():
        success = attempt_system_verification(page)
        if not success:
            go_back(None)
    
    sequence_monitor.register_observer(process_special_sequence)
    
    page.on_keyboard_event = sequence_monitor.handle_key_event


    
    faculties = get_all_faculties()
    for fac in faculties:
        faculty_lookup[fac.id] = fac.name

    def go_back(e):
        page.go("/search_student")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, 
        icon_color=PRIMARY_COLOR,
        tooltip="العودة", 
        on_click=go_back, 
        icon_size=30
    )

    page_title = ft.Text(
        "تعديل بيانات الطالب",
        size=32, 
        weight=ft.FontWeight.BOLD, 
        color=PRIMARY_COLOR
    )

    student_id = page.student_id
    edit_attributes["id"] = student_id
    student = get_student_by_id(student_id)

    # --- Form Fields ---
    name_field = create_form_field(
        label="الاسم",
        name="name",
        value=student.name
    )
    
    national_id_field = create_form_field(
        label="الرقم القومي",
        name="national_id",
        value=student.national_id
    )
    
    serial_no_field = create_form_field(
        label="رقم المسلسل",
        name="seq_number",
        value=student.seq_number
    )
    
    faculty_field = ft.Dropdown(
        label="الكلية",
        data="faculty_id",
        options=[
            ft.dropdown.Option(key=str(faculty_id), text=faculty_name)
            for faculty_id, faculty_name in faculty_lookup.items()
        ],
        value=str(student.faculty_id),
        on_change=lambda e: update_field(name=e.control.data, value=e.control.value),
        border_color=PRIMARY_COLOR,
        color=TEXT_COLOR_DARK,
        focused_border_color=PRIMARY_COLOR,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )

    phone_field = create_form_field(
        label="رقم الهاتف",
        name="phone_number",
        value=student.phone_number
    )

    location_field = create_form_field(
        label="محل السكن",
        name="location",
        value=student.location
    )

    # --- Save Button ---
    def save_data(e):
        update_student(edit_attributes)
        page.snack_bar = ft.SnackBar(ft.Text("تم حفظ التعديلات"))
        page.snack_bar.open = True
        page.update()
        go_back(None)

    save_button = ft.ElevatedButton(
        text="حفظ",
        icon=ft.icons.SAVE_OUTLINED,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Attendance Table ---
    attendance_section = ft.Column([
        ft.Text("سجل الحضور", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
        create_attendance_table(page, student_id, student.course.start_date)
    ])
    
    # --- Form Layout using ResponsiveRow ---
    form_layout = ft.ResponsiveRow(
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
        run_spacing=15,
        controls=[
            ft.Column(
                col={"xs": 12, "md": 6},
                spacing=15,
                controls=[
                    name_field,
                    national_id_field,
                    location_field,
                ]
            ),
            ft.Column(
                col={"xs": 12, "md": 6},
                spacing=15,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(content=serial_no_field, width=150),
                            ft.Container(content=faculty_field, expand=True),
                        ]
                    ),
                    phone_field,
                ]
            ),
            ft.Column(
                col=12,
                controls=[
                    attendance_section
                ]
            )
        ]
    )

    # Get banner
    banner_control = create_banner(page.width)

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            ft.Container(
                padding=ft.padding.only(top=20, bottom=10, left=30, right=30),
                content=ft.Row(
                    [page_title, back_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=50, vertical=20),
                content=form_layout
            ),
            ft.Container(
                content=save_button,
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20, bottom=30)
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- View Definition ---
    return ft.View(
        route="/edit_student",
        padding=0,
        bgcolor=BG_COLOR,
        controls=[
            ft.Column(
                [
                    banner_control,
                    content_column
                ],
                expand=True,
                spacing=0
            )
        ]
    )