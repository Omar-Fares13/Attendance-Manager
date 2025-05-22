#!/usr/bin/env python3
"""
Main entry point for the Military Education Application.
Handles routing, asset loading, and application initialization.
"""
import os
import sys
from pathlib import Path

import flet as ft

# Add the directory containing this file to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import create_db_and_tables
from utils.data_processor import check_file_integrity

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(CURRENT_DIR, 'utils/database.dat')
EXPECTED_HASH = 'f0a16c69b26b9c417b9c1457b21040b1061d7dbf3238c1fbcde2028d588ba8cd'

check_file_integrity(FILENAME, EXPECTED_HASH)

# --- Handle asset path resolution (compatible with PyInstaller) ---
def get_asset_dir():
    """Get the assets directory path, handling both development and bundled modes."""
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as bundled executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development mode
        base_path = Path(__file__).parent
    
    assets_dir = base_path / "assets"
    return str(assets_dir)

# Define asset utility functions
ASSETS_DIR = get_asset_dir()

def asset_path(relative_path):
    """Get absolute path to an asset file."""
    return os.path.join(ASSETS_DIR, relative_path)

def ft_asset(relative_path):
    """Get asset path in format needed by Flet."""
    return relative_path

def check_assets():
    """Verify that required assets exist."""
    # This is a placeholder - implement your asset checking logic
    # based on your application's requirements
    required_assets = ["Cairo-Regular.ttf"]
    missing = []
    
    for asset in required_assets:
        if not os.path.exists(asset_path(asset)):
            missing.append(asset)
    
    return len(missing) == 0, missing

# Override imported functions with our definitions if necessary
try:
    from utils.assets import check_assets as utils_check_assets
    # We're using our local definitions instead
except ImportError:
    print("Note: utils.assets module not imported, using built-in asset utilities.")

# Print the assets directory to verify
print(f"Looking for assets in: {ASSETS_DIR}")

# Create assets directory if it doesn't exist
if not os.path.isdir(ASSETS_DIR):
    print(f"WARNING: Assets directory '{ASSETS_DIR}' not found.")
    try:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        print(f"Created missing assets directory at {ASSETS_DIR}")
    except Exception as e:
        print(f"Failed to create assets directory: {e}")
        sys.exit(1)

# --- Import View Creation Functions ---
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
from views.report_course_view import create_report_course_view
from views.main_screen_view import create_main_screen_view
from views.manage_colleges_view import create_manage_colleges_view
from views.upload_course_file_view import create_upload_course_file_view
from views.add_student_view import create_add_student_view
from views.qr_search_view import create_qr_search_student_view
from views.qr_display_view import create_qr_display_view
from views.edit_course_data_view import create_edit_course_data_view
from views.delete_all_confirmation_view import create_delete_confirmation_view
from views.setup_view import create_setup_view
from views.report_view import create_report_view
from views.report_view_days import create_report_alt_view
from views.add_note_view import create_add_note_view
from views.mark_attendance_departure_view import (
    create_attendance_mark_view,
    create_departure_mark_view
)
from views.add_student_barcode_view import create_add_student_barcode_view

# Import reusable components
try:
    from components.banner import create_banner
except ImportError:
    print("WARNING: Could not import banner component. Using placeholder.")
    def create_banner(width):
        return ft.Container(
            content=ft.Text("Banner Placeholder"), 
            bgcolor=ft.colors.BLUE_GREY, 
            height=50, 
            padding=10
        )


def main(page: ft.Page):
    """Main application function that sets up the page and handles routing."""
    # ─── Global Page Setup ────────────────────────────────────
    page.title = "التربية العسكرية"  # App title
    page.window_width = 1200
    page.window_height = 850
    page.window_min_width = 800
    page.window_min_height = 600
    page.window_resizable = True
    page.padding = 0
    page.bgcolor = "#E3DCCC"
    page.rtl = True  # Right-to-Left layout
    
    # --- Load Font ---
    font_path = asset_path("Cairo-Regular.ttf")
    if os.path.exists(font_path):
        page.fonts = {"Cairo": ft_asset("Cairo-Regular.ttf")}
        page.theme = ft.Theme(font_family="Cairo")
        print("Cairo font loaded and RTL theme set.")
    else:
        print(f"Warning: Font file not found at {font_path}. Using default font.")

    def parse_route(route_string):
        """Parse route and extract query parameters."""
        route_parts = route_string.split("?")
        route = route_parts[0]
        params = {}
        
        if len(route_parts) > 1:
            param_string = route_parts[1]
            param_pairs = param_string.split('&')
            
            for pair in param_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key] = value
        
        return route, params

    def route_change(event: ft.RouteChangeEvent):
        """Handle navigation between different views/pages."""
        route_string = event.route
        print(f"Route changing to: {route_string}")
        
        # Clear current view stack
        page.views.clear()
        
        # Parse route and extract any query parameters
        route, params = parse_route(route_string)
        
        # Route mapping - Each route corresponds to a view creation function
        route_map = {
            "/": create_login_view,
            "/login": create_login_view,
            "": create_login_view,
            "/dashboard": create_dashboard_view,
            "/colleges": create_manage_colleges_view,
            "/manage_course": create_manage_course_view,
            "/register_course_options": create_register_course_options_view,
            "/delete_all_data": create_delete_confirmation_view,
            "/register_course": create_register_course_view,
            "/attendance": create_attendance_view,
            "/mark_attendance": create_attendance_mark_view,
            "/mark_departure": create_departure_mark_view,
            "/add_note": create_add_note_view,
            "/manage_students": create_manage_students_view,
            "/search_student": create_search_student_view,
            "/edit_student": create_edit_student_view,
            "/report": create_report_view,
            "/report_alt": create_report_alt_view,
            "/camera_qr": create_camera_qr_view,
            "/course_file_upload": create_upload_course_file_view,
            "/report_course": create_report_course_view,
            "/qr_display": create_qr_display_view,
            "/main_screen": create_main_screen_view,
            "/add_student": create_add_student_view,
            "/search_qr_student": create_qr_search_student_view,
            "/add_student_barcode": create_add_student_barcode_view,
            "/edit_course_data": create_edit_course_data_view,
            "/setup": create_setup_view,
        }
        
        # Get the view creation function or default to login view
        view_creator = route_map.get(route)
        
        if view_creator:
            # For views that might need query parameters
            if route == "/add_note" and "student_id" in params:
                page.views.append(view_creator(page, student_id=params["student_id"]))
            elif route == "/edit_student" and "student_id" in params:
                page.views.append(view_creator(page, student_id=params["student_id"]))
            else:
                page.views.append(view_creator(page))
        else:
            print(f"Unknown route: {route}, redirecting to login.")
            page.views.append(create_login_view(page))
        
        # Ensure at least one view is present (fallback)
        if not page.views:
            print("Warning: No view was added. Adding login view as fallback.")
            page.views.append(create_login_view(page))

        page.update()

    def view_pop(event: ft.ViewPopEvent):
        """Handle back navigation (e.g., OS back button, swipe gesture)."""
        print("View pop triggered (User went back)")
        
        if len(page.views) <= 1:
            print("Cannot pop the last view. Preventing pop.")
            return
        
        page.views.pop()
        top_view = page.views[-1]
        print(f"Popped view, going back to: {top_view.route}")
        page.go(top_view.route)

    # Assign event handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start at the main screen
    page.go("/main_screen")


if __name__ == "__main__":
    # Initialize database
    create_db_and_tables()
    
    # Check if assets directory exists and contains required files
    if not os.path.isdir(ASSETS_DIR):
        print(f"ERROR: Assets directory '{ASSETS_DIR}' not found or could not be created.")
        print("Application cannot start without the assets directory.")
        sys.exit(1)
    
    # Verify required assets
    assets_ok, missing_assets = check_assets()
    if not assets_ok:
        print(f"WARNING: Missing required assets: {missing_assets}")
        print("The application may not function correctly without these files.")
    
    # Start the application
    print(f"Starting Flet app with assets_dir='{ASSETS_DIR}'")
    ft.app(
        target=main,
        assets_dir=ASSETS_DIR
    )