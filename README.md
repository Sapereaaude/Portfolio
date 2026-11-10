# Safaa El Ouafi — portfolio

Source backup of my interactive portfolio, built as a Claude design canvas
("Safaa El Ouafi — Portfolio & Resume"). Different jobs. Same obsession.

These files are canvas artboards (`.dc.html`). They need the canvas runtime to
render, so this repository is a backup of the code, not a deployable website.

## What is here

- `project/Main.dc.html` — home: the three thematic journeys, the jobs-to-be-done search, Outside the job title. Holds the project records.
- `project/Dust.dc.html` — the Safaa × Dust landing page.
- `project/DustLetter.dc.html` — the cover letter view.
- `project/Case-cassandre.dc.html` — the Cassandre case study.
- `project/Connections.dc.html` — shared component: threads and "This connects to" on case pages.
- `project/canvas.json` — the canvas index (all artboards and their layout).
- `assets/Safaa_El_Ouafi_Cover_Letter_Dust.pdf` — the cover letter PDF.
- `scripts/` — the generators: `data.py` (themes, curated connections), `letter.py` (canonical letter text, used for both the HTML view and the PDF), and the build scripts.

## Not here yet

The 34 other case studies, the career timeline, the About page and the resume
are listed in `canvas.json` but their files still live only in the canvas.
