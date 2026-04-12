# Maui Permit Checklists

A free community resource published and maintained by
[Oʻen Maui Architecture + Design](https://oenmaui.com).

**Live site:** https://permits.oenmaui.com

These are the permit checklists Oʻen Maui uses in its own practice, cleaned up, cross-referenced,
and published openly so anyone on the island can use them. They cover the two permit processes
that trip up the most projects on Maui:

- **Building Permit Submission Checklist** — everything a complete building permit package for a
  new residential project needs before submission through the County's MAPPS portal.
- **Maui SMA Permit Checklist** — a phase-by-phase walk-through of the Special Management Area
  process under HRS 205A, up to date with the 2024 Maui Island Shoreline Rule update, the
  Erosion Hazard Line, and the Act 125 of 2025 timeline changes.

The two checklists are designed to be read together. Items that trigger parallel review in the
other checklist are tagged inline so you can cross-reference them without losing your place.

## This is educational, not legal or regulatory advice

These checklists are educational summaries of publicly available Maui County and State of
Hawaiʻi permitting requirements. They are provided as-is, without warranty of any kind, and
are not a substitute for the current requirements published by Maui County (DPW, Planning,
SHPD), the State of Hawaiʻi (DLNR, DOH), or any other agency with jurisdiction over your
project.

**Rules change.** Every update on this site is recorded with a date and a change-log entry in
[`CHANGELOG.md`](CHANGELOG.md). Before you rely on any item for a submission, confirm it against
the current published requirement from the relevant agency.

If you are unsure whether an item applies to your project, talk to a licensed professional or
the permitting agency directly.

## Updates and how to report issues

The checklists are reviewed and updated on a **quarterly** cadence. If you find an error,
something out of date, or an edge case the checklists don't cover well, please let us know:

- Open a thread in [**GitHub Discussions**](../../discussions) — preferred, so the community
  can see and learn from the exchange.
- Or email us directly at **studio@oenmaui.com**.

We try to acknowledge urgent issues faster than the quarterly cycle.

## How the documents are built

Both checklists are generated from Python scripts in [`_generators/`](_generators/) so that the
HTML and the PDF are always in sync with a single source of truth.

- `build_sma_checklist.py` generates the SMA HTML and PDF in one pass.
- `build_bpc_pdf.py` parses the hand-maintained Building Permit HTML and renders the matching
  PDF.

See [`_generators/README.md`](_generators/README.md) for the full build notes.

## License

The generator code in [`_generators/`](_generators/) is released under the MIT License — see
[`LICENSE`](LICENSE).

The checklist content itself (the HTML pages, the PDFs, and the landing page copy) is released
under **Creative Commons Attribution 4.0** (CC BY 4.0). You are free to share and adapt the
checklists for any purpose, including commercially, as long as you give appropriate credit to
Oʻen Maui Architecture + Design and indicate if changes were made.

## About Oʻen Maui Architecture + Design

Oʻen Maui is a small boutique architecture and design practice based on Maui, doing careful,
locally grounded work. If you need help going from checklist to permitted project, we're a
short email away at **studio@oenmaui.com**, or visit us at [oenmaui.com](https://oenmaui.com).
