#Requires AutoHotkey v2.0
CoordMode("Pixel","Screen")

; after your globals (top of the script)
watching := true
SetTimer(WatchTick, intervalMs)           ; actually start the loop
TrayTip("Ammo watcher","ON",800)          ; optional
TraySetToolTip("Ammo watcher: ON")        ; optional

; --- Pixels to watch ---
topX := 621, topY := 99,  topRGB := 0xC59E00
botX := 621, botY := 126, botRGB := 0xFFCC00

tol := 0            ; 0 = exact match; raise to 4–8 if shade varies
intervalMs := 30    ; check rate
cooldownMs := 200   ; min delay between Q taps

; globals/state
global watching := false
global lastDrop := 0

; Toggle ON/OFF  (Ctrl+Alt+S)
^!s::
{
    global watching, intervalMs
    watching := !watching
    SetTimer(WatchTick, watching ? intervalMs : 0)
    TrayTip("Ammo watcher", watching ? "ON" : "OFF", 800)
}

; Quit (optional)
Esc::ExitApp

WatchTick(*) {
    global topX, topY, topRGB, botX, botY, botRGB, tol, lastDrop, cooldownMs
    if PixelMatches(topX, topY, topRGB, tol) || PixelMatches(botX, botY, botRGB, tol) {
        now := A_TickCount
        if (now - lastDrop >= cooldownMs) {
            Send "q"
            lastDrop := now
        }
    }
}

PixelMatches(x, y, want, t) {
    cur := PixelGetColor(x, y, "RGB")
    if (t = 0)
        return (cur = want)
    curR := (cur >> 16) & 0xFF, curG := (cur >> 8) & 0xFF, curB := cur & 0xFF
    wr   := (want >> 16) & 0xFF, wg   := (want >> 8) & 0xFF, wb  := want & 0xFF
    return Abs(curR - wr) <= t && Abs(curG - wg) <= t && Abs(curB - wb) <= t
}
