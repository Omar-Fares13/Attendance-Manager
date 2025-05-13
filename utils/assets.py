"""
Asset management utilities for handling application resources.
Provides functions for path resolution and asset verification
that work in both development and bundled environments.
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple, Union


# Function to determine the correct assets directory path
def get_assets_dir() -> str:
    """
    Determine the correct assets directory path based on execution context.
    Works in both development mode and when bundled with PyInstaller.
    
    Returns:
        str: Absolute path to the assets directory
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # When running as bundled app
        base_dir = Path(sys._MEIPASS)
    else:
        # In development mode - resolve from this file's location
        base_dir = Path(__file__).parent.parent
    
    return str(base_dir / "assets")


# Define assets directory
ASSETS_DIR = get_assets_dir()


# --- Icon Constants ---
# Dashboard Icons
ICON_REGISTER = "icon_register.png"
ICON_MANAGE = "icon_manage.png"
ICON_REPORT = "icon_report.png"
ICON_COLLEGE = "icon_college.png"
ICON_QR_CODE = "qr_code_pdf.png"

# Management Icons
ICON_ATTENDANCE = "icon_attendance.png"
ICON_COLLEGE_MANAGE = "icon_college_manage.png"
ICON_STUDENT_DATA = "icon_student_data.png"
ICON_DEPARTURE = "icon_departure.png"

# Student Related Icons
ICON_ADD_STUDENT = "icon_add_student.png"
ICON_SEARCH_STUDENT = "icon_search_student.png"
ICON_FEMALE = "icon_female.png"
ICON_MALE = "icon_male.png"

# File & Action Icons
ICON_TRASH = "icon_trash.png"
ICON_FOLDER_UPLOAD = "icon_folder_upload.png"
ICON_CAMERA_QR = "icon_camera_qr.png"


# --- Asset Group Definitions ---
CORE_ASSETS = ["camo.png", "logo.png", "Cairo-Regular.ttf"]
DASHBOARD_ASSETS = [ICON_REGISTER, ICON_MANAGE, ICON_REPORT, ICON_COLLEGE]
MANAGE_COURSE_ASSETS = [ICON_ATTENDANCE, ICON_COLLEGE_MANAGE, ICON_STUDENT_DATA]
ATTENDANCE_PAGE_ASSETS = [ICON_DEPARTURE]
MANAGE_STUDENTS_ASSETS = [ICON_ADD_STUDENT, ICON_SEARCH_STUDENT]
REGISTER_COURSE_ASSETS = [ICON_FEMALE, ICON_MALE]
REGISTER_OPTIONS_ASSETS = [ICON_TRASH, ICON_FOLDER_UPLOAD, ICON_CAMERA_QR]

# Combine all unique assets needed
ALL_REQUIRED_ASSETS = list(set(
    CORE_ASSETS +
    DASHBOARD_ASSETS +
    MANAGE_COURSE_ASSETS +
    ATTENDANCE_PAGE_ASSETS +
    MANAGE_STUDENTS_ASSETS +
    REGISTER_COURSE_ASSETS +
    REGISTER_OPTIONS_ASSETS
))


def asset_path(filename: str) -> str:
    """
    Construct the absolute path to an asset file.
    
    Args:
        filename: Name of the asset file (with extension)
        
    Returns:
        str: Full absolute path to the asset
    """
    return os.path.join(ASSETS_DIR, filename)


def check_assets() -> Tuple[bool, List[str]]:
    """
    Verify that all required assets exist.
    
    Returns:
        Tuple containing:
        - bool: True if all assets found, False otherwise
        - List[str]: List of missing files (empty if all found)
    """
    missing_files = []
    
    # First check if assets directory exists
    if not os.path.isdir(ASSETS_DIR):
        print(f"Error: Assets directory not found at: {ASSETS_DIR}")
        return False, [f"Directory 'assets'"]
    
    # Check each required asset
    for filename in ALL_REQUIRED_ASSETS:
        full_path = asset_path(filename)
        if not os.path.exists(full_path):
            missing_files.append(filename)
    
    # Report results
    if missing_files:
        print(f"Error: {len(missing_files)} required file(s) missing from assets directory:")
        for filename in missing_files:
            print(f" - {filename} (Expected at: {asset_path(filename)})")
        return False, missing_files
    else:
        print(f"All {len(ALL_REQUIRED_ASSETS)} required assets found.")
        return True, []


def ft_asset(filename: str) -> str:
    """
    Returns the asset path in the format needed by Flet.
    Flet needs paths relative to the assets directory.
    
    Args:
        filename: Name of the asset file (with extension)
        
    Returns:
        str: Path to asset in format needed by Flet
    """
    return filename


if __name__ == "__main__":
    # Allow this module to be run directly to check assets
    print(f"Assets directory: {ASSETS_DIR}")
    status, missing = check_assets()
    if status:
        print("✅ All assets verified successfully.")
    else:
        print(f"❌ Missing {len(missing)} assets.")
        sys.exit(1)