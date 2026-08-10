#!/usr/bin/env python3
"""Build hero assets

Outputs into site/static/img/:
  base.webp          hero background, 1672x941
  clouds-far.webp    far cloud strip, 1672x260, seamless horizontally
  clouds-near.webp   near cloud strip, 1672x260, seamless horizontally

Cloud strips are composed only from blobs cut out of main_clouds.png -
no cloud pixel is drawn procedurally.  Blobs are placed with wrap-around
so the strip tiles seamlessly, and alpha fades to zero before the strip
bottom so clouds never meet the mountain ridge.
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

SRC = Path(__file__).parent / "src-art"
OUT = Path(__file__).parent / "static/img"
OUT.mkdir(parents=True, exist_ok=True)

ART_W, ART_H = 1672, 941
STRIP_W, STRIP_H = ART_W, 260
FADE_TOP, FADE_BOT = 222, 252      # alpha ramps 1 -> 0 across these rows
SKY = np.array([54, 156, 247], dtype=float)

rng = np.random.default_rng(7)


# --------------------------------------------------------------------------
# cloud blobs
# --------------------------------------------------------------------------
def cut_blobs():
    """Return every cloud blob from the source as its own RGBA crop."""
    src = np.array(Image.open(SRC / "main_clouds.png"))
    alpha = src[:, :, 3]
    solid = (alpha > 24).astype(np.uint8)
    grouped = cv2.dilate(solid, np.ones((9, 9), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(grouped, 8)

    blobs = []
    for i in range(1, count):
        x, y, w, h, area = stats[i]
        if area < 900:
            continue
        crop = src[y:y + h, x:x + w].copy()
        keep = (labels[y:y + h, x:x + w] == i)
        crop[:, :, 3] = np.where(keep, crop[:, :, 3], 0)
        blobs.append({"img": crop, "w": w, "h": h, "area": int(area)})

    blobs.sort(key=lambda b: -b["area"])
    return blobs


def scaled(blob, factor, flip=False):
    im = Image.fromarray(blob["img"], "RGBA")
    w = max(1, int(round(blob["w"] * factor)))
    h = max(1, int(round(blob["h"] * factor)))
    im = im.resize((w, h), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return np.array(im).astype(float)


def paste_over(canvas, patch, x, y):
    """Alpha-over composite, wrapping horizontally at STRIP_W."""
    ph, pw = patch.shape[:2]
    for dx in (-STRIP_W, 0, STRIP_W):
        px = x + dx
        x0, x1 = max(0, px), min(STRIP_W, px + pw)
        if x0 >= x1:
            continue
        y0, y1 = max(0, y), min(STRIP_H, y + ph)
        if y0 >= y1:
            continue
        sub = patch[y0 - y:y1 - y, x0 - px:x1 - px]
        dst = canvas[y0:y1, x0:x1]
        sa = sub[:, :, 3:4] / 255.0
        da = dst[:, :, 3:4] / 255.0
        out_a = sa + da * (1 - sa)
        safe = np.where(out_a > 0, out_a, 1)
        dst[:, :, :3] = (sub[:, :, :3] * sa + dst[:, :, :3] * da * (1 - sa)) / safe
        dst[:, :, 3:4] = out_a * 255


def build_strip(blobs, factor, placements, haze, opacity, name):
    canvas = np.zeros((STRIP_H, STRIP_W, 4), dtype=float)

    for idx, x, y, flip in placements:
        patch = scaled(blobs[idx], factor, flip)
        if haze > 0:                      # atmospheric perspective
            patch[:, :, :3] += (SKY - patch[:, :, :3]) * haze
        paste_over(canvas, patch, x, y)

    # fade to nothing before the ridge, so there is never a hard cut line
    ramp = np.ones(STRIP_H)
    band = np.arange(FADE_TOP, FADE_BOT)
    ramp[FADE_TOP:FADE_BOT] = 1 - (band - FADE_TOP) / (FADE_BOT - FADE_TOP)
    ramp[FADE_BOT:] = 0
    canvas[:, :, 3] *= ramp[:, None] * opacity

    img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA")
    img.save(OUT / name, quality=82, method=6)
    return img


def main():
    blobs = cut_blobs()
    print(f"{len(blobs)} cloud blobs cut")
    for i, b in enumerate(blobs[:10]):
        print(f"  {i}: {b['w']}x{b['h']}  area {b['area']}")

    # ---- near layer: the three big cumulus plus one medium bank ----------
    # index, x, y, flip     (y is the top of the blob inside the strip)
    # Vertical spread matters more than horizontal here: banks sitting at the
    # same height read as one rigid strip sliding past.
    near = [
        (0, 40, 90, False),
        (2, 690, 150, True),
        (1, 1160, 117, False),
        (5, 480, 191, False),
    ]
    build_strip(blobs, 0.50, near, haze=0.0, opacity=0.85, name="clouds-near.webp")

    # ---- far layer: streaks and small puffs, hazed and translucent -------
    far = [
        (3, 60, 143, False),
        (6, 330, 111, True),
        (4, 520, 186, False),
        (7, 820, 131, False),
        (9, 1010, 199, True),
        (8, 1180, 119, False),
        (10, 1380, 164, True),
        (11, 1520, 101, False),
        (12, 220, 207, True),
        (13, 900, 176, False),
        (14, 1290, 94, True),
        (15, 640, 158, False),
    ]
    build_strip(blobs, 0.35, far, haze=0.28, opacity=0.55, name="clouds-far.webp")

    # ---- background ------------------------------------------------------
    base = Image.open(SRC / "main_base_clean.png").convert("RGB")
    assert base.size == (ART_W, ART_H)
    base.save(OUT / "base.webp", quality=82, method=6)

    # The cat is built separately, by build_cat.py.

    for f in sorted(OUT.iterdir()):
        print(f"{f.name:20} {f.stat().st_size / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
