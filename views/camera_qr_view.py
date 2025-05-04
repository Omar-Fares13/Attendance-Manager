# views/camera_qr_view.py
# This file defines the view for the '/camera_qr' route,
# matching the FIRST screenshot ("الصورة").

import flet as ft
import os

# Make sure these components/utils exist and are importable
# Adjust the path based on your project structure if necessary
try:
    # Assuming components and utils are siblings to the views directory
    from ..components.banner import create_banner
    from ..utils.assets import ft_asset
except (ImportError, ValueError):
    print("WARN: Failed to import components/utils relative to camera_qr_view. Trying absolute.")
    try:
        from components.banner import create_banner
        from utils.assets import ft_asset
    except ImportError:
        print("ERROR: Failed to import components/utils in camera_qr_view. Check paths.")
        # Fallback placeholders if imports fail
        def create_banner(page_width): return ft.Container(
            content=ft.Row([
                ft.Image(src='assets/logo.png' if os.path.exists('assets/logo.png') else '', height=40), # Placeholder logo
                ft.Text("التربية العسكرية - جامعة عين شمس", color=ft.colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            height=60,
            bgcolor="#5C544A", # Dark Grey placeholder
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )
        def ft_asset(path): return path # Assume assets are directly accessible


# --- Helper to display student data lines ---
def create_data_row(label: str, value: str):
    """Creates a Row for displaying a label and value (RTL friendly)."""
    return ft.Row(
        [
            # Value first (left in LTR, right in RTL)
            ft.Text(
                value,
                text_align=ft.TextAlign.RIGHT, # Align text content right within its bounds
                weight=ft.FontWeight.W_500,
                size=14,
                color=ft.colors.BLACK87,
                selectable=True, # Allow text selection
            ),
            # Label second (right in LTR, left in RTL)
            ft.Text(
                label,
                text_align=ft.TextAlign.RIGHT, # Align text content right within its bounds
                weight=ft.FontWeight.BOLD,
                size=14,
                color="#B58B18", # Gold color
            ),
        ],
        alignment=ft.MainAxisAlignment.END, # Align items to the end (right for LTR, left for RTL)
        spacing=5,
        # Ensure the row itself flows correctly in RTL
        # Flet handles this implicitly if page.rtl = True
    )

# --- Main View Creation Function ---
def create_camera_qr_view(page: ft.Page):
    """Creates the Flet View for the Camera/QR screen, matching the FIRST image."""

    # IMPORTANT: Ensure page.rtl is set to True for correct Arabic layout
    # This should ideally be done in your main app setup: page.rtl = True
    if not page.rtl:
       print("WARNING: page.rtl is not set to True. Layout might be incorrect for Arabic.")
       # page.rtl = True # You could force it here, but global setup is better

    # --- Controls ---
    def go_back(e):
        """Navigates back to the previous view or a fallback route."""
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            # Define a sensible fallback if there's no previous view in the stack
            page.go("/register_course_options")
            print("Navigating back to fallback '/register_course_options'")

    back_button_top_left = ft.IconButton(
        # Use ARROW_FORWARD for RTL back arrow (points left visually)
        icon=ft.icons.ARROW_FORWARD_OUTLINED,
        icon_color="#B58B18", # Gold color
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )

    page_title = ft.Text(
        "الصورة",
        size=32,
        weight=ft.FontWeight.BOLD,
        color="#B58B18", # Gold color
        text_align=ft.TextAlign.CENTER
    )

    # --- Left Panel: Student Data ---
    student_data_column = ft.Column(
        spacing=8,
        controls=[
            # Use a Row to center the Title text within the column width
            ft.Row(
                [
                    ft.Text(
                        "بيانات الطالب",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="#B58B18",  # Gold color
                        # text_align=ft.TextAlign.CENTER # Not strictly needed now Row handles it
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER  # Center horizontally
            ),
            ft.Divider(height=1, color=ft.colors.with_opacity(0.5, "#B58B18")),  # Thin gold divider
            # --- Placeholder Data (Replace with actual data later) ---
            create_data_row("الاسم:", "محمد محمد محمد"),
            create_data_row("ID الطالب:", "123456"),
            create_data_row("الرقم القومي:", "12345678901234"),
            create_data_row("الكلية:", "الهندسة"),
            create_data_row("مسلسل:", "123"),
            create_data_row("ملاحظات:", "واحد اثنان ثلاثة اربعة"),
        ]
    )

    # --- Button Click Handlers ---
    def show_qr_click(e):
        # This function should navigate to the QR display page
        print("Show QR Clicked - Navigating to /qr_display")
        page.go("/qr_display")
        # No other UI changes happen on THIS screen when this button is clicked

    def retake_photo_click(e):
        # This function should likely re-initialize or interact with the camera
        print("Retake Photo Clicked - Action Needed")
        page.show_snack_bar(ft.SnackBar(ft.Text("إعادة تفعيل الكاميرا... (تحتاج لتنفيذ)"), open=True))
        # !! Add logic here to handle camera retake !!

    def capture_click(e):
        # This function should capture the image from the camera feed
        print("Capture Clicked - Action Needed")
        page.show_snack_bar(ft.SnackBar(ft.Text("التقاط الصورة... (تحتاج لتنفيذ)"), open=True))
        # !! Add logic here to capture image !!

    # --- Buttons ---
    # NOTE: In RTL, the order in the Row list is reversed visually.
    # First item goes right, second item goes left.

    show_qr_btn = ft.ElevatedButton( # Gold Button (عرض QR - visually on the right in RTL)
        "عرض QR",
        icon=ft.icons.QR_CODE_2,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#B58B18", # Gold color
        color=ft.colors.WHITE,
        height=40,
        on_click=show_qr_click
    )

    retake_photo_btn = ft.ElevatedButton( # Red Button (اعادة الصورة - visually on the left in RTL)
        "اعادة الصورة",
        icon=ft.icons.REFRESH,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#C83737", # Red color
        color=ft.colors.WHITE,
        height=40,
        on_click=retake_photo_click
    )

    return_button_main = ft.ElevatedButton( # Grey Button (Bottom Left)
        "الرجوع",
        icon=ft.icons.ARROW_BACK, # Standard back arrow icon
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#5C544A", # Dark grey color
        color=ft.colors.WHITE,
        height=45,
        on_click=go_back
    )

    capture_button = ft.ElevatedButton( # Green Button (Below Camera)
        "التقاط",
        icon=ft.icons.CAMERA_ALT, # Using CAMERA_ALT for better visual
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        bgcolor="#6FA03C", # Green color
        color=ft.colors.WHITE,
        height=45,
        on_click=capture_click
    )

    # --- Panel Layouts ---
    left_panel = ft.Container( # Contains Data + Retake/ShowQR buttons
        content=ft.Column(
            [
                student_data_column,
                # Spacer to push buttons to the bottom
                ft.Container(expand=True),
                # Button Row - Order matters for RTL visual layout
                ft.Row(
                    # For RTL: First item is right, Second item is left.
                    # Image shows Gold (QR) on Right, Red (Retake) on Left.
                    [show_qr_btn, retake_photo_btn],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            # Ensure column takes available space if needed, but main alignment is start
            alignment=ft.MainAxisAlignment.START,
            spacing=15 # Add some space between data and buttons
        ),
        # Styling to match the image
        bgcolor=ft.colors.WHITE, # White background inside panel
        border=ft.border.all(2, "#B58B18"), # Gold border
        border_radius=12, # Rounded corners
        padding=ft.padding.all(15),
    )

    # Placeholder for Camera Feed / Captured Image
    # Replace 'assets/placeholder_camera.png' with your actual placeholder or camera feed widget
    camera_image_placeholder = ft.Image(
        # Use a placeholder image that looks similar to the screenshot's blurry background
        src=ft_asset("assets/placeholder_camera.jpg"), # <<< CHANGE AS NEEDED
        # Or use the camo if that's the intended placeholder:
        # src=ft_asset("assets/camo.png"),
        fit=ft.ImageFit.COVER,
        border_radius=8, # Slightly rounded corners for the image itself inside the border
        expand=True # Make image fill the container space
    )

    camera_container = ft.Container( # Camera Area Container
        content=camera_image_placeholder,
        # Styling to match the image
        # Removed internal alignment=center to let image expand
        border=ft.border.all(2, "#B58B18"), # Gold border
        border_radius=12, # Rounded corners for the container
        expand=True, # Allow container to expand vertically
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS, # Ensure inner radius is clipped nicely
    )

    right_panel_column = ft.Column( # Contains Camera + Capture button
        [
            # Camera area takes most space
            ft.Container(content=camera_container, expand=True),
            # Space between camera and button
            ft.Container(height=15),
            # Capture button centered below camera
            ft.Row([capture_button], alignment=ft.MainAxisAlignment.CENTER)
        ],
        expand=True, # Allow column to expand vertically
        spacing=0 # No extra space between elements managed by Containers above
    )

    # --- Main Layout using ResponsiveRow for Panels ---
    main_panels_layout = ft.ResponsiveRow(
        [
            # Left Panel takes less space on medium/large screens
            ft.Container(
                content=left_panel,
                col={"xs": 12, "sm": 12, "md": 5, "lg": 4}, # Adjusted columns
                padding=ft.padding.only(bottom=10) # Add padding for small screens run spacing
            ),
            # Right Panel takes more space
            ft.Container(
                content=right_panel_column,
                col={"xs": 12, "sm": 12, "md": 7, "lg": 8}, # Adjusted columns
                padding=ft.padding.only(bottom=10)
            ),
        ],
        # Align panels to the top and stretch vertically if possible
        vertical_alignment=ft.CrossAxisAlignment.START, # Changed from STRETCH
        spacing=30, # Horizontal space between panels
        run_spacing=20 # Vertical space between rows on small screens
    )

    # --- Get banner ---
    # Ensure the banner is created correctly - this relies on the imported function
    try:
        # Pass page width for potential responsiveness in the banner itself
        banner_control = create_banner(page.width)
    except Exception as e:
        print(f"ERROR creating banner: {e}")
        banner_control = ft.Container(
            height=60,
            bgcolor=ft.colors.RED,
            content=ft.Text(f"Banner Error: {e}")
        )

    # --- Page Content Layout ---
    content_column = ft.Column(
        [
            # Top Bar: Back button on the left
            ft.Container(
                content=ft.Row([back_button_top_left]),
                padding=ft.padding.only(top=10, left=20, right=20) # Added right padding
            ),
            # Centered Title below the back button row
            ft.Container(
                content=ft.Row([page_title], alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.only(bottom=15)
            ),
            # Main content area (panels) with padding and expansion
            ft.Container(
                content=main_panels_layout,
                padding=ft.padding.symmetric(horizontal=30),
                expand=True # Allow this container to take up remaining vertical space
            ),
            # Bottom Bar: Return button on the left
            ft.Container(
                content=ft.Row([return_button_main]),
                padding=ft.padding.only(left=30, bottom=20, top=10, right=30) # Added right padding
            )
        ],
        expand=True, # Make this column fill the space below the banner
        scroll=ft.ScrollMode.ADAPTIVE, # Allow scrolling if content overflows
        spacing=0 # Remove default spacing between column elements
    )

    # --- View Definition ---
    return ft.View(
        route="/camera_qr", # Route for THIS view
        padding=0, # No padding for the view itself
        bgcolor="#E3DCCC", # Beige background matching the image
        controls=[
            # Stack banner and main content vertically
            ft.Column(
                [
                    banner_control,
                    content_column, # Add the main content area
                ],
                expand=True, # Ensure this column fills the page
                spacing=0 # No space between banner and content column
            )
        ]
    )

# --- Example Usage (for testing this view directly) ---
if __name__ == "__main__":
    # You'll need a way to provide assets if running directly
    # Create dummy assets folder and files if needed
    if not os.path.exists("assets"):
        os.makedirs("assets")
    # Create dummy placeholder image if it doesn't exist
    dummy_image_path = "assets/placeholder_camera.png"
    if not os.path.exists(dummy_image_path):
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (400, 300), color = (200, 200, 200))
            d = ImageDraw.Draw(img)
            d.text((150,130), "Placeholder", fill=(50,50,50))
            img.save(dummy_image_path)
            print(f"Created dummy placeholder image at: {dummy_image_path}")
        except ImportError:
            print("PIL not found, cannot create dummy image. Please provide 'assets/placeholder_camera.png'")
        except Exception as e:
             print(f"Error creating dummy image: {e}")

    # Dummy logo for banner placeholder
    dummy_logo_path = "assets/logo.png"
    if not os.path.exists(dummy_logo_path):
         try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (100, 100), color = (240, 240, 240))
            d = ImageDraw.Draw(img)
            d.rectangle([(10,10), (90,90)], fill=(100,100,180))
            d.text((30,45), "LOGO", fill=(255,255,255))
            img.save(dummy_logo_path)
            print(f"Created dummy logo image at: {dummy_logo_path}")
         except ImportError:
            print("PIL not found, cannot create dummy logo. Please provide 'assets/logo.png'")
         except Exception as e:
             print(f"Error creating dummy logo: {e}")


    def main(page: ft.Page):
        page.title = "Camera QR View Test"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # !!! IMPORTANT FOR ARABIC LAYOUT !!!
        page.rtl = True

        # Add the view to the page
        camera_view = create_camera_qr_view(page)
        page.views.append(camera_view) # Add directly for testing
        page.update()

        # Simulate navigation for testing go_back
        def navigate_to_test_view(e):
             # A dummy previous view
             page.views.insert(0, ft.View("/register_course_options", [ft.Text("Dummy Previous View"), ft.ElevatedButton("Go to Camera", on_click=lambda _: page.go("/camera_qr"))]))
             page.go("/camera_qr") # Go back to the camera view after adding previous one

        # Optional: Add a button to simulate being on a different page first
        # page.add(ft.ElevatedButton("Simulate Navigation History", on_click=navigate_to_test_view))


    ft.app(target=main, assets_dir="assets") # Make assets folder available