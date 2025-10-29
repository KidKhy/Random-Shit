import time, math, pydirectinput as pdi, pyautogui as pag, mss, keyboard

# ---------------------- constants you might tweak ----------------------
TARGET_RGB        = (89, 54, 213)
COLOR_TOL         = 25
SEARCH_STEP       = 5
MIN_DIST          = 100
LOCKOUT_TIME      = 2.5
HAMMER_CD         = 0
DRAG_MIN_TIME     = 0.002
POST_WAIT         = 0.05
SCAN_DELAY        = 0.005
PIXEL_STEP        = 6
PLAY_IMG          = r"C:\Users\zache\OneDrive\Desktop\PB\Play.png"  # <─ new
# ----------------------------------------------------------------------

pdi.FAILSAFE = False
pdi.PAUSE    = 0
pag.PAUSE    = 0

with mss.mss() as sct:
    MON = sct.monitors[1]
    WIDTH, HEIGHT = MON["width"], MON["height"]

def colour_dist(c):
    return abs(c[0]-TARGET_RGB[0])+abs(c[1]-TARGET_RGB[1])+abs(c[2]-TARGET_RGB[2])

def drag(x0, y0, x1, y1, duration):
    if duration == 0:
        pdi.moveTo(x1, y1); return
    dx, dy = x1 - x0, y1 - y0
    steps  = max(1, max(abs(dx), abs(dy)) // PIXEL_STEP)
    pause  = max(duration / steps, 0.001)
    for s in range(1, steps + 1):
        pdi.moveTo(x0 + dx * s // steps, y0 + dy * s // steps)
        time.sleep(pause)

last_click_time = 0.0
last_pos        = None
cur_x, cur_y    = pag.position()

print("Running — Esc quits, Play button has priority")
try:
    while not keyboard.is_pressed("esc"):

        # ---------- Play‑button priority ----------
        try:
            btn = pag.locateCenterOnScreen(PLAY_IMG, confidence=0.90)
        except pag.ImageNotFoundException:
            btn = None
        if btn:
            drag(cur_x, cur_y, btn.x, btn.y, DRAG_MIN_TIME)  # same drag method
            cur_x, cur_y = btn.x, btn.y
            time.sleep(SCAN_DELAY)
            continue             # skip colour search this frame
        # ------------------------------------------

        frame = sct.grab(MON)

        # -------- find matching violet pixel --------
        target = None
        for y in range(0, HEIGHT, SEARCH_STEP):
            for x in range(0, WIDTH, SEARCH_STEP):
                if colour_dist(frame.pixel(x, y)[::-1]) > COLOR_TOL:
                    continue
                if last_pos and math.hypot(x-last_pos[0], y-last_pos[1]) < MIN_DIST:
                    continue
                target = (x, y)
                break
            if target: break

        if not target:
            time.sleep(SCAN_DELAY); continue
        if time.time() - last_click_time < HAMMER_CD:
            time.sleep(SCAN_DELAY); continue
        # -------------------------------------------

        tx, ty = target
        drag(cur_x, cur_y, tx, ty, DRAG_MIN_TIME)
        cur_x, cur_y = tx, ty

        # pag.click()  # ← still disabled
        time.sleep(POST_WAIT)

        last_click_time = time.time()
        last_pos        = (tx, ty)

        time.sleep(SCAN_DELAY)

except KeyboardInterrupt:
    pass
print("Stopped")
