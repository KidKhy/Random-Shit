import time
import pyautogui
import keyboard          # pip install keyboard
import mss               # pip install mss

pyautogui.FAILSAFE = True     # move mouse to a corner to quit

def get_pixel_rgb(x, y):
    """grab one pixel quickly, handles both BGR and BGRA tuples"""
    with mss.mss() as sct:
        box = {"top": y, "left": x, "width": 1, "height": 1}
        pixel = sct.grab(box).pixel(0, 0)
    b, g, r = pixel[:3]
    return r, g, b

print("Running…")
print(" • Hover over any spot and press F8 to show its RGB.")
print(" • Press Esc (or move the pointer into a screen corner) to quit.\n")

try:
    while True:
        if keyboard.is_pressed("esc"):
            break

        if keyboard.is_pressed("f8"):
            x, y = pyautogui.position()
            rgb = get_pixel_rgb(x, y)
            print(f"Pixel at ({x}, {y})  ->  RGB {rgb}")
            time.sleep(0.3)        # debounce the key so it prints once

        time.sleep(0.05)           # light CPU load

except KeyboardInterrupt:
    pass

print("Stopped")
