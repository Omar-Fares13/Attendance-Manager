from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a font that supports Arabic (adjust path if needed)
pdfmetrics.registerFont(
    TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
)

def generate_report_pdf(
    out_path,
    name_ar,
    student_id,
    department,
    ums_level,
    train_acc,
    test_acc
):
    c = canvas.Canvas(out_path)
    text = c.beginText(40, 800)
    text.setFont('DejaVuSans', 12)
    text.textLine(f"Name: {name_ar}")
    text.textLine(f"Student ID: {student_id}")
    text.textLine(f"Department: {department}")
    text.textLine(f"UMS Level: {ums_level}")
    text.textLine("")  # blank line
    text.textLine(f"Training Accuracy: {train_acc:.4f}")
    text.textLine(f"Testing Accuracy: {test_acc:.4f}")
    c.drawText(text)
    c.save()

if __name__ == "__main__":
    generate_report_pdf(
        out_path="2021170363.pdf",
        name_ar="عمر ماهر فتحي حامد",
        student_id="2021170363",
        department="SC",
        ums_level="4",
        train_acc=1.0000,
        test_acc=0.8750
    )
