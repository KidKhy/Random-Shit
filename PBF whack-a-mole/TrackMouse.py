import time
import pyautogui

print("Tracking the mouse. Press Ctrl+C to stop.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"X {x}  Y {y}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped")
