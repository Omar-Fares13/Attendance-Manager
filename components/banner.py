# components/banner.py
import flet as ft
from utils.assets import ft_asset # Use ft_asset for src (ensure this import works)

def create_banner(page_width = 100): # No page_width argument needed
    """Creates the responsive top banner widget."""
    BANNER_H = 140 # Consistent height

    return ft.Stack(
        # The Stack will expand horizontally if its parent allows/dictates.
        # Typically, placing this banner at the top of a View's main Column
        # achieves this automatically.
        height=BANNER_H,
        controls=[
            # 1. Camouflage Background Image
            ft.Image(
                src=ft_asset("camo.png"), # Use relative path for Flet assets
                # width removed - let parent/Stack determine width
                height=BANNER_H,
                fit=ft.ImageFit.COVER,
                # Optional: If the background image *still* doesn't fill the
                # width in your specific layout, you might need expand=True.
                # Try without first.
                # expand=True
            ),
            # 2. Overlay Content (Logo + Text)
            ft.Container(
                # Container expands to fill the Stack area by default
                padding=ft.padding.symmetric(horizontal=30, vertical=15), # Reduced horizontal padding
                content=ft.Row(
                    [
                        # Logo (consider wrapping in a Container if more control is needed)
                        ft.Image(
                            src=ft_asset("logo.png"), # Use relative path
                            width=80, height=80,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        # Text Column - Make it expand to push against the logo
                        ft.Column(
                            [
                                ft.Text(
                                    "التربية العسكرية",
                                    size=32, weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE,
                                    # Ensure text aligns right within its column space
                                    text_align=ft.TextAlign.RIGHT
                                ),
                                ft.Text(
                                    "جامعة عين شمس",
                                    size=18, color=ft.Colors.WHITE,
                                    # Ensure text aligns right within its column space
                                    text_align=ft.TextAlign.RIGHT
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER, # Center vertically within the column
                            horizontal_alignment=ft.CrossAxisAlignment.END, # Align text lines to the right end
                            expand=True # <<< Allow this column to take available horizontal space
                        )
                    ],
                    # Space between works well here to push logo and text apart
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ]
    )

# --- IMPORTANT: Update View Files ---
# You MUST now go into every view file (like login_view.py, dashboard_view.py,
# upload_course_file_view.py, etc.) that uses the banner and change the line:
#
# From: banner_control = create_banner(page.width)
# or:   banner_control = create_banner(page.window_width or 1200)
#
# To:   banner_control = create_banner()
#
# Example in upload_course_file_view.py:
#
#    # --- Get Banner ---
#    # Ensure create_banner can handle potential None width if page hasn't fully rendered
#    # banner_control = create_banner(page.window_width or 1200) # OLD WAY
#    banner_control = create_banner() # NEW RESPONSIVE WAY
#
# --- End Example ---