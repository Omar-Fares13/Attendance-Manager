import os
import io
import threading
import flet as ft
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from logic.students import get_all_students_with_relationships
from logic.qr_generator import generate_qr_code

def generate_qr_pdfs(page: ft.Page):
    """Generate PDF files for all students with their QR codes"""

    # Function to show success/error messages
    # This runs on the main UI thread, so it's safe
    def show_snackbar(message, color=ft.colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, text_align=ft.TextAlign.RIGHT),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    # Helper function to update UI elements from a background thread
    # Flet requires UI updates to be done on the main thread
    def run_on_ui_thread(func):
        page.run_thread(func)

    # Create progress dialog components first
    progress = ft.ProgressBar(width=300, value=0)
    progress_text = ft.Text("جاري إنشاء الملفات...")
    progress_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("إنشاء ملفات PDF"),
        content=ft.Column([progress_text, progress], tight=True),
    )

    # Function to handle opening/closing the progress dialog
    def update_progress_dialog(open_status):
        page.dialog = progress_dialog
        progress_dialog.open = open_status
        page.update()

    # Function to update the progress bar and text
    def update_progress(value, text):
        progress.value = value
        progress_text.value = text
        page.update()

    # Function to create the actual PDFs - MODIFIED TO ACCEPT save_dir
    def process_pdf_generation(save_dir):
        try:
            # Get students with all relationships preloaded
            students = get_all_students_with_relationships()
            if not students:
                # Use run_on_ui_thread to show snackbar from the thread
                run_on_ui_thread(lambda: show_snackbar("لا يوجد طلاب مسجلين", ft.colors.AMBER_700))
                return

            # Show progress dialog - Use run_on_ui_thread
            run_on_ui_thread(lambda: update_progress_dialog(True))

            # Generate PDFs for each student
            total = len(students)
            success_count = 0
            
            # Track created folders to avoid recreating them
            created_folders = set()

            for i, student in enumerate(students):
                try:
                    # Get course information
                    course = student.course
                    if not course:
                        print(f"Warning: No course found for student {student.name} (ID: {student.id})")
                        continue

                    # Format date ranges for folder and filename (day/month only)
                    start_date_str = course.start_date.strftime("%d-%m")
                    end_date_str = course.end_date.strftime("%d-%m")
                    date_range = f"{start_date_str}-{end_date_str}"

                    # Create folder name based on course and gender
                    gender_text = "ذكور" if student.is_male else "اناث"
                    faculty_name = student.faculty.name.replace(" ", "_")
                    
                    # Create folder name: faculty_gender_courseID_daterange
                    folder_name = f"{gender_text}_دورة_{date_range}"
                    course_folder_path = os.path.join(save_dir, folder_name)
                    
                    # Create the folder if it doesn't exist
                    if folder_name not in created_folders:
                        os.makedirs(course_folder_path, exist_ok=True)
                        created_folders.add(folder_name)

                    # Create student PDF filename
                    filename = f"{student.seq_number}_{faculty_name}.pdf"
                    filepath = os.path.join(course_folder_path, filename)

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

                    # Update progress - Use run_on_ui_thread
                    run_on_ui_thread(lambda: update_progress((i + 1) / total, f"تم إنشاء {i+1} من {total} ملف"))

                except Exception as e:
                    print(f"Error creating PDF for student {student.name}: {e}")
                    # Log error for this specific student, but continue

            # Close progress dialog - Use run_on_ui_thread
            run_on_ui_thread(lambda: update_progress_dialog(False))

            # Show completion message - Use run_on_ui_thread
            run_on_ui_thread(lambda: show_snackbar(f"تم إنشاء {success_count} من {total} ملف PDF بنجاح"))

        except Exception as e:
            # Show error message - Use run_on_ui_thread
            print(f"Error in PDF generation: {e}")
            # Make sure dialog is closed even on error
            run_on_ui_thread(lambda: update_progress_dialog(False))
            run_on_ui_thread(lambda: show_snackbar(f"حدث خطأ: {str(e)}", ft.colors.RED_700))


    # --- Flet File Picker Logic (replaces Tkinter) ---

    # Define the result handler for the file picker dialog
    def pick_directory_result(e: ft.FilePickerResultEvent):
        # e.path contains the selected directory path, or None if cancelled
        save_dir = e.path if e.path else None

        # No need for page.client_storage anymore
        # page.client_storage.set("temp_save_dir", save_dir) # Remove this

        if save_dir:
            # If a directory was selected, start the background thread
            # Pass the selected directory path to the thread function
            threading.Thread(target=process_pdf_generation, args=(save_dir,), daemon=True).start()
        else:
            # If the user cancelled the dialog
            show_snackbar("تم إلغاء العملية", ft.colors.AMBER_700)

    # Create the FilePicker instance
    # This control doesn't have a visual representation, it just opens the OS dialog
    file_picker = ft.FilePicker(on_result=pick_directory_result)

    # Add the file picker to the page's overlay
    # Overlay is a list of controls displayed on top of everything else.
    # This is necessary for the FilePicker to work correctly within Flet.
    page.overlay.append(file_picker)
    page.update() # Update the page to ensure the file_picker is added

    # Open the native directory picker dialog
    file_picker.get_directory_path(
        dialog_title="اختر مكان حفظ ملفات PDF"
    )

    # The rest of the logic happens asynchronously in the pick_directory_result handler
    # and then in the process_pdf_generation thread.