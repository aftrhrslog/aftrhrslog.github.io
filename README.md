## Running it

```
hugo server
```

Hugo **0.140.2 or newer**, extended edition. The extended build is needed for
the CSS pipeline (`minify` + `fingerprint`).

## Before you publish

1. In `hugo.toml`, change `baseURL` to your own `https://<username>.github.io/`.
2. In `content/about.md`, fill in the GitHub and email lines.
3. Push to `main`. The workflow in `.github/workflows/deploy.yml` builds and
   deploys. In the repository settings, set **Pages → Source → GitHub Actions**.

## The Now section

`content/now/` holds one file per update, named for the day it was written:

```
content/now/2026-08-01.md
```

```yaml
---
date: 2026-08-01
---

- one line
- another line
```

Keep the filename and the `date` in step — the filename is what sorts the
folder for you, and `date` is what the site actually reads.

The newest file is what the home page shows; everything older is listed at
`/now/`. Individual entries deliberately get no page of their own — the
`cascade` block in `content/now/_index.md` turns rendering off for them, so the
archive is the only place they appear.

Nothing here touches the five Notes tags. Now is a snapshot of a moment, not a
subject, so it lives on its own axis.

## Writing a note

Drop a Markdown file into `content/notes/`:

```yaml
---
title: "A title"
date: 2026-08-10
tags: ["Thoughts"]
description: "One or two sentences. Used as the list summary and the meta description."
---
```

Tags are fixed at five: `Thoughts`, `Purchases`, `Research`, `Leisure`, `Misc`.
Each has its own colour in `assets/css/main.css` (search for `.tag-`). If you
add a sixth tag it will render in a neutral grey until you give it a colour.

A contents box appears automatically on notes over 180 words that have more
than one heading. `description` overrides the auto-generated summary.

## How the hero works

The artwork is `static/img/base.webp`, 1672 × 941. Every coordinate in the CSS
is a percentage of that, so the whole scene scales as one piece.

**Sizing.** The sheet is capped at 960px, so the artwork is never drawn larger
than that and the page keeps one measure from header to footer. Wider windows
get canvas either side.

Height does the rest. The hero is `clamp(300px, min(540px, 56.28vw), 82vh)`
tall, and the stage is `max(100%, height x 1.7768)` wide. Above about 533px the
height follows the width and the whole drawing fits; below it the height stops
shrinking, the stage holds its size, and a little more is trimmed from each
side with every pixel lost.

That floor replaces what used to be stepped crop breakpoints at 1200px and
768px. The steps made the drawing jump *larger* as the window narrowed, which
is the one thing a responsive image should never do. The scale now only ever
decreases; verified across nineteen widths from 1920 down to 320.

The `160.7vh` term in the sheet width only bites on a short window, where it
keeps the top of the sky from being cropped away.

**Clouds.** `clouds-near.webp` and `clouds-far.webp` are strips 1672 × 260,
composed from blobs cut out of the original cloud drawing and placed with
wrap-around, so each tiles seamlessly. Two copies sit side by side in a track
that translates by -50%; the near layer takes 210s, the far one 420s.

One pane per visible slice of sky — the centre light and the narrow one on the
right. Both panes hold the same full-width track at the same offset, which is
what keeps a cloud lined up as it passes behind a window post. The strips fade
to nothing above the ridge, so clouds never meet the mountains and there is no
hard cut line anywhere.

The left sliver of sky is left alone: the tree fills almost all of it, and the
top of the artwork is cropped away on most screens anyway.

**The cat.** One sheet of 36 drawings, 380 x 437 per frame, played straight
through at 7 frames per second. Three frames put the tail flat on the floor
(4, 16 and 28); the cat holds each of those for four seconds, which makes the
17.1s loop feel like a cat settling rather than a looping sprite.

The strip is moved with `translateX`, not `background-position`. Percentage
background positions are measured against (box width - image width), which does
not divide evenly into 36 and lands between frames; `translateX` is measured
against the strip's own width, so one frame is exactly 100/36 of a turn. The
keyframes use `step-end` so a single frame can be held while the rest keep an
even beat.

Four spots, chosen at random on every page load:

| | Centre x | Ground y | |
| --- | --- | --- | --- |
| `p1` | 471 | 928 | desk, left of the laptop |
| `p2` | 812 | 858 | on the laptop keyboard — the no-JS default |
| `p3` | 1275 | 918 | beside the plant |
| `p4` | 1510 | 660 | on the books, at 0.85 scale |

Phones draw from `p1`, `p2` and `p3`; `p4` falls outside the trim entirely.
The trim is centred, so at 390px the visible artwork runs from x 224 to x 1448
and `p3` loses up to 81px from the end of its tail — the body is whole down to
344px. Below that the body starts to clip too, but 320px phones are rare
enough to live with. Every
spot is anchored by the front paws, which sit at x 52-252 and y 517 in *every*
frame of the source sheet — so the cat meets the desk exactly wherever it is
placed, and the elliptical CSS contact shadow lines up without adjustment.

To move a spot, run `build_cat.py` and copy the percentages it prints; to change
the speed or the resting frames, edit `FPS`, `REST` and `HOLD` at the top of
that script and paste the keyframes it writes into `main.css`.

**Motion.** Everything stops under `prefers-reduced-motion: reduce`, and an
IntersectionObserver pauses the animations whenever the hero is off screen.

## Rebuilding the assets

`build_assets.py` regenerates the cloud strips and the background;
`build_cat.py` regenerates the cat strip and the 404 still. Both need `pillow`
(the first also needs `numpy` and `opencv-python`) and expect the source art
beside them.

## Search

Hugo writes `index.json` at the site root — one record per note and per Now
entry, with the title, date, tags and the full plain text. The search page
fetches it on the first keystroke and filters in the browser; nothing is
fetched until someone actually searches, so the index costs the rest of the
site nothing.

Matching is plain substring, all terms required, no fuzzy matching: a typo
finds nothing rather than finding the wrong thing. Title matches sort above
body matches, then newest first. Results show a window of text around the
first hit with the terms marked.

At 500 notes of 400 words the index is roughly 1.5 MB, about 350 KB over the
wire — lighter than the cat. If it ever does get heavy, the fix is to send
less per record (swap `.Plain` for a truncated version in
`layouts/index.json`) rather than to split the file.

## What is deliberately absent

No RSS, no analytics, no comments, no dark mode, no cookies. The
only JavaScript on the site is the twenty lines that place the cat and pause
the animations.
