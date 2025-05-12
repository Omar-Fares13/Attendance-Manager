import flet as ft
from datetime import date, datetime, timedelta
import locale

# Set locale for Arabic weekday names
try:
    locale.setlocale(locale.LC_TIME, 'ar_AE.UTF-8')  # For Unix/Linux
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Arabic')  # For Windows
    except:
        pass  # Fallback - will use hardcoded Arabic day names if locale fails

# --- Define Colors ---
TABLE_HEADER_BG = "#5A5A5A"
TABLE_CELL_BG = "#F5F5F5"
TABLE_BORDER_COLOR = "#DDDDDD"
TABLE_ALT_ROW_BG = "#EFEFEF"
ATTENDANCE_PRESENT_BG = "#008000"  # Light green
ATTENDANCE_ABSENT_BG = "#FF0000"   # Light red


def get_report_dates():
    """Generate 12 school days (Saturday through Thursday, skipping Fridays)"""
    today = date.today()
    
    # Find the most recent Saturday (or today if it's Saturday)
    days_since_saturday = (today.weekday() + 2) % 7  # Saturday is 5 in Python's weekday()
    start_date = today - timedelta(days=days_since_saturday)
    
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
        0: "اثنين",   # Monday
        1: "ثلاثاء",  # Tuesday
        2: "أربعاء",  # Wednesday
        3: "خميس",    # Thursday
        4: "جمعة",    # Friday
        5: "سبت",     # Saturday
        6: "أحد"      # Sunday
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


def create_attendance_cell(arrival, departure):
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
                    weight=ft.FontWeight.BOLD if arrival else ft.FontWeight.NORMAL
                ),
                ft.Text(
                    value=departure or "",
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD if departure else ft.FontWeight.NORMAL
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
        width=60
    )


def create_data_rows(dates, processed_data):
    """Create DataRow objects for the data table"""
    rows = []
    
    for i, student in enumerate(processed_data):
        cells = [
            # Sequence number
            ft.DataCell(
                ft.Text(value=str(student['seq']), text_align=ft.TextAlign.CENTER)
            ),
            # Student name
            ft.DataCell(
                ft.Text(value=student['name'], text_align=ft.TextAlign.CENTER)
            ),
            # Faculty name
            ft.DataCell(
                ft.Text(value=student['faculty'], text_align=ft.TextAlign.CENTER)
            )
        ]
        
        # Add attendance cells for each date
        for d in dates:
            attendance_data = student['attendance'].get(d, {})
            arrival = attendance_data.get('arrival', '')
            departure = attendance_data.get('departure', '')
            
            cells.append(
                ft.DataCell(
                    create_attendance_cell(arrival, departure)
                )
            )
        
        # Alternate row background colors
        bg_color = TABLE_ALT_ROW_BG if i % 2 == 1 else TABLE_CELL_BG
        
        rows.append(ft.DataRow(cells=cells, color=bg_color))
    
    return rows


def create_report_days_view(page: ft.Page) -> ft.View:
    """Create the main attendance report view"""
    # Get dates for our report
    report_dates = get_report_dates()
    
    # Create headers and columns
    headers = create_headers(report_dates)
    columns = create_data_columns(headers)
    
    # Sample data (in a real app, this would come from a database)
    sample_data = [
        {
            'seq': 1,
            'name': 'أحمد محمود',
            'faculty': 'علوم الحاسوب',
            'attendance': {
                report_dates[0]: {'arrival': '08:15', 'departure': '12:30'},
                report_dates[1]: {'arrival': '08:20', 'departure': '12:35'},
                report_dates[3]: {'arrival': '08:00', 'departure': '12:30'},
                report_dates[5]: {'arrival': '08:10', 'departure': ''},
                report_dates[7]: {'arrival': '08:30', 'departure': '12:15'},
                report_dates[10]: {'arrival': '08:05', 'departure': '12:25'},
            }
        },
        {
            'seq': 2,
            'name': 'فاطمة علي',
            'faculty': 'الهندسة',
            'attendance': {
                report_dates[0]: {'arrival': '08:05', 'departure': '12:25'},
                report_dates[2]: {'arrival': '08:10', 'departure': '12:30'},
                report_dates[3]: {'arrival': '08:15', 'departure': '12:35'},
                report_dates[4]: {'arrival': '08:00', 'departure': '12:20'},
                report_dates[8]: {'arrival': '08:25', 'departure': '12:40'},
                report_dates[9]: {'arrival': '08:15', 'departure': '12:30'},
            }
        },
        {
            'seq': 3,
            'name': 'محمد سامي',
            'faculty': 'الطب',
            'attendance': {
                report_dates[1]: {'arrival': '08:30', 'departure': '12:45'},
                report_dates[2]: {'arrival': '08:25', 'departure': '12:40'},
                report_dates[5]: {'arrival': '08:15', 'departure': '12:30'},
                report_dates[6]: {'arrival': '08:20', 'departure': '12:35'},
                report_dates[9]: {'arrival': '08:10', 'departure': '12:25'},
                report_dates[11]: {'arrival': '08:05', 'departure': '12:20'},
            }
        },
    ]
    
    # Create data rows
    rows = create_data_rows(report_dates, sample_data)
    
    # Create the data table
    data_table = ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, TABLE_BORDER_COLOR),
        border_radius=ft.border_radius.all(8),
        vertical_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        horizontal_lines=ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        heading_row_height=80,
        data_row_min_height=60,
        data_row_max_height=80,
        divider_thickness=1,
        column_spacing=5,
    )
    
    # Put it all together in a view
    return ft.View(
        "/attendance-report",
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                "تقرير الحضور لمدة أسبوعين",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=ft.padding.symmetric(vertical=20),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            content=data_table,
                            padding=ft.padding.all(20),
                            border_radius=ft.border_radius.all(10),
                            bgcolor=ft.colors.WHITE,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                            )
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                padding=ft.padding.all(20),
            )
        ],
        padding=0,
        bgcolor="#f0f0f0",
    )


def main(page: ft.Page):
    page.title = "Attendance Report"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # Set the view
    page.views.append(create_report_days_view(page))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)