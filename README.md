# Safaa El Ouafi — portfolio

Source backup of my interactive portfolio, built as a Claude design canvas
("Safaa El Ouafi — Portfolio & Resume"). Different jobs. Same obsession.

The pages are designed as canvas artboards (`project/*.dc.html`). The deployable
website is generated from them into `site/`.

## The website

- `site/` — the static site: `/`, `/dust`, `/dust/letter`, `/timeline`, `/about`, `/resume` and `/work/<project>`.
- `site/dc.js` — the small script that renders each page in the browser. While the podcast plays, it swaps pages in place so the audio never stops.
- `assets/tldr.js` — the TL;DR ◖)) podcast player in the navbar. To publish the episode: put the MP3 in `assets/audio/`, set `src` (and the transcript) at the top of the file, rebuild.
- `scripts/build_site.py` — rebuilds `site/` from `project/` (`python3 scripts/build_site.py`). It also refreshes `var DOC` in `Main.dc.html`: how well each case is documented, which the search uses to rank results.
- `vercel.json` — tells Vercel to serve `site/` as is, with no build step (preset: Other).

## Case studies are content

Each case study lives in `content/cases/<id>.json` and is edited from `/admin` (Decap CMS). `scripts/cases.py` writes `project/Case-*.dc.html` from those files on every build, so don't edit the case pages directly. Setup and daily use: `docs/CONTENT-STUDIO.md`.

## What is here

- `project/Main.dc.html` — home: the three thematic journeys, the jobs-to-be-done search, Outside the job title. Holds the project records.
- `project/Dust.dc.html` — the Safaa × Dust landing page.
- `project/DustLetter.dc.html` — the cover letter view.
- `project/Case-cassandre.dc.html` — the Cassandre case study.
- `project/Connections.dc.html` — shared component: threads and "This connects to" on case pages.
- `project/canvas.json` — the canvas index (all artboards and their layout).
- `assets/Safaa_El_Ouafi_Cover_Letter_Dust.pdf` — the cover letter PDF.
- `scripts/` — the generators: `data.py` (themes, curated connections), `letter.py` (canonical letter text, used for both the HTML view and the PDF), and the build scripts.

## Recovered from the canvas export

- `project/Timeline.dc.html`, `project/About.dc.html`, `project/Resume.dc.html` and the 34 other `project/Case-*.dc.html` case studies — rebuilt from the canvas's HTML export (same content, re-serialised by the export). `scripts/unpack.py` is the script that unpacks an export.
- `export/site-pages.html` — the canvas's own standalone export of the "Site" pages. Opens in a browser.

All 42 artboards listed in `project/canvas.json` are in this repository.
