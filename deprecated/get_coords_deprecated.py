import time
import cv2
import mss
import numpy as np
import win32gui
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = (
    "C:/Program Files/Tesseract-OCR/tesseract.exe"
)
reference_width = 1920
reference_height = 991

REGION = {"x": 633, "y": 115, "width": 194, "height": 90}

def start(hwnd):
    with mss.mss() as sct:
        while True:
            if not win32gui.IsWindow(hwnd):
                print("hytale gone")
                break
            client_rect = win32gui.GetClientRect(hwnd) #0 0 1280 720
            client_width = client_rect[2] - client_rect[0] # 1280 - 0
            client_height = client_rect[3] - client_rect[1] # 720 - 0

            if client_width <= 0 or client_height <= 0:
                print("invalid dimensions")
                break



            #calculate scaling

            scale_x = client_width / reference_width #1280/1920 = 0.67
            scale_y = client_height / reference_height

            x = round(REGION["x"] * scale_x)
            y = round(REGION["y"] * scale_y)
            width = round(REGION["width"] * scale_x)
            height = round(REGION["height"] * scale_y) 



            #referencing client to screen
            client_left, client_top = win32gui.ClientToScreen(hwnd, (0,0))
            capture = {
                "left": client_left + x, 
                "top": client_top + y ,
                "width": width,
                "height": height
            }
            #screenshot

            screenshot = np.array(sct.grab(capture))


            #opencv

            image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            enlarged = cv2.resize(
                gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC
            )

            #ocr
            text = pytesseract.image_to_string(
                enlarged, config="--psm 7"

            )
            cv2.imwrite("debug_screenshot.png", image)
            print("Detected: ", text.strip())
            cv2.imshow("hytale ss region", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(1)
    cv2.destroyAllWindows()
    print("coordinate detection stopped")
