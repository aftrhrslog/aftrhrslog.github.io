# Body design pass — August 2026

Open `preview/index.html` in a browser to see the home page without running
Hugo. It loads the real `assets/css/main.css` and the real hero images, with the
note rows hardcoded.

## What changed

**assets/css/main.css** — one new section appended at the end, "Design pass —
body". Nothing above it was edited, so reverting means deleting that block.

- Measure 68ch → 60ch, body 1.1875rem/1.72 → 1.125rem/1.62. 68ch on Newsreader
  ran to about 80 characters a line.
- `--ink-meta: #465355` replaces `--ink-soft` for small labels; the old value was
  borderline on mint at 13px.
- The page under the desk fades beige → mint (`main.page` gradient), so the desk
  does not stop at a hard edge.
- Everything sits on an 8px grid: 2px borders, 8-on/8-off dashed rules, 8px
  square bullets and tag markers, blur-free offset shadows (8px on Now, 4px on a
  hovered note row).
- Section labels are IBM Plex Mono, uppercase, preceded by an 8px square.
- Now keeps its own box, now a 2px blue border with a hard shadow instead of the
  rounded card with a left accent bar.
- Tags are square chips: thin rule, mono uppercase label, 8px colour square. The
  five tag colours survive as the square only, so the top of Notes is calmer.
- Note rows are bordered blocks that gain a border and a hard shadow on hover,
  instead of hairline-separated blocks.
- Below 600px: 22px gutters, Now drops to 16px padding and a 4px shadow, rows
  tighten to 12px.

**layouts/_default/baseof.html** — `<main class="wrap">` became
`<main class="page"><div class="wrap">`, so the gradient can span the sheet while
the text keeps its measure.

**layouts/index.html** — the home list is now the six most recent notes in the
same row shape as /notes/, with descriptions. The old one-note-per-tag block is
kept in `layouts/index-by-tag.html.txt` if you prefer it.

**layouts/_default/list.html** — tag before date in the meta line, and the date
in ISO form to match the mono setting.

**layouts/partials/head.html** — IBM Plex Mono added as its own request.

## Not changed

The hero, its animation, the cat sprite sheet, all content, search, and the
build workflow.
