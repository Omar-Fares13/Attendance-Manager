# utils/assets.py
import os

ASSETS_DIR = "assets"

# --- Existing Icons ---
ICON_REGISTER = "icon_register.png"
ICON_MANAGE   = "icon_manage.png"
ICON_REPORT   = "icon_report.png"
ICON_COLLEGE  = "icon_college.png"
ICON_ATTENDANCE     = "icon_attendance.png"
ICON_COLLEGE_MANAGE = "icon_college_manage.png"
ICON_STUDENT_DATA   = "icon_student_data.png"
ICON_DEPARTURE      = "icon_departure.png"
ICON_ADD_STUDENT     = "icon_add_student.png"
ICON_SEARCH_STUDENT  = "icon_search_student.png"
ICON_FEMALE = "icon_female.png"
ICON_MALE   = "icon_male.png"

# --- NEW ICONS for Register Course Options page ---
ICON_TRASH          = "icon_trash.png"          # <<< Replace with your RED trash icon file
ICON_FOLDER_UPLOAD  = "icon_folder_upload.png"  # <<< Replace with your GOLD folder/upload icon file
ICON_CAMERA_QR      = "icon_camera_qr.png"      # <<< Replace with your DARK camera/QR icon file
# ---

# Required assets lists
CORE_ASSETS = ["camo.png", "logo.png", "Cairo-Regular.ttf"]
DASHBOARD_ASSETS = [ICON_REGISTER, ICON_MANAGE, ICON_REPORT, ICON_COLLEGE]
MANAGE_COURSE_ASSETS = [ICON_ATTENDANCE, ICON_COLLEGE_MANAGE, ICON_STUDENT_DATA]
ATTENDANCE_PAGE_ASSETS = [ICON_DEPARTURE]
MANAGE_STUDENTS_ASSETS = [ICON_ADD_STUDENT, ICON_SEARCH_STUDENT]
REGISTER_COURSE_ASSETS = [ICON_FEMALE, ICON_MALE]
# --- NEW ASSETS LIST ---
REGISTER_OPTIONS_ASSETS = [ICON_TRASH, ICON_FOLDER_UPLOAD, ICON_CAMERA_QR]
# Combine all unique assets needed
ALL_REQUIRED_ASSETS = list(set(
    CORE_ASSETS +
    DASHBOARD_ASSETS +
    MANAGE_COURSE_ASSETS +
    ATTENDANCE_PAGE_ASSETS +
    MANAGE_STUDENTS_ASSETS +
    REGISTER_COURSE_ASSETS +
    REGISTER_OPTIONS_ASSETS # Add the new list
))
# ---

def asset_path(fname):
    """Constructs the absolute path to an asset file relative to the project root."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    return os.path.join(project_root, ASSETS_DIR, fname)

def check_assets():
    """Checks if all required assets exist."""
    missing_files = []
    assets_dir_path = os.path.dirname(asset_path(""))
    if not os.path.isdir(assets_dir_path):
         print(f"Error: Assets directory '{ASSETS_DIR}' not found at expected location: {assets_dir_path}")
         return False, [f"Directory '{ASSETS_DIR}'"]

    for f in ALL_REQUIRED_ASSETS:
        full_path = asset_path(f)
        if not os.path.exists(full_path):
            missing_files.append(f)

    if missing_files:
        print(f"Error: One or more required files missing from '{ASSETS_DIR}':")
        for f in missing_files:
             print(f" - {f} (Expected at: {asset_path(f)})")
        return False, missing_files
    else:
        print("All required assets found.")
        return True, []

def ft_asset(fname):
    return fname