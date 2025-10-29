import time, pydirectinput as pdi, pyautogui as pag, mss, keyboard

# fast SendInput
pdi.FAILSAFE = False
pdi.PAUSE    = 0
pag.PAUSE    = 0

# ------------- knobs -------------
THRESHOLD        = 10
SCAN_DELAY       = 0.02
DRAG_MIN_TIME    = 0
PIXEL_STEP       = 4
HOVER_BEFORE     = 0.05
POST_WAIT        = 0.10
HAMMER_CD        = 0.10
SAME_HOLE_BLOCK  = 5.0
# ---------------------------------

HOLES = [
    (597,590,(7,0,5)), (483,747,(8,0,6)), (746,751,(9,0,6)),
    (806,587,(9,1,6)), (962,652,(12,4,9)),(1125,583,(12,3,8)),
    (1167,751,(12,3,7)),(1318,588,(12,1,6)),(1432,749,(13,1,6)),
]

# grab rectangle
xs, ys = [h[0] for h in HOLES], [h[1] for h in HOLES]
LEFT, TOP = min(xs), min(ys)
W, H      = max(xs)-LEFT+1, max(ys)-TOP+1

def pixel_up(img, lx, ly, base):
    b,g,r = img.pixel(lx,ly)[:3]
    return abs(r-base[0])+abs(g-base[1])+abs(b-base[2]) > THRESHOLD

def drag_move(x0,y0,x1,y1,min_time, img, lx,ly, base):
    """drag in PIXEL_STEP hops; abort if pixel drops during drag"""
    dx,dy = x1-x0, y1-y0
    steps = max(1, max(abs(dx),abs(dy))//PIXEL_STEP)
    pause = max(min_time/steps, 0.001)
    for s in range(1, steps+1):
        pdi.moveTo(x0 + dx*s//steps, y0 + dy*s//steps)
        time.sleep(pause)
        if not pixel_up(img, lx, ly, base):
            return False   # mole vanished
    return True            # still up

per_hole_last = [0.0]*len(HOLES)
last_any = 0.0
last_idx = None
cur_x,cur_y = pag.position()

print("Running — Esc to stop")
try:
    with mss.mss() as sct:
        while not keyboard.is_pressed("esc"):
            now = time.time()
            frame = sct.grab({"left":LEFT,"top":TOP,"width":W,"height":H})

            # list of holes currently up
            up_list = [ i for i,(x,y,base) in enumerate(HOLES)
                         if pixel_up(frame,x-LEFT,y-TOP,base) ]

            # skip frame if none or ALL 9 holes look up (likely false flood)
            if len(up_list) == 0 or len(up_list) == len(HOLES):
                time.sleep(SCAN_DELAY)
                continue

            for idx in up_list:
                x,y,base = HOLES[idx]
                if idx == last_idx:                          continue
                if now - per_hole_last[idx] < SAME_HOLE_BLOCK: continue
                if now - last_any < HAMMER_CD:               continue

                # smooth drag, abort if pixel drops en‑route
                if not drag_move(cur_x,cur_y,x,y,DRAG_MIN_TIME,
                                 frame, x-LEFT, y-TOP, base):
                    break  # mole vanished; restart scan

                cur_x,cur_y = x,y

                # hover while re‑checking
                t0 = time.time()
                stay = True
                while time.time()-t0 < HOVER_BEFORE:
                    px = sct.grab({"left":x,"top":y,"width":1,"height":1})
                    if not pixel_up(px,0,0,base):
                        stay = False
                        break
                    time.sleep(0.005)

                if stay:
                    pdi.click()
                    time.sleep(POST_WAIT)
                    per_hole_last[idx] = last_any = time.time()
                    last_idx = idx
                break  # after attempt, restart scan

            time.sleep(SCAN_DELAY)

except KeyboardInterrupt:
    pass
print("Stopped")
