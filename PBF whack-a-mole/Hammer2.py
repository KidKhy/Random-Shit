import time, math, threading
import pydirectinput as pdi, pyautogui as pag, mss, keyboard

# ---------------------- constants you might tweak ----------------------
TARGET_RGB        = (89, 54, 213)
COLOR_TOL         = 30
SEARCH_STEP       = 5
MIN_DIST          = 70
LOCKOUT_TIME      = 1.8
HAMMER_CD         = 0
DRAG_MIN_TIME     = 0.002
POST_WAIT         = 0.05
SCAN_DELAY        = 0.004
PIXEL_STEP        = 5
# autoclicker interval in seconds
AUTOCLICK_INTERVAL = 0.05
# ----------------------------------------------------------------------

# disable failsafe and pauses
pdi.FAILSAFE = False
pdi.PAUSE    = 0
pag.PAUSE    = 0

# set up and start background autoclicker
autoclicker_stop = threading.Event()
def autoclicker():
    while not autoclicker_stop.is_set():
        pdi.click()
        time.sleep(AUTOCLICK_INTERVAL)
auto_thread = threading.Thread(target=autoclicker, daemon=True)
auto_thread.start()

# grab primary monitor dimensions
with mss.mss() as sct:
    MON = sct.monitors[1]
    WIDTH, HEIGHT = MON["width"], MON["height"]


def colour_dist(c):
    return abs(c[0] - TARGET_RGB[0]) + abs(c[1] - TARGET_RGB[1]) + abs(c[2] - TARGET_RGB[2])


def drag(x0, y0, x1, y1, duration):
    if duration == 0:
        pdi.moveTo(x1, y1)
        return
    dx, dy = x1 - x0, y1 - y0
    steps  = max(1, max(abs(dx), abs(dy)) // PIXEL_STEP)
    pause  = max(duration / steps, 0.001)
    for s in range(1, steps + 1):
        pdi.moveTo(x0 + dx * s // steps, y0 + dy * s // steps)
        time.sleep(pause)

last_click_time = 0.0
last_pos        = None
cur_x, cur_y    = pag.position()

print("Running — press Esc to stop")
try:
    with mss.mss() as sct:
        while not keyboard.is_pressed("esc"):
            # look for Play button image first, click if found
            try:
                play = pag.locateCenterOnScreen(
                    r"C:\\Users\\zache\\OneDrive\\Desktop\\PBF\\Play.png",
                    confidence=0.8
                )
            except pag.ImageNotFoundException:
                play = None

            if play:
                pdi.moveTo(play.x, play.y)
                pdi.moveRel(1, 0); pdi.moveRel(-1, 0)
                pdi.click()
                time.sleep(POST_WAIT)
                continue

            # existing color-based hover logic and hole detection
            frame = sct.grab(MON)
            target = None
            for y in range(0, HEIGHT, SEARCH_STEP):
                for x in range(0, WIDTH, SEARCH_STEP):
                    b, g, r = frame.pixel(x, y)[:3]
                    if colour_dist((r, g, b)) <= COLOR_TOL:
                        if last_pos and math.hypot(x-last_pos[0], y-last_pos[1]) < MIN_DIST:
                            continue
                        target = (x, y)
                        break
                if target:
                    break

            if not target:
                time.sleep(SCAN_DELAY)
                continue

            now = time.time()
            if now - last_click_time < HAMMER_CD:
                time.sleep(SCAN_DELAY)
                continue

            tx, ty = target
            if colour_dist(frame.pixel(tx, ty)[:3][::-1]) > COLOR_TOL:
                time.sleep(SCAN_DELAY)
                continue

            # move cursor to hole, autoclicker will handle the clicks
            drag(cur_x, cur_y, tx, ty, DRAG_MIN_TIME)
            cur_x, cur_y = tx, ty

            last_click_time = time.time()
            last_pos        = (tx, ty)
            time.sleep(SCAN_DELAY)

except KeyboardInterrupt:
    pass
finally:
    # stop autoclicker thread
    autoclicker_stop.set()
    auto_thread.join()

print("Stopped")
