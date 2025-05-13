import os
import io
import threading
import time
import flet as ft
from tkinter import filedialog, Tk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from logic.students import get_all_students_with_relationships
from logic.qr_generator import generate_qr_code

def generate_qr_pdfs(page: ft.Page):
    """Generate PDF files for all students with their QR codes"""
    
    # Function to show success/error messages
    def show_snackbar(message, color=ft.colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.RIGHT),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()
    
    # Create progress dialog components first
    progress = ft.ProgressBar(width=300, value=0)
    progress_text = ft.Text("جاري إنشاء الملفات...")
    progress_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("إنشاء ملفات PDF"),
        content=ft.Column([progress_text, progress], tight=True),
    )
    
    # Function to create the actual PDFs
    def process_pdf_generation():
        try:
            # Get students with all relationships preloaded
            students = get_all_students_with_relationships()
            if not students:
                show_snackbar("لا يوجد طلاب مسجلين", ft.colors.AMBER_700)
                return
            
            # We need to ask for directory BEFORE starting the thread
            # This is handled in the main function below
            save_dir = page.client_storage.get("temp_save_dir")
            
            if not save_dir:  # User cancelled
                show_snackbar("تم إلغاء العملية", ft.colors.AMBER_700)
                return
            
            # Show progress dialog
            page.dialog = progress_dialog
            progress_dialog.open = True
            page.update()
            
            # Generate PDFs for each student
            total = len(students)
            success_count = 0
            
            for i, student in enumerate(students):
                try:
                    # Get course information
                    course = student.course
                    if not course:
                        print(f"Warning: No course found for student {student.name} (ID: {student.id})")
                        continue
                    
                    # Format date ranges for the filename (day/month only)
                    start_date_str = course.start_date.strftime("%d-%m")
                    end_date_str = course.end_date.strftime("%d-%m")
                    date_range = f"{start_date_str}-{end_date_str}"
                    
                    # Format filename: seq_faculty_gender_daterange.pdf
                    gender = "ذكور" if student.is_male else "اناث"
                    faculty_name = student.faculty.name.replace(" ", "_")
                    filename = f"{student.seq_number}_{faculty_name}_{gender}_{date_range}.pdf"
                    filepath = os.path.join(save_dir, filename)
                    
                    # Create PDF
                    buffer = io.BytesIO()
                    p = canvas.Canvas(buffer, pagesize=A4)
                    
                    # Generate QR code and convert to ImageReader
                    qr_buffer = generate_qr_code(student.qr_code)
                    img = ImageReader(qr_buffer)
                    p.drawImage(img, 175, 400, width=250, height=250)
                    
                    p.save()
                    
                    # Save the PDF
                    with open(filepath, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    success_count += 1
                    
                    # Update progress
                    progress.value = (i + 1) / total
                    progress_text.value = f"تم إنشاء {i+1} من {total} ملف"
                    page.update()
                    
                except Exception as e:
                    print(f"Error creating PDF for student {student.name}: {e}")
            
            # Close progress dialog
            progress_dialog.open = False
            page.update()
            
            # Show completion message
            show_snackbar(f"تم إنشاء {success_count} من {total} ملف PDF بنجاح")
            
        except Exception as e:
            # Show error message
            print(f"Error in PDF generation: {e}")
            progress_dialog.open = False  # Make sure dialog is closed
            page.update()
            show_snackbar(f"حدث خطأ: {str(e)}", ft.colors.RED_700)
    
    # First ask for directory on the main thread
    root = Tk()
    root.attributes('-topmost', True)  # Force to front
    root.lift()  # Bring window to front
    root.focus_force()  # Force focus
    root.withdraw()  # Hide the main window
    
    save_dir = filedialog.askdirectory(title="اختر مكان حفظ ملفات PDF", parent=root)
    root.destroy()
    
    # Store directory in client storage for the thread to access
    page.client_storage.set("temp_save_dir", save_dir)
    
    if save_dir:
        # Run the process in a thread
        threading.Thread(target=process_pdf_generation, daemon=True).start()
    else:
        show_snackbar("تم إلغاء العملية", ft.colors.AMBER_700)