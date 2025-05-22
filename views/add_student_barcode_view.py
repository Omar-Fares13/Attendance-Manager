import flet as ft
from components.banner import create_banner
from utils.assets import ft_asset
from logic.qr_scanner import scan_qr_code_continuous
from logic.qr_code_decryption_systeml import process_qr_data
import threading
import base64
import json
import logging
import sys

# Set up logging to show in terminal
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_add_student_barcode_view(page: ft.Page):
    """Creates the Flet View for adding a new student using barcode."""
    logger.info("="*50)
    logger.info("Initializing Add Student Barcode View")
    
    # Counter for scanned QR codes
    scanned_count = 0
    count_text = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color="#B58B18")
    scanning_active = False
    
    # Student data display
    student_name = ft.Text("-", size=20, color="#666666")
    student_national_id = ft.Text("-", size=20, color="#666666")
    student_address = ft.Text("-", size=20, color="#666666")
    student_phone = ft.Text("-", size=20, color="#666666")
    
    def parse_qr_data(qr_value):
        """Parse QR code data and return student information"""
        logger.info("="*50)
        logger.info("Parsing QR code data")
        logger.info(f"Raw QR value: {repr(qr_value)}")  # Show raw representation
        logger.info(f"QR value length: {len(qr_value)}")
        logger.info(f"QR value bytes: {[hex(ord(c)) for c in qr_value[:20]]}...")  # Show first 20 bytes in hex
        
        try:
            # Clean the QR value first
            qr_value = qr_value.strip()
            # Remove any BOM or special characters
            qr_value = qr_value.lstrip('\ufeff')
            # Remove any null bytes
            qr_value = qr_value.replace('\x00', '')
            
            logger.info("After cleaning:")
            logger.info(f"Cleaned QR value: {repr(qr_value)}")
            logger.info(f"Cleaned length: {len(qr_value)}")
            
            # First try to parse as JSON directly
            logger.info("Attempting to parse as JSON directly...")
            try:
                # Try to fix common JSON issues before parsing
                json_str = qr_value
                # Replace single quotes with double quotes
                json_str = json_str.replace("'", '"')
                # Fix trailing commas
                json_str = json_str.replace(',}', '}')
                json_str = json_str.replace(',]', ']')
                
                logger.info("Attempting to parse JSON string:")
                logger.info(f"JSON string: {repr(json_str)}")
                
                # Try to detect if the string starts with a valid JSON character
                if not json_str or json_str[0] not in '{[':
                    logger.info("Not a JSON string, attempting to process as base64...")
                    # If not JSON, try to process as base64
                    try:
                        student_data = process_qr_data(qr_value)
                        logger.info("Successfully processed QR data")
                        logger.info(f"Processed data: {student_data}")
                        
                        return {
                            'full_name': student_data.full_name,
                            'national_id': student_data.national_id,
                            'phone_number': student_data.phone_number,
                            'address': student_data.address
                        }
                    except Exception as e:
                        logger.error("="*50)
                        logger.error("QR Data Processing Error")
                        logger.error(f"Error type: {type(e).__name__}")
                        logger.error(f"Error details: {str(e)}")
                        logger.error(f"QR value: {repr(qr_value)}")
                        logger.error("="*50)
                        raise Exception(f"Failed to process QR data: {str(e)}")
                
                data = json.loads(json_str)
                logger.info("Successfully parsed as JSON")
                logger.info(f"Parsed data: {data}")
                
                # If we got here, we successfully parsed JSON
                return {
                    'full_name': data.get('fullName', data.get('n', '')),
                    'national_id': data.get('nationalId', data.get('i', '')),
                    'phone_number': data.get('phoneNumber', data.get('p', '')),
                    'address': data.get('address', data.get('a', ''))
                }
                
            except json.JSONDecodeError as e:
                logger.info(f"JSON parsing failed: {str(e)}, attempting base64 processing...")
                # If not JSON, try to process as base64
                try:
                    student_data = process_qr_data(qr_value)
                    logger.info("Successfully processed QR data")
                    logger.info(f"Processed data: {student_data}")
                    
                    return {
                        'full_name': student_data.full_name,
                        'national_id': student_data.national_id,
                        'phone_number': student_data.phone_number,
                        'address': student_data.address
                    }
                except Exception as e:
                    logger.error("="*50)
                    logger.error("QR Data Processing Error")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.error(f"Error details: {str(e)}")
                    logger.error(f"QR value: {repr(qr_value)}")
                    logger.error("="*50)
                    raise Exception(f"Failed to process QR data: {str(e)}")
                
        except Exception as e:
            logger.error("="*50)
            logger.error("QR Code Processing Error")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"QR value: {repr(qr_value)}")
            logger.error("="*50)
            raise Exception(f"Failed to process QR data: {str(e)}")
    
    def go_back(e):
        # Stop scanning if active
        if scanning_active:
            logger.info("Stopping scanning due to back button press")
            stop_scanning()
        page.go("/manage_students")
        
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD_OUTLINED,
        icon_color="#B58B18",
        tooltip="العودة",
        on_click=go_back,
        icon_size=30
    )
    
    page_title = ft.Text(
        "اضافة طالب جديد بالباركود",
        size=28,
        weight=ft.FontWeight.BOLD,
        color="#B58B18"
    )

    # Create scan button
    scan_btn = ft.ElevatedButton(
        "ابدأ مسح الباركود",
        bgcolor="#B58B18",
        color=ft.colors.WHITE,
        width=200,
        on_click=lambda e: toggle_scanning(e.page, scan_btn)
    )

    def stop_scanning():
        """Stops the QR code scanning process"""
        nonlocal scanning_active
        logger.info("Stopping QR code scanning")
        scanning_active = False
        scan_btn.text = "ابدأ مسح الباركود"
        scan_btn.disabled = False
        page.update()

    def toggle_scanning(page: ft.Page, scan_btn: ft.ElevatedButton):
        """Toggles the QR code scanning process"""
        nonlocal scanning_active
        
        if scanning_active:
            logger.info("Scanning already active, stopping...")
            stop_scanning()
            return
            
        logger.info("Starting QR code scanning")
        scanning_active = True
        scan_btn.disabled = True
        scan_btn.text = "جاري المسح..."
        page.update()

        def on_detect(qr_code_value):
            """Callback when a QR code is detected"""
            if not scanning_active:
                logger.info("Scanning stopped, ignoring QR code")
                return
                
            nonlocal scanned_count
            scanned_count += 1
            count_text.value = str(scanned_count)
            logger.info(f"QR code detected (count: {scanned_count})")
            
            try:
                # Parse QR code data
                logger.info("Processing QR code data...")
                student_info = parse_qr_data(qr_code_value)
                logger.info("Successfully processed QR code data")
                
                # Update student information
                student_name.value = student_info['full_name']
                student_national_id.value = student_info['national_id']
                student_address.value = student_info['address']
                student_phone.value = student_info['phone_number']
                
                # Show success message
                logger.info("Showing success message")
                snackbar = ft.SnackBar(
                    content=ft.Text("تم قراءة بيانات الطالب بنجاح"),
                    bgcolor=ft.colors.GREEN_700,
                    duration=1000
                )
                page.overlay.append(snackbar)
                snackbar.open = True
                
            except Exception as e:
                # Show error message with more details
                error_msg = str(e)
                logger.error("="*50)
                logger.error("QR Code Processing Error")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error details: {error_msg}")
                logger.error(f"QR code value: {qr_code_value}")
                logger.error("="*50)
                
                snackbar = ft.SnackBar(
                    content=ft.Text(f"خطأ في قراءة البيانات: {error_msg}"),
                    bgcolor=ft.colors.RED_700,
                    duration=30000
                )
                page.overlay.append(snackbar)
                snackbar.open = True
            
            page.update()

        # Start scanning in separate thread
        logger.info("Starting QR code scanning thread")
        threading.Thread(
            target=scan_qr_code_continuous,
            args=(on_detect,),
            daemon=True
        ).start()
    
    # Create the main content
    content_column = ft.Column(
        [
            ft.Container(
                padding=ft.padding.only(top=20, left=30, right=30),
                content=ft.Row(
                    [page_title, back_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            ft.Container(
                expand=True,
                padding=ft.padding.symmetric(horizontal=30, vertical=20),
                alignment=ft.alignment.center,
                content=ft.Row(
                    [
                        # Left column - QR scanner
                        ft.Column(
                            [
                                ft.Icon(
                                    ft.icons.QR_CODE_SCANNER,
                                    size=100,
                                    color="#B58B18"
                                ),
                                ft.Container(height=20),
                                ft.Text(
                                    "قم بمسح باركود الطالب",
                                    size=20,
                                    color="#666666",
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Container(height=20),
                                ft.Row(
                                    [
                                        ft.Text(
                                            "عدد الباركود المقروءة: ",
                                            size=20,
                                            color="#666666"
                                        ),
                                        count_text
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.Container(height=20),
                                scan_btn
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        # Right column - Student data
                        ft.Container(
                            width=400,
                            padding=20,
                            border=ft.border.all(2, "#B58B18"),
                            border_radius=10,
                            content=ft.Column(
                                [
                                    ft.Container(height=20),
                                    ft.Row(
                                        [
                                            ft.Text("اسم الطالب: ", size=20, color="#B58B18", weight=ft.FontWeight.BOLD),
                                            student_name
                                        ],
                                        alignment=ft.MainAxisAlignment.START
                                    ),
                                    ft.Container(height=10),
                                    ft.Row(
                                        [
                                            ft.Text("الرقم القومي: ", size=20, color="#B58B18", weight=ft.FontWeight.BOLD),
                                            student_national_id
                                        ],
                                        alignment=ft.MainAxisAlignment.START
                                    ),
                                    ft.Container(height=10),
                                    ft.Row(
                                        [
                                            ft.Text("العنوان: ", size=20, color="#B58B18", weight=ft.FontWeight.BOLD),
                                            student_address
                                        ],
                                        alignment=ft.MainAxisAlignment.START
                                    ),
                                    ft.Container(height=10),
                                    ft.Row(
                                        [
                                            ft.Text("رقم الهاتف: ", size=20, color="#B58B18", weight=ft.FontWeight.BOLD),
                                            student_phone
                                        ],
                                        alignment=ft.MainAxisAlignment.START
                                    )
                                ],
                                spacing=10
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=50
                )
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    banner_control = create_banner(page.width)
    logger.info("Add Student Barcode View initialized successfully")
    logger.info("="*50)
    
    return ft.View(
        route="/add_student_barcode",
        padding=0,
        bgcolor="#E3DCCC",
        controls=[
            ft.Column(
                [banner_control, content_column],
                expand=True,
                spacing=0
            )
        ]
    ) 