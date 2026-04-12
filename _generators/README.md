# Permit Forms and Checklist — Generators

This folder holds the two single-source Python generators that produce the
Oʻen Maui permit checklists. **Edit the HTML file as source of truth**, then
re-run the matching generator to refresh the PDF. Do not edit the PDF directly.

## Files in this folder

- `build_bpc_pdf.py` — parses
  `Oʻen Maui — Building Permit Submission Checklist.html`
  and writes the matching `.pdf` next to it.
- `build_sma_checklist.py` — data lives inline in this script; it writes
  **both** the SMA HTML and the SMA PDF.

## Usage

From a terminal on your Mac:

```bash
cd "~/Documents/Ø'en MAUI Architecture + Design/Admin/Permit Forms and Checklist/_generators"

# After editing the BPC HTML, regenerate the PDF:
python3 build_bpc_pdf.py

# After editing build_sma_checklist.py data, regenerate both SMA outputs:
python3 build_sma_checklist.py
```

Both scripts auto-detect whether they're running on the Mac or in a sandbox
and pick the right paths.

## Requirements

- Python 3.10+
- `reportlab` (`pip install reportlab`)
- `beautifulsoup4` (`pip install beautifulsoup4`) — only used by the BPC
  generator
- DejaVu Sans TTF fonts at `/usr/share/fonts/truetype/dejavu/` (or the script
  falls back to Helvetica and ʻokina renders as a box — so install
  DejaVu on macOS if not present: `brew install --cask font-dejavu`)

## Versioning rules

- BPC version lives in the HTML header `<div class="doc-meta">` as
  `Rev. April 2026 — v1.X`. Bump it there, add a change-log `<li>` in the
  `.change-banner` block, then rerun `build_bpc_pdf.py`.
- SMA version lives in `build_sma_checklist.py` as `DOC_REV` near the top.
  Bump it there and add an entry to `RECENT_CHANGES`.
- When BPC sections are renumbered, the SMA cross-references must be
  updated in the `SECTIONS` and `XREF_MATRIX` tables at the top of
  `build_sma_checklist.py`.

## Cross-reference convention

- Inside the BPC HTML, SMA cross-references use
  `<span class="tag xref">↔ SMA Phase X</span>` immediately after any
  other tags, followed by a `<div class="note">` that points back to the
  corresponding SMA phase.
- Inside the SMA data model, each item has an `xref` string like
  `↔ BPC § 4 Site Plan` that renders at the end of the item.
- The two documents are designed to read as a matched pair — every task
  in the Special Management Area workflow is tracked in the SMA checklist,
  and referenced (not duplicated) from the BPC checklist.
