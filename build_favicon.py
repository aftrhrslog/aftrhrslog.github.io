#!/usr/bin/env python3
"""Cut the pixel-art house down to a set of icons.

The source draws on a 16 px grid, so the crop is snapped to that grid before
anything is resized — otherwise the house ends up half a block off centre and
the windows lose their symmetry.

Small sizes are resampled smoothly rather than by nearest neighbour: at 16 px
a 42-block drawing cannot keep its grid, and a smooth reduction reads better
than a shattered one.
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

SRC = Path("/mnt/user-data/uploads/favicon.png")
OUT = Path(__file__).parent / "static"

GRID = 16           # the artwork's pixel block, in source pixels
PAD = 0.07          # breathing room around the house, as a share of the side
MINT = (233, 243, 238)


def square_crop():
    im = Image.open(SRC).convert("RGBA")
    a = np.array(im)
    solid = (a[:, :, 3] > 16).astype(np.uint8)

    # The chimney smoke floats free of the house and, if it is framed in,
    # pushes the house down to about two thirds of the square.  At 16 px the
    # smoke is invisible anyway, so the crop follows the largest connected
    # blob — the house with its bushes — and lets the smoke fall outside.
    count, labels, stats, _ = cv2.connectedComponentsWithStats(solid, 8)
    biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    ys, xs = np.where(labels == biggest)

    x0, x1 = xs.min(), xs.max() + 1
    y0, y1 = ys.min(), ys.max() + 1
    x0 -= x0 % GRID
    y0 -= y0 % GRID
    x1 += (-x1) % GRID
    y1 += (-y1) % GRID

    side = max(x1 - x0, y1 - y0)
    side += 2 * (int(side * PAD) // GRID + 1) * GRID          # keep it on grid

    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    box = (cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)

    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im.crop(box), (0, 0))
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    art = square_crop()
    print(f"square source {art.size[0]} px  ({art.size[0] // GRID} blocks)")

    art.resize((512, 512), Image.LANCZOS).save(OUT / "icon-512.png")
    art.resize((192, 192), Image.LANCZOS).save(OUT / "icon-192.png")

    # iOS ignores transparency and composites on black, so give it a ground
    touch = Image.new("RGB", (180, 180), MINT)
    inner = art.resize((156, 156), Image.LANCZOS)
    touch.paste(inner, (12, 12), inner)
    touch.save(OUT / "apple-touch-icon.png")

    art.resize((48, 48), Image.LANCZOS).save(
        OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    for f in ["favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png"]:
        print(f"  {f:24} {(OUT / f).stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
