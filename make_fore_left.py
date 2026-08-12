"""Cut the left window pane's foreground mask out of the artwork.

The left slice of sky (art x 0-137) is the only one with something standing in
front of it, so its drifting cloud strip has to be covered again by the tree.
This writes static/img/fore-left.png, the alpha mask that does the covering.

The mask is a measurement rather than a drawing.  For each row of the slice the
sky's own colour is fitted as a straight line in x -- a painted sky is a smooth
gradient, a tree is not -- and each pixel's alpha is how far it sits from that
fitted colour.  The painter's anti-aliased leaf edges therefore survive as
partial alpha, so a cloud is seen through the edge of a leaf by exactly the
amount that edge was already translucent, and no hard boundary is introduced
anywhere for a seam to show up at.

Which pixels count as sky is decided once on the day picture, where the sky is
unambiguous.  The colour distance is then measured separately on day, sunset
and night and the three alphas combined with max, so a pixel is only let go if
all three hours agree it is sky.

Run from the site root:  python3 make_fore_left.py
Requires numpy, pillow, opencv-python.  The artwork is only read, never
written; re-running is safe and reproduces the same file byte for byte.
"""
import os

import cv2
import numpy as np
from PIL import Image

X0, X1 = 0, 137        # sky runs to x=137; the near window post starts at 138
Y0, Y1 = 0, 258        # the same band height as .pane in main.css
LO, HI = 9.0, 32.0     # RGB distance from sky at which alpha goes 0 -> 1

day = np.asarray(Image.open("static/img/base.webp").convert("RGB")).astype(float)

r, g, b = day[..., 0], day[..., 1], day[..., 2]
seed = ((b > 150) & (b > r + 60) & (b > g + 40))[Y0:Y1, X0:X1]
seed = cv2.erode(seed.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)

xs = np.arange(X1 - X0, dtype=float)
H = Y1 - Y0

alphas, report = [], []
for name in ["base.webp", "base-sunset.webp", "base-night.webp"]:
    img = np.asarray(Image.open("static/img/" + name).convert("RGB")).astype(float)
    sl = img[Y0:Y1, X0:X1]

    ref = np.full((H, X1 - X0, 3), np.nan)
    for y in range(H):
        m = seed[y]
        if m.sum() < 12:                    # too little clear sky in this row
            continue
        for c in range(3):
            k, d = np.polyfit(xs[m], sl[y][m, c], 1)
            ref[y, :, c] = k * xs + d

    good = ~np.isnan(ref[:, 0, 0])          # unfitted rows borrow the nearest fit
    idx = np.where(good)[0]
    for y in np.where(~good)[0]:
        ref[y] = ref[idx[np.argmin(np.abs(idx - y))]]

    dist = np.linalg.norm(sl - ref, axis=2)
    a = np.clip((dist - LO) / (HI - LO), 0, 1)
    alphas.append(a)
    report.append((name, a.mean(), (a > 0.5).mean()))

alpha = np.max(np.stack(alphas), axis=0)

# A gap between leaves is real sky and must stay open; a lone transparent pixel
# inside solid foliage is a measurement artefact.  Close 1px specks only.
solid = (alpha > 0.5).astype(np.uint8)
closed = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
speck = (closed > 0) & (solid == 0)
alpha[speck] = np.maximum(alpha[speck], 0.85)

# The value has to live in the alpha channel: CSS mask-image reads alpha, so a
# plain greyscale PNG -- whose alpha is 1 everywhere -- masks nothing at all.
m = (alpha * 255).round().astype(np.uint8)
rgba = np.dstack([np.full_like(m, 255)] * 3 + [m])
Image.fromarray(rgba, "RGBA").save("static/img/fore-left.png", optimize=True)

for n, mean, cov in report:
    print("%-18s mean alpha %.3f   opaque %5.1f%%" % (n, mean, cov * 100))
print("combined           mean alpha %.3f   opaque %5.1f%%"
      % (alpha.mean(), (alpha > 0.5).mean() * 100))
print("rows of clear sky above the tree:", int(((alpha > 0.5).sum(axis=1) == 0).sum()))
print("static/img/fore-left.png",
      os.path.getsize("static/img/fore-left.png"), "bytes", m.shape[::-1])
