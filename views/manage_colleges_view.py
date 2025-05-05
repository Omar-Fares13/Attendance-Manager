# views/manage_colleges_view.py
import flet as ft
from components.banner import create_banner # Assuming your banner component is here
import functools # Import functools for partial

# --- Constants ---
PAGE_BGCOLOR = "#E3DCCC"
INPUT_BGCOLOR = ft.colors.WHITE
INPUT_BORDER_COLOR = "#B58B18" # Gold
BUTTON_BGCOLOR = "#B58B18" # Gold
BUTTON_TEXT_COLOR = ft.colors.WHITE
TEXT_COLOR_GOLD = "#B58B18" # Gold
TEXT_COLOR_DARK = "#262626" # Slightly darker text for better contrast
TEXT_COLOR_TABLE_DATA = ft.colors.BLACK # Explicitly black for table data cells
FONT_FAMILY_REGULAR = "Tajawal" # Reference the font name defined in main.py
FONT_FAMILY_BOLD = "Tajawal-Bold"
BORDER_RADIUS = 8
TABLE_ROW_TEXT = TEXT_COLOR_DARK # Ensure this contrasts well with both row colors (Used for headers)
DELETE_BUTTON_COLOR = ft.colors.RED_700
TABLE_BORDER_COLOR = ft.colors.with_opacity(0.5, ft.colors.BLACK45)
STATUS_ACTIVE_COLOR = ft.colors.GREEN_700
STATUS_INACTIVE_COLOR = ft.colors.GREY_500
CHIP_BG_ACTIVE = ft.colors.with_opacity(0.1, ft.colors.GREEN_100)
CHIP_BG_INACTIVE = ft.colors.with_opacity(0.1, ft.colors.GREY_100)
SEARCH_ICON_COLOR = "#6B6B6B" # Greyish color for search icon

class ManageCollegesState:
    def __init__(self, page: ft.Page):
        self.page = page # Store page reference if needed for updates elsewhere
        self.search_term = "" # State to hold the current search term

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
            expand=2
        )
        self.college_code_field = ft.TextField(
            label="رمز الكلية",
            text_align=ft.TextAlign.RIGHT,
            bgcolor=INPUT_BGCOLOR,
            border_color=INPUT_BORDER_COLOR,
            border_radius=BORDER_RADIUS,
            border_width=1.5,
            height=50,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            text_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR, color=TEXT_COLOR_DARK),
            label_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR),
            expand=1
        )
        self.search_field = ft.TextField(
            label="بحث بالاسم أو الرمز...",
            text_align=ft.TextAlign.RIGHT,
            bgcolor=INPUT_BGCOLOR,
            border_color=INPUT_BORDER_COLOR,
            border_radius=BORDER_RADIUS,
            border_width=1.5,
            height=50,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
            text_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR, color=TEXT_COLOR_DARK),
            label_style=ft.TextStyle(font_family=FONT_FAMILY_REGULAR),
            prefix_icon=ft.icons.SEARCH, # Add search icon inside
            # *** REMOVED: prefix_icon_color=SEARCH_ICON_COLOR, *** <--- Removed this line
            on_submit=self.search_colleges, # Allow searching by pressing Enter
            expand=True # Let search field take available space
        )

        # --- Data ---
        # Store the original full list separately
        self._all_colleges = [
            {"id": 1, "name": "كلية الهندسة", "code": "ENG", "status": "Active"},
            {"id": 2, "name": "كلية الطب", "code": "MED", "status": "Active"},
            {"id": 3, "name": "كلية التجارة", "code": "COM", "status": "Active"},
            {"id": 4, "name": "كلية الآداب", "code": "ART", "status": "Inactive"},
            {"id": 5, "name": "كلية العلوم", "code": "SCI", "status": "Active"},
        ]
        # self.colleges will hold the currently displayed (potentially filtered) list
        self.colleges = self._all_colleges[:] # Start with a copy of the full list

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
            columns=[ # Use TABLE_ROW_TEXT (dark) for headers
                ft.DataColumn(ft.Text("اسم الكلية", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.RIGHT), numeric=False),
                ft.DataColumn(ft.Text("الرمز", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.CENTER), numeric=False),
                ft.DataColumn(ft.Text("الحالة", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.CENTER), numeric=False),
                ft.DataColumn(ft.Text("إجراءات", weight=ft.FontWeight.BOLD, font_family=FONT_FAMILY_BOLD, color=TABLE_ROW_TEXT, text_align=ft.TextAlign.CENTER), numeric=False),
            ],
            rows=self.build_data_rows(), # Build initial rows
            expand=True
        )
    # --- Action Handlers ---
    def save_college(self, e):
        college_name = self.college_name_field.value.strip()
        college_code = self.college_code_field.value.strip().upper()

        is_valid = True
        if not college_name:
            self.college_name_field.error_text = "اسم الكلية مطلوب"
            is_valid = False
        else:
             self.college_name_field.error_text = None

        if not college_code:
            self.college_code_field.error_text = "رمز الكلية مطلوب"
            is_valid = False
        else:
            # Check if code already exists in the *original* list
            if any(c['code'] == college_code for c in self._all_colleges):
                 self.college_code_field.error_text = "هذا الرمز مستخدم بالفعل"
                 is_valid = False
            else:
                self.college_code_field.error_text = None

        self.college_name_field.update()
        self.college_code_field.update()

        if not is_valid:
            self.page.show_snack_bar(ft.SnackBar(ft.Text("يرجى تصحيح الأخطاء", font_family=FONT_FAMILY_REGULAR), open=True, bgcolor=ft.colors.RED_100))
            return

        print(f"Save: Name='{college_name}', Code='{college_code}'")
        # --- Simulate Saving ---
        new_id = (max(c["id"] for c in self._all_colleges) + 1) if self._all_colleges else 1
        new_college = {"id": new_id, "name": college_name, "code": college_code, "status": "Active"}
        self._all_colleges.append(new_college) # Add to the original list
        # --- End Simulation ---

        # Clear inputs and update table (which will apply current filter)
        self.college_name_field.value = ""
        self.college_code_field.value = ""
        self.update_table() # Update table will now re-filter based on search_term
        self.college_name_field.update()
        self.college_code_field.update()
        self.page.show_snack_bar(ft.SnackBar(ft.Text(f"تم حفظ الكلية: {college_name}", font_family=FONT_FAMILY_REGULAR), open=True, bgcolor=ft.colors.GREEN_100))

    def delete_college(self, e, college_id_to_delete):
        print(f"Delete requested for college ID: {college_id_to_delete}")
        college_to_delete = next((c for c in self._all_colleges if c["id"] == college_id_to_delete), None)

        if college_to_delete:
            # --- Simulate Deletion ---
            self._all_colleges = [c for c in self._all_colleges if c["id"] != college_id_to_delete] # Remove from original list
             # --- End Simulation ---
            self.update_table() # Update table will re-filter
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"تم حذف الكلية: {college_to_delete['name']}", font_family=FONT_FAMILY_REGULAR), open=True, bgcolor=ft.colors.AMBER_100))
        else:
            print(f"Error: College with ID {college_id_to_delete} not found for deletion.")
            self.page.show_snack_bar(ft.SnackBar(ft.Text("خطأ: لم يتم العثور على الكلية للحذف", font_family=FONT_FAMILY_REGULAR), open=True, bgcolor=ft.colors.RED_100))

    def search_colleges(self, e):
        """Filters the colleges based on the search field value."""
        self.search_term = self.search_field.value.strip().lower()
        print(f"Searching for: '{self.search_term}'")
        self.update_table() # Rebuild the table with the filter applied

    # --- Helper to build/update table ---
    def build_data_rows(self):
        """Builds table rows based on the current filter."""
        rows = []
        # Filter the original list based on the current search term
        if self.search_term:
            self.colleges = [
                c for c in self._all_colleges
                if self.search_term in c["name"].lower() or self.search_term in c["code"].lower()
            ]
        else:
            self.colleges = self._all_colleges[:] # No search term, show all

        for college in self.colleges: # Iterate over the potentially filtered list
            status_chip = ft.Chip(
                label=ft.Text("نشطة" if college["status"] == "Active" else "غير نشطة", font_family=FONT_FAMILY_REGULAR, size=12),
                bgcolor=CHIP_BG_ACTIVE if college["status"] == "Active" else CHIP_BG_INACTIVE,
                label_style=ft.TextStyle(color=STATUS_ACTIVE_COLOR if college["status"] == "Active" else STATUS_INACTIVE_COLOR)
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        # *** CHANGE: Set text color to TEXT_COLOR_TABLE_DATA (black) ***
                        ft.DataCell(ft.Text(college["name"], font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.RIGHT, color=TEXT_COLOR_TABLE_DATA)),
                        ft.DataCell(ft.Text(college["code"], font_family=FONT_FAMILY_REGULAR, text_align=ft.TextAlign.CENTER, color=TEXT_COLOR_TABLE_DATA)),
                        # --- End Change ---
                        ft.DataCell(ft.Container(content=status_chip, alignment=ft.alignment.center)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE,
                                        icon_color=DELETE_BUTTON_COLOR,
                                        tooltip="حذف الكلية",
                                        # Use functools.partial to pass the college ID without lambda scope issues
                                        on_click=functools.partial(self.delete_college, college_id_to_delete=college["id"])
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=0
                            )
                        ),
                    ]
                )
            )
        return rows

    def update_table(self):
        """Rebuilds and updates the DataTable rows based on current data and filter."""
        self.data_table.rows = self.build_data_rows()
        self.data_table.update()

# --- View Creation Function ---
def create_manage_colleges_view(page: ft.Page):
    """Creates the Flet View for the Manage Colleges screen using DataTable."""

    view_state = ManageCollegesState(page)

    # --- Controls ---
    banner_control = create_banner()

    page_title = ft.Container(
        content=ft.Text(
            "ادارة الكليات", # Corrected typo
            size=36,
            font_family=FONT_FAMILY_BOLD,
            color=TEXT_COLOR_GOLD,
            text_align=ft.TextAlign.CENTER
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=20, bottom=10) # Reduced bottom padding
    )

    save_button = ft.Container(
        content=ft.Text("حفظ", color=BUTTON_TEXT_COLOR, weight=ft.FontWeight.W_600, size=16, font_family=FONT_FAMILY_BOLD),
        bgcolor=BUTTON_BGCOLOR,
        border_radius=BORDER_RADIUS,
        padding=ft.padding.symmetric(horizontal=30, vertical=13),
        alignment=ft.alignment.center,
        on_click=view_state.save_college,
        tooltip="حفظ الكلية الجديدة",
        width=120,
        height=50,
    )

    # Row for adding new colleges
    add_input_row = ft.Row(
        [
            save_button,
            view_state.college_code_field,
            view_state.college_name_field,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=15
    )

    # *** NEW: Search Button *** (Using IconButton for simplicity)
    search_button = ft.IconButton(
        icon=ft.icons.SEARCH,
        icon_color=BUTTON_TEXT_COLOR,
        bgcolor=BUTTON_BGCOLOR,
        tooltip="بحث",
        on_click=view_state.search_colleges,
        height=50,
        width=55, # Make it roughly square
    )

    # *** NEW: Row for Search controls ***
    search_row = ft.Row(
        [
            search_button, # Add the search button
            view_state.search_field, # Add the search field
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=15
    )


    input_container = ft.Container(
        # Use a Column to stack add and search rows
        content=ft.Column(
            [
                add_input_row,
                ft.Divider(height=10, color=ft.colors.TRANSPARENT), # Add some space
                search_row,
            ],
            spacing=5 # Space between the two rows
        ),
        padding=ft.padding.symmetric(horizontal=50, vertical=15),
        alignment=ft.alignment.top_center, # Align content to top
    )

    table_container = ft.Container(
        content=ft.Column(
            [view_state.data_table],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        ),
        padding=ft.padding.symmetric(horizontal=50, vertical=10), # Reduced vertical padding
        expand=True
    )

    # --- Main Column Layout ---
    main_column = ft.Column(
        [
            page_title,
            input_container,
            ft.Divider(height=5, color=ft.colors.BLACK12), # Separator line
            table_container
        ],
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # --- Return the View ---
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
                spacing=0
            )
        ]
    )