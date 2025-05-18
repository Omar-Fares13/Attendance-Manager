# views/report_view.py

import flet as ft
import math
from logic.students import create_students_from_file
from components.banner import create_banner
from logic.file_write import get_student_data, create_excel, setup_file_picker

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

FONT_FAMILY_REGULAR = "Tajawal"
FONT_FAMILY_BOLD = "Tajawal-Bold"

attribs = {}

content_ref = ft.Ref[ft.Column]()


def create_uneditable_cell(value: str, ref: ft.Ref[ft.TextField]):
    return ft.Text(
        value=value,
        text_align=ft.TextAlign.RIGHT,
        size=14,
        font_family=FONT_FAMILY_REGULAR,
        color=TEXT_COLOR_DARK,
        overflow=ft.TextOverflow.ELLIPSIS,
        no_wrap=True
    )


def create_report_view(page: ft.Page):
    # -------------------------------------------------------------
    # 1) ORIGINAL DATA FETCH
    # -------------------------------------------------------------
    headers     = ["م", "الاسم", "الرقم القومي", "الكلية",
                   "انذارات", "حضور", "غياب", "الحالة", "ملاحظات"]
    all_rows_raw = get_student_data(
        page.course_id, page.faculty_id
    )
    all_rows_raw = [row[:] for row in all_rows_raw]   # local copy

    # -------------------------------------------------------------
    # 2) PAGINATION SETTINGS
    # -------------------------------------------------------------
    rows_per_page = 30                                     # tweak as you like
    page_index    = 0                                      # zero-based
    total_pages   = max(1, math.ceil(len(all_rows_raw) / rows_per_page))

    def slice_rows(idx: int):
        start = idx * rows_per_page
        end   = start + rows_per_page
        return all_rows_raw[start:end]

    # -------------------------------------------------------------
    # 3) BUILD STATIC PARTS –   DataColumns
    # -------------------------------------------------------------
    dt_columns = [
        ft.DataColumn(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=10),
                alignment=ft.alignment.center_right,
                content=ft.Text(
                    header_text,
                    color=TEXT_COLOR_HEADER,
                    weight=ft.FontWeight.BOLD,
                    size=14,
                    font_family=FONT_FAMILY_BOLD,
                    text_align=ft.TextAlign.RIGHT,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            )
        ) for header_text in headers
    ]

    # -------------------------------------------------------------
    # 4) Helper to PRODUCE DataRow objects for ONE page
    # -------------------------------------------------------------
    def build_dt_rows(raw_rows):
        refs = [[ft.Ref[ft.TextField]() for _ in headers] for _ in raw_rows]
        dtr = []
        for r_idx, row_data in enumerate(raw_rows):
            cells = [
                ft.DataCell(create_uneditable_cell(cell_value, refs[r_idx][c_idx]))
                for c_idx, cell_value in enumerate(row_data)
            ]
            dtr.append(ft.DataRow(cells=cells, color=TABLE_CELL_BG))
        return dtr

    # -------------------------------------------------------------
    # 5) INITIAL TABLE – with the first slice
    # -------------------------------------------------------------
    data_table = ft.DataTable(
        columns      = dt_columns,
        rows         = build_dt_rows(slice_rows(page_index)),
        border       = ft.border.all(1, TABLE_BORDER_COLOR),
        border_radius= ft.border_radius.all(8),
        vertical_lines   = ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        horizontal_lines = ft.border.BorderSide(1, TABLE_BORDER_COLOR),
        sort_ascending   = True,
        heading_row_color= TABLE_HEADER_BG,
        heading_row_height = 50,
        data_row_max_height= 50,
        divider_thickness  = 0,
        horizontal_margin  = 10,
        show_checkbox_column= False,
    )

    # -------------------------------------------------------------
    # 6) PAGINATION CONTROLS (Prev, Page#, Next)
    # -------------------------------------------------------------
    page_lbl = ft.Text(f"{page_index+1} / {total_pages}",
                       weight=ft.FontWeight.BOLD, size=16)

    def refresh():
        nonlocal page_index
        page_index = max(0, min(page_index, total_pages-1))
        data_table.rows = build_dt_rows(slice_rows(page_index))
        page_lbl.value  = f"{page_index+1} / {total_pages}"
        page.update()

    def prev_page(e):
        nonlocal page_index
        if page_index > 0:
            page_index -= 1
            refresh()

    def next_page(e):
        nonlocal page_index
        if page_index < total_pages-1:
            page_index += 1
            refresh()

    nav_bar = ft.Row(
        [
            ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="السابق",
                          on_click=prev_page),
            page_lbl,
            ft.IconButton(icon=ft.icons.CHEVRON_LEFT,  tooltip="التالي",
                          on_click=next_page),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # -------------------------------------------------------------
    # 7) REMAINDER OF ORIGINAL VIEW  (back button, excel button…)
    # -------------------------------------------------------------
    def go_back(e): page.go("/report_course")

    def extract_pdf(e): print("pdf")

    def extract_xlsx(e):
        failing = [row for row in all_rows_raw if row[-2] == "راسب"]
        passing = [row for row in all_rows_raw if row[-2] != "راسب"]
        sorted_data = failing + passing
        summary = ["-" for _ in headers]
        summary[-2] = f"إجمالي الراسب: {len(failing)} | إجمالي الناجح: {len(passing)}"
        setup_file_picker(page, page.course_name, headers, [summary] + sorted_data)

    back_button = ft.IconButton(icon=ft.icons.ARROW_FORWARD_OUTLINED,
                                icon_color=PRIMARY_COLOR,
                                tooltip="العودة",
                                on_click=go_back,
                                icon_size=30)

    title = ft.Text("تقرير", size=32, weight=ft.FontWeight.BOLD,
                    color=PRIMARY_COLOR, font_family=FONT_FAMILY_BOLD,
                    text_align=ft.TextAlign.CENTER)

    pdf_button = ft.ElevatedButton(
        text="استخراج ملف PDF",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50, width=220,
        on_click=extract_pdf,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    excel_button = ft.ElevatedButton(
        key="confirm_section",
        text="استخراج ملف Excel",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=BUTTON_CONFIRM_COLOR,
        color=BUTTON_TEXT_COLOR,
        height=50, width=220,
        on_click=extract_xlsx,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    scroll_down_fab = ft.FloatingActionButton(
        icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
        tooltip="اذهب إلى الأسفل",
        on_click=lambda e: content_ref.current.scroll_to(
            key="confirm_section", duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )
    )

    banner_control = create_banner()

    # -------------------------------------------------------------
    # 8) LAYOUT
    # -------------------------------------------------------------
    content_column = ft.Column(
        [
            ft.Container(ft.Row([back_button],
                                alignment=ft.MainAxisAlignment.START),
                         padding=ft.padding.only(top=15, left=30, right=30)),
            ft.Container(title,
                         padding=ft.padding.symmetric(horizontal=30),
                         alignment=ft.alignment.center),

            # main table
            data_table,

            # pagination bar
            nav_bar,

            ft.Container(height=30),

            ft.Row([excel_button], alignment=ft.MainAxisAlignment.CENTER),

            ft.Container(height=30),
        ],
        ref=content_ref,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=20
    )

    return ft.View(
        route="/report",
        bgcolor=BG_COLOR,
        floating_action_button=scroll_down_fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
        padding=0,
        controls=[
            ft.Column(
                [
                    banner_control,
                    ft.Container(content=content_column,
                                 expand=True,
                                 padding=ft.padding.only(
                                     left=30, right=30, bottom=20))
                ],
                expand=True,
                spacing=0
            )
        ]
    )