import qrcode

def generate_qr_code(data, filename='qr_code.png'):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,  # Controls size of QR code (1 is smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create image and save
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✅ QR code saved as '{filename}' with data: {data}")

# Example usage
generate_qr_code("Fsocity", filename='test_qr.png')
