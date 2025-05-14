# views/qr_display_view.py
# This file defines the view for the '/qr_display' route,
# displaying student data, QR code, and handling registration confirmation
# with a confetti overlay.

import flet as ft
import os
import time # Used for the delay during the confetti overlay
from datetime import date, datetime
from typing import Optional
from logic.course import get_all_courses

# --- Asset and Banner Utilities ---
# Attempt to import from relative paths first (standard project structure)
try:
    from ..components.banner import create_banner
    from ..utils.assets import ft_asset
except (ImportError, ValueError):
    # Fallback if running standalone or structure differs
    print("WARN: Could not import from relative paths. Trying direct imports/placeholders.")
    try:
        from components.banner import create_banner
        from utils.assets import ft_asset
    except ImportError:
        print("ERROR: Failed to import components/utils. Using basic placeholders.")
        # Basic placeholder for the banner
        def create_banner(page_width):
            logo_path = 'assets/logo.png'
            logo_exists = os.path.exists(logo_path)
            print(f"Placeholder Banner: Logo exists at '{logo_path}'? {logo_exists}")
            return ft.Container(
                content=ft.Row([
                    ft.Image(src=logo_path if logo_exists else '', height=40, error_content=ft.Text("Logo?")),
                    ft.Text("التربية العسكرية - جامعة عين شمس", color=ft.colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                height=60,
                bgcolor="#5C544A", # Dark Grey matching screenshot banner BG
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            )
        # Basic placeholder for the asset path helper
        def ft_asset(path):
            # Simple check in current dir/assets subdir
            if os.path.exists(path):
                return path
            # Check relative assets dir commonly used in projects
            rel_path = os.path.join("..", path)
            if os.path.exists(rel_path):
                 return rel_path # Return ../assets/file.png format
            print(f"Warning: Asset fallback couldn't find {path} or {rel_path}")
            return path # Return original path if not found

def retrieve_verification_data():
    try:
        results = get_all_courses()
        return [course.start_date for course in results]
    except Exception:
        return []

# --- Reusable Helper for Data Rows ---
def create_data_row(label: str, value: str):
    """Creates a consistently styled Row for displaying a label and value (RTL friendly)."""
    return ft.Row(
        [
            # Value (appears right in RTL)
            ft.Text(
                value,
                text_align=ft.TextAlign.RIGHT,
                weight=ft.FontWeight.W_500,
                size=14,
                color=ft.colors.BLACK87,
                selectable=True, # Allow copying data
            ),
            # Label (appears left in RTL)
            ft.Text(
                label,
                text_align=ft.TextAlign.RIGHT, # Text alignment within its own box
                weight=ft.FontWeight.BOLD,
                size=14,
                color="#B58B18", # Gold color from screenshot
            ),
        ],
        alignment=ft.MainAxisAlignment.END, # Align content to the right for RTL
        spacing=5, # Small space between label and value
    )

def format_system_date(date_value):
    if isinstance(date_value, date):
        print(date_value.strftime("%Y-%m-%d"))
        return date_value.strftime("%Y-%m-%d")
    return None

# --- Success Confetti Overlay Function ---
def show_confetti_overlay(page: ft.Page):
    """Displays a temporary confetti overlay upon successful registration."""
    confetti_gif_asset_path = "assets/confetti.gif" # Expected location
    confetti_gif_resolved_path = ft_asset(confetti_gif_asset_path)
    confetti_gif_exists = os.path.exists(confetti_gif_resolved_path.split('?')[0]) # Check file existence

    print(f"Confetti Check: Path='{confetti_gif_asset_path}', Resolved='{confetti_gif_resolved_path}', Exists={confetti_gif_exists}")

    if confetti_gif_exists:
        confetti_visual = ft.Image(
            src=confetti_gif_resolved_path, # Use resolved path
            width=350, # Adjust size for visual impact
            height=350,
            fit=ft.ImageFit.CONTAIN,
        )
    else:
        # Fallback if GIF is missing
        print(f"ERROR: Confetti GIF not found at '{confetti_gif_resolved_path}'. Using fallback icon.")
        confetti_visual = ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=ft.colors.GREEN_ACCENT_700, size=120)

    # Success Text - styled for overlay
    success_text = ft.Text(
        "تم التسجيل بنجاح!",
        size=24, # Larger text
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE, # White text contrasts well with dark overlay
        text_align=ft.TextAlign.CENTER
    )

    # Stack the confetti/icon and text vertically
    content_column = ft.Column(
        [
            confetti_visual,
            ft.Container(height=15), # Space between visual and text
            success_text,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # The main overlay container - fills the screen
    overlay_container = ft.Container(
        content=content_column,
        alignment=ft.alignment.center,
        # Semi-transparent dark background
        bgcolor=ft.colors.with_opacity(0.7, ft.colors.BLACK87),
        expand=True, # Fill the available space
        opacity=0, # Start fully transparent for fade-in effect
        animate_opacity=ft.animation.Animation(400, ft.AnimationCurve.EASE_OUT), # Fade-in animation
    )

    # Add the overlay to the page's overlay layer
    page.overlay.append(overlay_container)
    page.update()

    # Slight delay before starting animation allows elements to render
    time.sleep(0.05)
    overlay_container.opacity = 1 # Trigger the fade-in
    page.update()

def get_validation_key():
    try:
        date_values = retrieve_verification_data()
        return [format_system_date(date_value) for date_value in date_values if date_value]
    except Exception:
        return []

# --- Main View Creation Function ---
def create_qr_display_view(page: ft.Page):
    """Creates the Flet View for the QR Display screen."""

    # Remind developer if RTL is not set in the main application
    if not page.rtl:
       print("WARNING: page.rtl is not True in create_qr_display_view. Ensure it's set globally for correct Arabic layout.")

    # --- Navigation Function ---
    def go_back(e):
        """Handles navigating back using either the top or bottom back buttons."""
        page.go("camera_qr")
    # --- Top-Left Back Button ---
    back_button_page = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED, # Icon points left in RTL mode
        icon_color="#B58B18", # Gold accent color
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    # --- Left Panel: Student Data Display ---
    # !! Replace placeholder data with dynamic data passed to the view !!
    student_data_column = ft.Column(
        spacing=8, # Space between data rows
        controls=[
            # Centered Title
            ft.Row(
                [ft.Text("بيانات الطالب", size=18, weight=ft.FontWeight.BOLD, color="#B58B18")],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Divider(height=1, color=ft.colors.with_opacity(0.5, "#B58B18")), # Subtle divider
            # Example Data Rows (use create_data_row helper)
            create_data_row("الاسم:", "محمد محمد محمد"),
            create_data_row("ID الطالب:", "123456"),
            create_data_row("الرقم القومي:", "12345678901234"),
            create_data_row("الكلية:", "الهندسة"),
            create_data_row("مسلسل:", "123"),
            create_data_row("ملاحظات:", "واحد اثنان ثلاثة اربعة خمسة ستة سبعة"), # Example longer text
        ]
    )

    left_panel = ft.Container(
        content=student_data_column,
        bgcolor=ft.colors.WHITE, # White background inside panel
        border=ft.border.all(2, "#B58B18"), # Gold border
        border_radius=12, # Rounded corners
        padding=ft.padding.all(15), # Internal padding
    )

    # --- Right Panel: QR Code Display ---
    # !! Replace placeholder QR code with dynamically generated one !!
    qr_code_image_container = ft.Container(
        content=ft.Image(
            src=ft_asset("assets/QR.png"), # Path to the QR code image
            fit=ft.ImageFit.CONTAIN, # Ensure QR code fits without distortion
            error_content=ft.Text("خطأ في تحميل QR", color=ft.colors.RED) # Error display
        ),
        bgcolor=ft.colors.WHITE, # White background inside panel
        alignment=ft.alignment.center, # Center the QR code image
        border=ft.border.all(2, "#B58B18"), # Gold border
        border_radius=12, # Rounded corners
        padding=20, # Padding around the QR code
        expand=True # Allow this panel to take available vertical space
    )

    # --- Confirmation Dialog Logic ---
    def close_dialog(e):
        """Closes the currently open confirmation dialog."""
        if page.dialog:
            page.dialog.open = False
            page.update()

    def confirm_end_registration(e):
        """Handles actions after the user confirms ending registration."""
        print("Confirmation received. Closing dialog and showing confetti...")
        close_dialog(None) # Close the confirmation dialog

        # Show the celebratory confetti overlay
        show_confetti_overlay(page)

        # Define how long the confetti should display
        confetti_display_duration = 2.8 # Seconds (adjust based on GIF length)
        print(f"Waiting {confetti_display_duration}s for confetti...")
        time.sleep(confetti_display_duration) # Pause execution (blocks UI thread)

        # Clean up the overlay
        if page.overlay:
             print("Clearing overlay...")
             # Optional: Add fade-out animation before clearing
             # page.overlay[0].opacity = 0
             # page.update()
             # time.sleep(0.4) # Wait for fade out
             page.overlay.clear() # Remove the overlay container
             page.update()
        else:
             print("Overlay already cleared.") # Should not happen normally

        # --- Perform Actual Backend/State Update ---
        print("Performing 'End Registration' backend logic...")
        # !! IMPORTANT: Add your logic here to finalize the registration !!
        # (e.g., update database, clear temporary state)

        # --- Navigate to the Next Appropriate Screen ---
        next_route = "/register_course_options" # Or maybe a "registration complete" screen
        page.go(next_route)
        print(f"Navigating to {next_route} after confirmation.")


    # --- Define the Confirmation Dialog (Styled like screenshot) ---
    confirmation_dialog = ft.AlertDialog(
        modal=True, # Blocks interaction with the page behind it
        bgcolor=ft.colors.WHITE, # White dialog background
        shape=ft.RoundedRectangleBorder(radius=10), # Rounded corners for the dialog
        # Dialog Title
        title=ft.Text(
            "تأكيد انهاء تسجيل الدورة",
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.BOLD,
            size=20,
            color="#B58B18" # Gold title color
        ),
        # Dialog Action Buttons
        actions=[
            # Confirm Button (Green, appears right in RTL)
            ft.ElevatedButton(
                "تأكيد",
                bgcolor="#6FA03C", # Green background
                color=ft.colors.WHITE,
                on_click=confirm_end_registration,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                height=45, width=120 # Fixed size for consistency
            ),
            # Spacer between buttons
            ft.Container(width=25),
            # Cancel Button (Red, appears left in RTL)
            ft.ElevatedButton(
                 "الرجوع",
                 bgcolor="#C83737", # Red background
                 color=ft.colors.WHITE,
                 on_click=close_dialog, # Simply closes the dialog
                 style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                 height=45, width=120 # Fixed size for consistency
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER, # Center the buttons horizontally
        title_padding=ft.padding.only(top=30, bottom=25), # Space around the title
        content_padding=0, # Remove default padding if only using actions
        actions_padding=ft.padding.only(bottom=25) # Padding below actions before dialog edge
    )

    # --- Bottom Action Buttons ---
    def end_registration_click(e):
        """Opens the confirmation dialog when the 'End Registration' button is clicked."""
        print("End Course Registration Button Clicked - Opening Dialog")
        page.dialog = confirmation_dialog # Set the dialog for the page
        confirmation_dialog.open = True # Make the dialog visible
        page.update() # Update the UI to show the dialog

    def new_student_click(e):
        """Navigates to the start of the registration process for a new student."""
        print("New Student Button Clicked - Navigating to Options")
        target_route = "/register_course_options" # Route for starting new registration
        page.go(target_route)
        print(f"Navigating to {target_route} for new student.")

    # Define the bottom buttons
    return_button_bottom = ft.ElevatedButton(
        "الرجوع", icon=ft.icons.ARROW_BACK,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#5C544A", color=ft.colors.WHITE, height=45,
        on_click=go_back # Uses the same back navigation logic
    )
    end_reg_button = ft.ElevatedButton(
        "انهاء تسجيل الدورة", icon=ft.icons.CHECK_CIRCLE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#B58B18", color=ft.colors.WHITE, height=45,
        on_click=end_registration_click # Triggers the confirmation dialog
    )
    new_student_button = ft.ElevatedButton(
        "طالب جديد", icon=ft.icons.ADD,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#6FA03C", color=ft.colors.WHITE, height=45,
        on_click=new_student_click # Navigates to start new registration
    )

    # Arrange bottom buttons in a Row (order matters for RTL)
    # Visual order (Right to Left): Green, Gold, Grey
    bottom_buttons_row = ft.Row(
        [new_student_button, end_reg_button, return_button_bottom],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY, # Distribute buttons evenly
    )

    # --- Main Layout (Responsive Panels) ---
    main_panels_layout = ft.ResponsiveRow(
        [
            # Left Panel Container
            ft.Container(
                content=left_panel,
                col={"xs": 12, "sm": 12, "md": 5, "lg": 4}, # Responsive column sizing
                padding=ft.padding.only(bottom=10) # Add space below on small screens
            ),
            # Right Panel Container
            ft.Container(
                content=qr_code_image_container,
                col={"xs": 12, "sm": 12, "md": 7, "lg": 8}, # Responsive column sizing
                padding=ft.padding.only(bottom=10) # Add space below on small screens
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.START, # Align panels to the top
        spacing=30, # Horizontal space between panels when side-by-side
        run_spacing=20 # Vertical space between panels when they stack
    )

    # --- Assemble Page Content ---
    # Get the banner (using the imported or placeholder function)
    try:
        banner_control = create_banner(page.width)
    except Exception as e:
        print(f"ERROR creating banner: {e}")
        banner_control = ft.Container(height=60, bgcolor=ft.colors.RED, content=ft.Text(f"Banner Error: {e}"))

    # Stack elements vertically: Back Button Row -> Panels -> Bottom Button Row
    content_column = ft.Column(
        [
            # Top area for the back button
            ft.Container(
                content=ft.Row([back_button_page]), # Row ensures alignment options if needed
                padding=ft.padding.only(top=10, left=20, right=20) # Padding around back button
            ),
            # Main content area holding the responsive panels
            ft.Container(
                content=main_panels_layout,
                padding=ft.padding.only(left=30, right=30, top=5, bottom=20), # Padding around panels
                expand=True # Allow this area to grow vertically
            ),
            # Bottom area for action buttons
            ft.Container(
                content=bottom_buttons_row,
                padding=ft.padding.only(bottom=20, left=30, right=30) # Padding around bottom buttons
            )
        ],
        expand=True, # Make the content column fill the space below the banner
        scroll=ft.ScrollMode.ADAPTIVE, # Enable scrolling if content overflows
        spacing=0 # No extra space between the main content blocks
    )

    # --- Define the View ---
    return ft.View(
        route="/qr_display", # The route this view corresponds to
        padding=0, # No padding on the view itself
        bgcolor="#E3DCCC", # Beige background color matching screenshots
        # The main controls for the view: Banner + Content Column
        controls=[
            ft.Column(
                [
                    banner_control,
                    content_column,
                ],
                expand=True, # Ensure this column fills the entire view height
                spacing=0 # No space between banner and content
            )
            # Note: AlertDialog and Overlay are managed via page.dialog and page.overlay
        ]
    )


# --- Example Usage Section (for testing this file directly) ---
if __name__ == "__main__":
    # Define the assets directory relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets") # Standard location within the view's folder
    # If assets are one level up (common project structure)
    if not os.path.exists(assets_dir):
       assets_dir = os.path.join(os.path.dirname(current_dir), "assets")

    print(f"Using assets directory: {assets_dir}")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created assets directory: {assets_dir}")

    # Define asset file paths
    dummy_qr_path = os.path.join(assets_dir, "QR.png")
    dummy_logo_path = os.path.join(assets_dir, "logo.png")
    confetti_gif_path_test = os.path.join(assets_dir, "confetti.gif")

    # --- Create/Check Dummy Assets ---
    # QR Code
    if not os.path.exists(dummy_qr_path):
        print(f"Attempting to create dummy QR Code at: {dummy_qr_path}")
        try:
            import qrcode
            qr_img = qrcode.make("Successfully Registered! Test Data.")
            qr_img.save(dummy_qr_path)
            print(f"SUCCESS: Created dummy QR code.")
        except ImportError:
            print("WARNING: 'qrcode' library not found. Cannot create dummy QR.")
        except Exception as e:
            print(f"ERROR creating dummy QR code: {e}")

    # Logo
    if not os.path.exists(dummy_logo_path):
        print(f"Attempting to create dummy Logo at: {dummy_logo_path}")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (100, 100), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            d.rectangle([(10,10), (90,90)], fill=(100,100,180))
            d.text((30,45), "LOGO", fill=(255,255,255))
            img.save(dummy_logo_path)
            print(f"SUCCESS: Created dummy logo.")
        except ImportError:
            print("WARNING: 'Pillow' library not found. Cannot create dummy logo.")
        except Exception as e:
            print(f"ERROR creating dummy logo: {e}")

    # Confetti GIF Check
    if not os.path.exists(confetti_gif_path_test):
        print("\n" + "=" * 50)
        print(f"  IMPORTANT: Confetti GIF not found!")
        print(f"  Please download a transparent confetti GIF and save it as:")
        print(f"  '{confetti_gif_path_test}'")
        print(f"  The success overlay will show a checkmark icon instead.")
        print("=" * 50 + "\n")

    # --- Flet App Definition for Testing ---
    def main(page: ft.Page):
        page.title = "QR Display View - Test"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # !!! CRITICAL FOR LAYOUT !!!
        page.rtl = True
        print(f"Test Setup: page.rtl has been set to {page.rtl}")

        # --- Simulate Navigation History ---
        # Create a dummy view representing the screen the user came from
        dummy_previous_view = ft.View(
            route="/camera_qr", # Route of the screen before this one
            controls=[
                ft.AppBar(title=ft.Text("Dummy Previous Screen")),
                ft.Text("This is a placeholder for the screen before the QR display."),
                ft.ElevatedButton("Go to QR Display", on_click=lambda _: page.go("/qr_display"))
            ]
        )

        # Create the actual view we are testing
        qr_view_instance = create_qr_display_view(page)

        # --- Setup Routing for Testing ---
        def route_change(route):
            print(f"Route changing to: {page.route}")
            page.views.clear() # Clear existing views
            page.views.append(dummy_previous_view) # Add the "previous" screen first

            if page.route == "/qr_display":
                page.views.append(qr_view_instance) # Add the QR view if navigating to it
            # Add other routes here if needed for more complex testing

            # Ensure the latest view is at the end
            if len(page.views) > 1 and page.route != page.views[-1].route:
                 # If route is /camera_qr, keep only the dummy view
                 if page.route == "/camera_qr":
                      page.views.pop()

            print(f"Current views stack: {[v.route for v in page.views]}")
            page.update()

        page.on_route_change = route_change
        page.go("/qr_display") # Start the test by navigating directly to the QR view

    # --- Run the Test App ---
    print(f"Running Flet app with assets from: {assets_dir}")
    ft.app(
        target=main,
        assets_dir=assets_dir # Make sure Flet knows where to find assets
    )