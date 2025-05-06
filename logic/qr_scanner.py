import cv2
from pyzbar.pyzbar import decode

def handle_qr_data(data):
    # This is the function that gets called whenever a QR code is detected
    print(f"📦 Detected QR Code data: {data}")

def scan_qr_code_continuous():
    cap = cv2.VideoCapture(0)
    last_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_this_frame = False
        for barcode in decode(frame):
            qr_data = barcode.data.decode('utf-8')

            # Call function if new QR code detected (different from last one)
            if qr_data != last_data:
                handle_qr_data(qr_data)
                last_data = qr_data

            # Draw rectangle
            pts = barcode.polygon
            if pts:
                pts = [(pt.x, pt.y) for pt in pts]
                pts.append(pts[0])
                for i in range(len(pts) - 1):
                    cv2.line(frame, pts[i], pts[i + 1], (255, 0, 0), 2)

            # Display detected data
            cv2.putText(frame, qr_data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            detected_this_frame = True

        cv2.imshow('QR Code Scanner (Press Q to quit)', frame)

        # Quit on 'q' key press
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
