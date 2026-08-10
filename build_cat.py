#!/usr/bin/env python3
"""Turn the 6x6 sprite sheet into one horizontal strip.

The sheet is a plain, evenly timed loop: 36 cells, read left to right and top
to bottom.  Cells are exactly 463 x 532 with no gutters.

Registration, measured across all 36 cells:
  front paws  x 52-252, identical in every frame  -> body centre x = 152
  paw line    y 517                               -> ground line
  ears        y 0-34    (head bob)
  tail        x 391-462 (swing)

Scale is chosen so the paw span matches the previous sprite (109 px at a
1672-wide hero), which keeps the cat's footprint on the desk unchanged.
"""

from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/mnt/user-data/uploads/animation-sequence.png")
OUT = Path("/home/claude/site/static/img")

COLS, ROWS = 6, 6
CW, CH = 463, 532
FRAMES = COLS * ROWS

FPS = 7                          # even beat for every frame
REST = (3, 15, 27)               # zero-based: the tail is on the floor here
HOLD = 4.0                       # seconds the cat sits still on a rest frame

FW = 380                         # chosen frame width, in hero pixels
SCALE = FW / CW                  # 0.82 — still a reduction from the source
FH = round(CH * SCALE)
BODY_CX = 152 * SCALE            # body centre inside the frame
GROUND = 517 * SCALE             # paw line inside the frame


def main():
    sheet = Image.open(SRC).convert("RGBA")
    assert sheet.size == (CW * COLS, CH * ROWS), sheet.size

    strip = Image.new("RGBA", (FW * FRAMES, FH), (0, 0, 0, 0))
    for i in range(FRAMES):
        r, c = divmod(i, COLS)
        cell = sheet.crop((c * CW, r * CH, (c + 1) * CW, (r + 1) * CH))
        strip.paste(cell.resize((FW, FH), Image.LANCZOS), (i * FW, 0))

    OUT.mkdir(parents=True, exist_ok=True)
    strip.save(OUT / "cat-strip.webp", quality=66, method=6)
    strip.crop((FW * REST[1], 0, FW * (REST[1] + 1), FH)).save(
        OUT / "cat-still.webp", quality=88, method=6)

    print(f"frame        {FW} x {FH}   (scale {SCALE:.4f})")
    print(f"body centre  {BODY_CX:.1f} px from the left of the frame")
    print(f"ground line  {GROUND:.1f} px from the top  ->  {100*GROUND/FH:.2f}%")
    print(f"strip        {FW * FRAMES} x {FH}")
    step = 1 / FPS
    total = FRAMES * step + len(REST) * HOLD
    stops, t = [], 0.0
    for i in range(FRAMES):
        stops.append(f"  {100 * t / total:8.4f}% {{ transform: translateX({-100 * i / FRAMES:.4f}%); }}")
        t += step + (HOLD if i in REST else 0)
    stops.append(f"  100.0000% {{ transform: translateX({-100 * (FRAMES - 1) / FRAMES:.4f}%); }}")
    Path("/home/claude/cat-keyframes.css").write_text(
        "@keyframes cat-reel {\n" + "\n".join(stops) + "\n}\n")

    print(f"strip        {FW * FRAMES} x {FH}")
    print(f"loop         {total:.4f}s  ({FRAMES} frames at {1000*step:.1f}ms"
          f" + {len(REST)} rests of {HOLD}s)")
    print(f"frozen frame translateX({-100 * REST[1] / FRAMES:.4f}%)")
    for n, cx, gy, sc in [("p1", 471, 928, 1), ("p2", 812, 858, 1),
                          ("p3", 1275, 918, 1), ("p4", 1510, 660, .85)]:
        w, h = FW * sc, FH * sc
        print(f"  .{n}  left {100*(cx - BODY_CX*sc)/1672:.4f}%  "
              f"top {100*(gy - GROUND*sc)/941:.4f}%  width {100*w/1672:.4f}%")
    print(f"  shadow centre {100*BODY_CX/FW:.2f}%  paw width {100*200*SCALE/FW:.2f}%"
          f"  ground {100*GROUND/FH:.2f}%")


if __name__ == "__main__":
    main()
