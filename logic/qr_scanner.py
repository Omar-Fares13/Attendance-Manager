import cv2
from pyzbar.pyzbar import decode
import time

def scan_qr_code_continuous(on_detect):
    """
    Captures from camera, calls on_detect(data) whenever a new QR is read.
    Press 'q' in the window or click the close button to stop scanning.
    Draws a bounding box around detected QR codes and displays the decoded data.
    """
    cap = cv2.VideoCapture(0)
    last_data = None
    last_detection_time = 0
    detection_cooldown = 1.0  # Minimum time between detections in seconds

    window_title = 'QR Scanner (press q to quit)'
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        
        # Decode any QR codes in the frame
        for barcode in decode(frame):
            qr_data = barcode.data.decode('utf-8')
            
            # Only process if enough time has passed since last detection
            if current_time - last_detection_time >= detection_cooldown:
                # Draw bounding box around the barcode
                x, y, w, h = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Put the decoded text above the rectangle
                cv2.putText(
                    frame,
                    qr_data,
                    (x, y - 10 if y - 10 > 10 else y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

                # Notify once per new QR code
                if qr_data != last_data:
                    on_detect(qr_data)
                    last_data = qr_data
                    last_detection_time = current_time

        # Overlay instructions
        cv2.putText(
            frame,
            "Press 'q' to quit",
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # Show the frame
        cv2.imshow(window_title, frame)

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
