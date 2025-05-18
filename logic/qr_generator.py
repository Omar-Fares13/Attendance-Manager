import qrcode
import io
 

def generate_qr_code(data):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create image and save it to a BytesIO buffer
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()  # In-memory buffer
    img.save(img_buffer, format="PNG")  # Save the image to the buffer
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer
