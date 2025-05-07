# logic/qr_scanner.py
import cv2
from pyzbar.pyzbar import decode

def scan_qr_code_continuous(on_detect):
    """
    Captures from camera, calls on_detect(data) whenever a new QR is read.
    """
    cap = cv2.VideoCapture(0)
    last_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for barcode in decode(frame):
            qr_data = barcode.data.decode('utf-8')
            if qr_data != last_data:
                on_detect(qr_data)
                last_data = qr_data

        cv2.imshow('QR Scanner (q to quit)', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
