# Change log

All notable changes to the Maui Permit Checklists are tracked here. This log is
updated as part of the quarterly review cycle and any out-of-cycle fixes.

## 2026-04 (out-of-cycle) — July 2026 permit reform notes added

- New page published at `updates/july-2026-permit-reforms.html` covering three
  Hawaiʻi state laws passed in 2025 that affect Maui County permitting:
  **Act 295 (SB 66)**, the expedited permit pathway for single-family and
  multi-family housing (effective July 1, 2026, sunsets June 30, 2031);
  **Act 293 (SB 15)**, the Chapter 6E historic-review amendment (already in
  effect as of July 3, 2025); and **Act 306 (HB 830)**, the SHPD third-party
  consultant valve (operative provisions effective July 1, 2026).
- The page is written in plain language for design professionals, homeowners,
  and contractors, and explicitly calls out two frequent misreadings — that
  Act 295 applies to any delayed permit, and that Act 293 eliminates historic
  review for anything not on a register. Neither is correct.
- Landing page (`index.html`) gains a heads-up callout linking to the new
  page, sitting between the existing disclaimer and the checklist cards.
- Building Permit Submission Checklist (`checklists/building-permit.html`)
  gains a heads-up note at the top of the page chrome flagging the Act 295
  pathway for qualifying inland housing projects.
- Maui SMA Permit Checklist (`checklists/sma-permit.html`) gains a heads-up
  note explaining that Act 295 **does not** reach shoreline work — the
  expedited pathway expressly excludes shoreline parcels and parcels impacted
  by waves, storm waves, high tide, or shoreline erosion, so the SMA process
  remains the path for coastal projects. This asymmetric framing between the
  two checklist pages is intentional.
- The quarterly maintenance review scheduled for July 1, 2026 will revisit
  the new page and flip the framing from "coming" to "in effect" when the
  operative laws actually take hold.

## 2026-04 — Initial public launch

- Building Permit Submission Checklist **v1.4** and Maui SMA Permit Checklist **v1.2**
  published as a free community resource at permits.oenmaui.com.
- Both checklists are cross-referenced: items in the Building Permit Checklist that
  trigger parallel SMA review are tagged with `↔ SMA Phase X` chips, and SMA items
  that affect the Building Permit submission carry `↔ BPC § X` chips in return.
- Source of truth for both documents is the Python generators in `_generators/`.

### Maui SMA Permit Checklist v1.2 (April 2026)

- Erosion Hazard Line (EHL) is now the default shoreline setback line under the
  2024 Maui Island Shoreline Rule update. Phase 1 was reordered so the
  "EHL mapped or not" check happens **before** any decision about ordering a
  certified shoreline survey.
- Phase 4 item on certified shoreline surveys rewritten. Under the 2024 rule,
  where the EHL is mapped it **is** the default shoreline setback line and no
  certified shoreline survey is required. A survey is now only needed when:
  1. The EHL is unmapped for the parcel;
  2. The project team is requesting an alternate setback on an accreting or
     geologically erosion-resistant lot; or
  3. A Shoreline Setback Variance is being filed under HRS 205A-43.
- The former "abuts the shoreline → survey" trigger has been removed.

### Maui SMA Permit Checklist v1.1 (April 2026)

- Cross-referenced with Building Permit Checklist v1.4. All `↔ BPC § X`
  cross-references re-numbered to match the BPC v1.3/v1.4 section structure
  (Civil/Grading is now § 10, Agency Approvals § 11, Frequently Flagged § 12).

### Building Permit Submission Checklist v1.4 (April 2026)

- Reverse `↔ SMA Phase X` cross-reference tags added inline so the Building
  Permit Checklist and the SMA Permit Checklist now read as a matched pair.
- New "Frequently Flagged" § 12 QC item covering the SMA cross-check.

### Building Permit Submission Checklist v1.3 (April 2026)

- New § 7 Building Separation added, shifting previous §§ 7–11 down one
  number.

---

## How this log is maintained

Every update — quarterly or out-of-cycle — gets an entry here **before** it goes
live. Each entry lists what changed, why, and a source. The public history of
this file is the public audit trail for the checklists.

If you find an error or something out of date, please open a thread in
[GitHub Discussions](../../discussions) or email **studio@oenmaui.com**.
