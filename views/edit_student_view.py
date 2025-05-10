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

edit_attributes = {}
faculty_lookup = {}


def update_field(name: str, value: str):
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
        label_style=ft.TextStyle(color="#B58B18", size=14),
        border_color="#B58B18",
        color="#000000",
        focused_border_color="#B58B18",
        bgcolor=ft.Colors.WHITE,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
        height=45,
        on_change=lambda e: update_field(e.control.data, value=e.control.value)
    )


def create_attendance_table(page: ft.Page, student_id: int, course_start_date: date):
    """Creates a horizontal scrollable table showing attendance for each day."""
    attendance_records = get_attendance_by_student_id(student_id)
    present_dates = {record.date for record in attendance_records}

    # Generate all days of the course (2 weeks starting Saturday)
    days = []
    current_date = course_start_date
    for week in range(1, 3):
        for _ in range(7):
            day_name = get_arabic_day_name(current_date.weekday())
            day_display = f"{day_name} {week}"
            days.append((current_date, day_display))
            current_date += timedelta(days=1)

    # Create columns
    columns = []
    for day_date, day_display in days:
        columns.append(
            ft.DataColumn(
                ft.Text(day_display, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                numeric=False
            )
        )

    # Create single row with all days
    cells = []
    for day_date, day_display in days:
        attended = day_date in present_dates
        icon_button = ft.IconButton(
            icon=ft.icons.CHECK if attended else ft.icons.CLOSE,
            icon_color=ft.colors.GREEN if attended else ft.colors.RED,
            data={"date": day_date, "student_id": student_id},
            on_click=lambda e: toggle_attendance(e, page),
            key=f"att_{day_date}",
            icon_size=20
        )
        cells.append(ft.DataCell(icon_button))

    # Create data table
    table = ft.DataTable(
        columns=columns,
        rows=[ft.DataRow(cells=cells)],
        heading_row_color=ft.colors.GREY_200,
        heading_row_height=40,
        horizontal_margin=15,
        column_spacing=20,
        divider_thickness=1,
        border=ft.border.all(1, "#B58B18"),
    )

    # Create a horizontally scrollable container
    return ft.Row(
        controls=[
            ft.Container(
                content=table,
                padding=10,
                border_radius=8,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
def toggle_attendance(e, page: ft.Page):
    """Toggle attendance status for a specific date"""
    student_id = e.control.data["student_id"]
    date = e.control.data["date"]

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
        else:
            # Create new record
            new_att = Attendance(
                student_id=student_id,
                date=date,
                arrival_time=time(0, 0)  # Default time
            )
            session.add(new_att)
            new_status = True
        session.commit()

    # Update UI
    e.control.icon = ft.icons.CHECK if new_status else ft.icons.CLOSE
    e.control.icon_color = ft.colors.GREEN if new_status else ft.colors.RED
    page.update()


def get_arabic_day_name(weekday: int) -> str:
    """Returns the Arabic name for the given weekday."""
    arabic_days = [
        "السبت", "الاحد", "الاثنين",
        "الاربعاء", "الخميس", "الجمعة", "السبت"
    ]
    return arabic_days[(weekday + 2) % 7]


def create_edit_student_view(page: ft.Page):
    """Creates the Flet View for the Edit Student Data screen."""
    faculties = get_all_faculties()
    for fac in faculties:
        faculty_lookup[fac.id] = fac.name

    def go_back(e):
        page.go("/search_student")

    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, icon_color="#B58B18",
        tooltip="العودة", on_click=go_back, icon_size=30
    )

    page_title = ft.Text(
        "تعديل بيانات الطالب",
        size=32, weight=ft.FontWeight.BOLD, color="#B58B18"
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
        border_color="#B58B18",
        focused_border_color="#B58B18",
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
        bgcolor="#B58B18",
        color=ft.Colors.WHITE,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=save_data
    )

    # --- Attendance Table ---
    attendance_table = ft.Column([
        ft.Text("سجل الحضور", size=20, weight=ft.FontWeight.BOLD, color="#B58B18"),
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
                    attendance_table
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
        bgcolor="#E3DCCC",
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