
import time
import cv2
import numpy as np
import pytesseract
from windows_capture import WindowsCapture

pytesseract.pytesseract.tesseract_cmd = (
    "C:/Program Files/Tesseract-OCR/tesseract.exe"
)

reference_width = 1920
reference_height = 991

REGION = {
    "x": 1450,
    "y": 220,
    "width": 310,
    "height": 30
}

def start(hwnd, sendcoords):

    print("Starting Hytale Windows Graphics Capture...")

    last_capture = 0

    capture = WindowsCapture(
        cursor_capture=False,
        draw_border=False,
        window_hwnd=hwnd,
        minimum_update_interval=200
    )

    @capture.event
    def on_frame_arrived(frame, capture_control):

        nonlocal last_capture

        current_time = time.monotonic()

        if current_time - last_capture < 1:
            return

        last_capture = current_time

        full_image = frame.frame_buffer.copy()

        frame_height, frame_width = full_image.shape[:2]

        # Calculate scaling
        scale_x = frame_width / reference_width
        scale_y = frame_height / reference_height

        x = round(REGION["x"] * scale_x)
        y = round(REGION["y"] * scale_y)

        width = round(REGION["width"] * scale_x)
        height = round(REGION["height"] * scale_y)

        # Crop OCR region
        image = full_image[
            y:y + height,
            x:x + width
        ]

        if image.size == 0:
            print("Invalid OCR region!")
            return

        # OpenCV
        image = cv2.cvtColor(
            image,
            cv2.IMREAD_GRAYSCALE
        )

        gray = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
        



        text = pytesseract.image_to_string(
            gray,
            config="--psm 7 -c tessedit_char_whitelist=0123456789-., "
        )
        coords = []
        coords.append(text[0:7])
        print(text[0:7])
        coords.append(text[7:15])
        print(text[7:15])
        coords.append(text[15:25])
        print(text[15:25])
        sendcoords(coords)

        # Debug screenshot
        cv2.imwrite("debug_screenshot.png", image)
        cv2.imwrite("debug_screenshot_gray.png", gray)
       # cv2.imwrite("debug_screenshot_enlarged.png", enlarged)

       # print("Detected:", text.strip())

        cv2.imshow("Hytale OCR Region", image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            capture_control.stop()

        #Store the coords in a list
       # coords.append(int(text[0:7]))
       # coords.append(int(text[10:15]))
        #coords.append(int(text[18:26]))
       # print(text[1:7])
       # print(text[9:15])
        #print(text[16:23])


    @capture.event
    def on_closed():
        print("Hytale capture closed")

    try:
        capture.start()
    finally:
        cv2.destroyAllWindows()
        print("Coordinate detection stopped.")


