# main.py
import flet as ft
import os

# --- Import View Creation Functions ---
# (Make sure all these files exist in your 'views' folder
#  and views/__init__.py exists)
from views.login_view import create_login_view
from views.dashboard_view import create_dashboard_view
from views.manage_course_view import create_manage_course_view
from views.attendance_view import create_attendance_view
from views.manage_students_view import create_manage_students_view
from views.search_student_view import create_search_student_view
from views.edit_student_view import create_edit_student_view
from views.register_course_view import create_register_course_view
from views.register_course_options_view import create_register_course_options_view
from views.camera_qr_view import create_camera_qr_view
from views.qr_display_view import create_qr_display_view
from views.report_course_view import create_report_course_view
from views.main_screen_view import create_main_screen_view
from views.manage_colleges_view import create_manage_colleges_view
from views.upload_course_file_view import create_upload_course_file_view
from views.add_student_view import create_add_student_view
from views.qr_search_view import create_qr_search_student_view
# --- Import the Attendance/Departure Mark Views ---
from views.mark_attendance_departure_view import (
    create_attendance_mark_view,
    create_departure_mark_view
)

# --- Import the new Add Note View ---
from views.add_note_view import create_add_note_view # <<< ADD THIS IMPORT


# --- Import Asset Utilities ---
# (Make sure 'utils/assets.py' exists)
try:
    from utils.assets import ASSETS_DIR, asset_path, check_assets, ft_asset
except ImportError:
    print("ERROR: Could not import from utils.assets. Make sure utils/assets.py exists.")
    # Define dummy functions/variables to prevent further crashes during import phase
    ASSETS_DIR = "assets"
    def asset_path(p): return os.path.join(ASSETS_DIR, p)
    def check_assets(): print("Warning: Asset check skipped due to import error."); return True, []
    def ft_asset(p): return p # Flet needs relative path from assets_dir
    # Exit if assets are critical - depends on your app structure
    # import sys
    # sys.exit(1)


# --- Import Reusable Components ---
# (Make sure 'components/banner.py' exists)
try:
    from components.banner import create_banner
except ImportError:
    print("ERROR: Could not import from components.banner. Make sure components/banner.py exists.")
    # Define a dummy banner if needed
    def create_banner(width): return ft.Container(content=ft.Text("Banner Placeholder"), bgcolor=ft.colors.BLUE_GREY, height=50, padding=10)
    # import sys
    # sys.exit(1)


# === Main Application Function ===
def main(page: ft.Page):
    # ─── Global Page Setup ────────────────────────────────────
    page.title = "التربية العسكرية" # App title
    # Set initial window size instead of forcing full screen immediately
    page.window_width = 1200
    page.window_height = 850 # Adjusted height slightly
    page.window_min_width = 800  # Optional: Minimum size
    page.window_min_height = 600 # Optional: Minimum size
    # page.window_full_screen = True   # Start in full screen - Can be less user-friendly
    page.window_resizable = True     # Allow resizing
    page.padding = 0                 # No padding around the edges of the window
    page.bgcolor = "#E3DCCC"         # Default background color for all views
    page.rtl = True                  # <<< SET Right-to-Left layout globally

    # --- Load Font ---
    # Construct the full path to the font file
    font_full_path = asset_path("Cairo-Regular.ttf") # Make sure this font is in assets folder
    if os.path.exists(font_full_path):
        # Use ft_asset for Flet to find the font within the assets directory
        page.fonts = {"Cairo": ft_asset("Cairo-Regular.ttf")}
        page.theme = ft.Theme(font_family="Cairo")
        print("Cairo font loaded and RTL theme set.")
    else:
        print(f"Warning: Font file not found at {font_full_path}. Using default font.")

    # ─── Routing Logic ────────────────────────────────────────
    def route_change(route: ft.RouteChangeEvent): # Use specific event type hinting
        """Handles navigation between different views/pages."""
        target_route = route.route # Get the route from the event object
        print(f"Route changing to: {target_route}") # Log the requested route
        page.views.clear() # Remove the current view(s) from the stack

        # --- Optional: Extract base route and query parameters if needed ---
        # Example: route could be "/add_note?student_id=123"
        route_parts = target_route.split("?")
        actual_route = route_parts[0]
        # query_params = {}
        # if len(route_parts) > 1:
        #     params = route_parts[1].split('&')
        #     for param in params:
        #         key_value = param.split('=')
        #         if len(key_value) == 2:
        #             query_params[key_value[0]] = key_value[1]
        # print(f"Actual route: {actual_route}, Params: {query_params}")


        # --- Add Views based on the actual route (ignoring params for now) ---
        # Login/Default Route (often checked first)
        if actual_route == "/" or actual_route == "/login" or actual_route == "" or "/login/" in actual_route:
             try:
                 page.views.append(create_login_view(page))
             except NameError:
                 print("ERROR: create_login_view is not defined. Check import.")
                 page.views.append(ft.View("/", [ft.Text("Error: Login View Missing")]))

        # Dashboard
        elif actual_route == "/dashboard":
            page.views.append(create_dashboard_view(page))


        # Colleges
        elif actual_route == '/colleges':
            page.views.append(create_manage_colleges_view(page))

        # Course Management
        elif actual_route == "/manage_course":
            page.views.append(create_manage_course_view(page))
        elif actual_route == "/register_course_options":
             page.views.append(create_register_course_options_view(page))
        elif actual_route == "/register_course":
             page.views.append(create_register_course_view(page))

        # Attendance Flow
        elif actual_route == "/attendance":
            page.views.append(create_attendance_view(page))
        elif actual_route == "/mark_attendance":
            page.views.append(create_attendance_mark_view(page))
        elif actual_route == "/mark_departure":
            page.views.append(create_departure_mark_view(page))
        elif actual_route == "/add_note":                 # <<< ADD THIS ROUTE
            # TODO: If you passed student_id via query params, retrieve it here:
            # student_id = query_params.get("student_id")
            # page.views.append(create_add_note_view(page, student_id=student_id)) # Pass it to the view function
            page.views.append(create_add_note_view(page)) # <<< CALL NEW VIEW FUNCTION


        # Student Management
        elif actual_route == "/manage_students":
            page.views.append(create_manage_students_view(page))
        elif actual_route == "/search_student":
            page.views.append(create_search_student_view(page))
        # Example route with parameter (Needs adjustment in view logic too)
        # elif actual_route.startswith("/edit_student/"): # If using path params like /edit_student/123
        #      student_id = actual_route.split('/')[-1] # Get ID from route
        #      page.views.append(create_edit_student_view(page, student_id)) # Pass ID
        elif actual_route == "/edit_student": # Assuming generic route for now
             page.views.append(create_edit_student_view(page))

        # QR Code Flow
        elif actual_route == "/camera_qr":
            page.views.append(create_camera_qr_view(page))
        elif actual_route == "/qr_display":
            page.views.append(create_qr_display_view(page))
        
        # File upload
        elif actual_route == "/course_file_upload":
            page.views.append(create_upload_course_file_view(page))

        # Reporting
        elif actual_route == "/report_course":
            page.views.append(create_report_course_view(page))
        elif actual_route == "/main_screen":
            page.views.append(create_main_screen_view(page))
        elif actual_route == "/add_student":
            page.views.append(create_add_student_view(page))
        elif actual_route == '/search_qr_student':
            page.views.append(create_qr_search_student_view(page))
        # --- Unknown Route Handling ---
        else:
             print(f"Unknown route: {target_route}, redirecting to login.")
             page.views.append(create_login_view(page)) # Go to login for safety
             
        # --- Ensure at least one view is present (fallback) ---
        if not page.views:
            print("Warning: No view was added for the route. Adding Login view as fallback.")
            try:
                 page.views.append(create_login_view(page))
            except NameError:
                  page.views.append(ft.View("/", [ft.Text("Error: Login View Missing")]))

        page.update() # Refresh the page to show the new view

    def view_pop(view_event: ft.ViewPopEvent): # Use specific event type hinting
        """Handles the user going back (e.g., OS back button, swipe gesture)."""
        print("View pop triggered (User went back)")
        if len(page.views) <= 1:
            print("Cannot pop the last view. Preventing pop.")
            # Optionally close the app or do nothing
            # page.window_close()
            return # Prevent Flet's default pop which might close app

        page.views.pop() # Remove the top view from the stack
        top_view = page.views[-1]
        print(f"Popped view, going back to: {top_view.route}")
        page.go(top_view.route) # Manually trigger route change to the previous view

    # Assign the handlers to the page events
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- Global Resize Handler (Optional - kept simple) ---
    def on_resize(e=None):
        pass # No action on resize for now

    page.on_resize = on_resize

    # ─── Initial Route ────────────────────────────────────────
    print("Starting app, navigating to initial route '/' ...")
    # Start at the root, route_change will handle displaying the login view
    page.go("/main_screen")


# --- Run the App Entry Point ---
if __name__ == "__main__":
    # First, check if the assets directory itself exists
    if not os.path.isdir(ASSETS_DIR):
         print(f"ERROR: Assets directory '{ASSETS_DIR}' not found.")
         print("Application cannot start without the assets directory.")
    else:
        # Proceed with asset check only if directory exists
        assets_ok, _ = check_assets()
        if assets_ok:
            print(f"Starting Flet app with assets_dir='{ASSETS_DIR}'")
            ft.app(
                target=main,
                assets_dir=ASSETS_DIR # Ensure this points correctly to your assets folder
            )
        else:
            print("\nApplication cannot start due to missing assets. Please fix the issues listed above.")