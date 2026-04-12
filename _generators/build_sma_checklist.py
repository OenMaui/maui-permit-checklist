#!/usr/bin/env python3
"""
Oʻen Maui Architecture + Design — SMA Permit Submission Checklist Builder
Generates matching HTML and PDF versions from a single data source.

Brand-matched to the existing Building Permit Submission Checklist so the two
documents can be used as sister checklists in tandem.
"""

import html as htmlmod
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, KeepTogether,
    PageBreak, HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Register DejaVu Sans so Unicode glyphs like ʻokina render correctly
_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Body",         f"{_FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold",    f"{_FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Body-Oblique", f"{_FONT_DIR}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("Body-BoldOblique", f"{_FONT_DIR}/DejaVuSans-BoldOblique.ttf"))
registerFontFamily(
    "Body",
    normal="Body",
    bold="Body-Bold",
    italic="Body-Oblique",
    boldItalic="Body-BoldOblique",
)
FONT_REG  = "Body"
FONT_BOLD = "Body-Bold"
FONT_IT   = "Body-Oblique"
FONT_BI   = "Body-BoldOblique"

# ----------------------------------------------------------------------------
# BRAND CONSTANTS (matched to Building Permit Checklist)
# ----------------------------------------------------------------------------
BRAND_NAME       = "Oʻen Maui Architecture + Design"
DOC_TITLE        = "SMA Permit Submission Checklist"
DOC_SUBTITLE     = "County of Maui Planning Department — Special Management Area"
DOC_SCOPE        = "HRS Ch. 205A · MC-12 Ch. 202 (eff. Aug 25, 2024) · Act 125 (2025)"
DOC_REV          = "Rev. April 2026 — v1.2"
DOC_SISTER       = "Sister document to the Building Permit Submission Checklist"
PREPARED_BY      = "Erik Thorup, Architect · erik@oenmaui.com · 808.446.6999"

COLOR_ACCENT     = HexColor("#0d4f6e")
COLOR_ACCENT2    = HexColor("#2b7a9c")
COLOR_INK        = HexColor("#1f2a36")
COLOR_MUTED      = HexColor("#5a6875")
COLOR_BG         = HexColor("#f6f4ef")
COLOR_CARD       = HexColor("#ffffff")
COLOR_LINE       = HexColor("#d9d3c4")
COLOR_REQ        = HexColor("#b5121b")
COLOR_COND       = HexColor("#b36b00")
COLOR_NEW        = HexColor("#116530")
COLOR_XREF       = HexColor("#4a1f6e")
COLOR_HIGHLIGHT  = HexColor("#fff6d6")
COLOR_HIGHLIGHT_BORDER = HexColor("#e0b400")
COLOR_XREF_BG    = HexColor("#efeaf5")

# ----------------------------------------------------------------------------
# CHECKLIST DATA MODEL
# Each item: (id, flags[], text, note_or_None, xref_or_None)
# Flags: "REQ" | "COND" | "NEW" | "XREF"
# xref = short "↔ BPC § X" string
# ----------------------------------------------------------------------------

RECENT_CHANGES = [
    ("v1.2 — Erosion Hazard Line is the default setback line (2024 Shoreline Rule update)",
     "Phase 1 reordered so the EHL mapped/unmapped check happens BEFORE any "
     "decision about ordering a certified shoreline survey. Phase 4 item on "
     "certified shoreline surveys rewritten: under the 2024 Maui Island "
     "Shoreline Rule update, where the EHL is mapped it IS the default "
     "shoreline setback line and no certified shoreline survey is required. "
     "A survey is now only needed when (1) the EHL is unmapped for the "
     "parcel, (2) the team requests an alternate setback on an accreting or "
     "erosion-resistant lot, or (3) a Shoreline Setback Variance is being "
     "filed. The former \"abuts the shoreline → survey\" trigger has been removed."),
    ("v1.1 — Cross-referenced with Building Permit Checklist v1.4 (Apr 2026)",
     "All ↔ BPC § X cross-references re-numbered to match BPC v1.3/v1.4 "
     "section structure (Civil/Grading is now § 10, Agency Approvals § 11, "
     "Frequently Flagged § 12). The Building Permit Checklist was given "
     "reverse ↔ SMA Phase X tags so the two documents now read as a matched "
     "pair."),
    ("Act 125 (effective May 29, 2025)",
     "Amended HRS 205A-22. Minor Permit valuation ceiling is now $750,000 "
     "for non-shoreline parcels, but only $500,000 for shoreline parcels or "
     "parcels impacted by waves, storm surge, high tide, or shoreline erosion. "
     "Above these amounts → Major / SMA Use Permit."),
    ("Maui SMA Rules amended Aug 25, 2024 (MC-12, Chapter 202)",
     "Clarified categorical exemptions; expressly stated that single-family "
     "residences are not categorical exemptions (though they may still be "
     "found exempt after assessment); tightened treatment of repair / "
     "renovation scope, ground disturbance, and cumulative effects."),
    ("MAPPS-only filing",
     "Maui Planning Department no longer accepts paper SMA applications. "
     "All filings go through the online MAPPS portal, and a processed Land "
     "Use Designation (LUD) form must be attached to any SMA Use Permit filing."),
    ("Shoreline setback / erosion",
     "Maui's shoreline framework now embeds projected erosion and 3.2 ft of "
     "sea-level rise into the Erosion Hazard Line used for setback "
     "determinations — directly relevant to most South Maui oceanfront parcels."),
    ("Legacy PDF packets are stale",
     "Some County PDFs still cite the pre-2025 $500,000 general Major "
     "threshold. Use current MAPPS guidance and Act 125 language, not the "
     "legacy packets."),
]

# Section is a dict: title, subtitle, items
SECTIONS = [
    {
        "num": "1",
        "title": "Parcel Due Diligence & Overlay Screening",
        "subtitle": "Before any design commitment or valuation work. South Maui "
                    "coastal parcels frequently carry multiple overlapping overlays.",
        "items": [
            ("p1-01", ["REQ"],
             "Confirm parcel lies within the mapped Maui SMA boundary (County SMA maps / MAPPS lookup).",
             "SMA approval is the first permit required for development in the SMA — other agencies should not authorize development first.",
             "↔ BPC § 4 Site Plan (SMA notation) · § 11 Agency Approvals"),
            ("p1-02", ["REQ"],
             "Pull current TMK report: zoning, community plan designation, state land use district, flood zone, shoreline overlays, special districts.",
             None,
             "↔ BPC § 4 Site Plan"),
            ("p1-03", ["REQ"],
             "Obtain a processed Land Use Designation (LUD) form through MAPPS.",
             "Required attachment for any SMA Use Permit filing. File the LUD request early — it is a separate MAPPS workflow.",
             None),
            ("p1-04", ["REQ"],
             "Identify whether the parcel is a shoreline parcel or is impacted by waves, storm surge, high tide, or shoreline erosion.",
             "This determination controls whether the $500,000 or $750,000 Minor threshold applies under Act 125.",
             None),
            ("p1-05", ["REQ"],
             "Determine whether the parcel has a mapped Erosion Hazard Line (EHL) using the County's published Maui Island EHL mapping.",
             "This check drives every downstream shoreline decision and must happen BEFORE ordering any certified shoreline survey. The EHL was modeled by the UH Climate Resilience Collaborative (projected erosion + 3.2 ft sea-level rise) with minor County adjustments for accreting or geologically stable shorelines.",
             "↔ BPC § 4 Site Plan (coastal setback)"),
            ("p1-06", ["REQ"],
             "Record the resulting default shoreline setback line based on the EHL check in p1-05.",
             "If the EHL is mapped, the EHL itself is the default setback line — under the 2024 Maui Island Shoreline Rule update, no certified shoreline survey is required in this default case. If the EHL is NOT mapped for the parcel, the default setback reverts to 200 ft (or an optional lot-depth-based formula), and a state-certified shoreline survey under HRS 205A will be needed in Phase 4 to establish the baseline.",
             "↔ BPC § 4 Site Plan (coastal setback)"),
            ("p1-07", ["COND"],
             "Flag whether the project team intends to request an alternate shoreline setback (e.g., lot is accreting or known to be geologically erosion-resistant).",
             "If yes, a state-certified shoreline survey will also be required in Phase 4 — the EHL distance is then applied from the certified shoreline instead of from the default EHL line. If the Planning Director agrees the shoreline is accreting or erosion-resistant, the setback may instead be established using the unmapped-EHL method.",
             None),
            ("p1-08", ["REQ"],
             "Confirm FEMA flood zone and whether any proposed work would trigger a Flood Development Permit.",
             "If required, the Flood Permit must issue before an SMA Exemption or Minor Permit approval.",
             "↔ BPC § 4 Site Plan (flood zone designation)"),
            ("p1-09", ["COND"],
             "Screen for tsunami inundation, coastal dune, wetland, estuary, and geologically hazardous overlays.",
             "These feed directly into the County's significance criteria and can push a project into Major.",
             None),
            ("p1-10", ["COND"],
             "Check for mapped cultural / historic / archaeological resources or iwi kūpuna sensitivity in the vicinity.",
             None,
             "↔ BPC § 4 Site Plan (SHPD) · § 11 SHPD review"),
            ("p1-11", ["REQ"],
             "Verify consistency with County General Plan, Maui Island Plan, applicable Community Plan (South Maui), and zoning.",
             "Inconsistency may require a concurrent plan amendment. South Maui Community Plan update is still underway.",
             None),
        ],
    },
    {
        "num": "2",
        "title": "Threshold Determination — Is This \"Development\"?",
        "subtitle": "The first legal question is not cost — it is whether the "
                    "activity is \"development\" under HRS 205A. Only then does "
                    "it sort into Exempt / Minor / Major.",
        "items": [
            ("p2-01", ["REQ"],
             "Test scope against the HRS 205A definition of \"development\" (placement of structures, grading, dredging, mining, change in density/intensity, substantial changes in appearance of land or water, etc.).",
             None, None),
            ("p2-02", ["REQ", "NEW"],
             "Check the 2024-amended categorical exemptions list in MC-12 Ch. 202 before assuming exempt status.",
             "The 2024 rules clarified several exemptions and confirmed that single-family residences are not categorical exemptions.",
             None),
            ("p2-03", ["COND"],
             "For repair / renovation / like-for-like work, confirm no new ground disturbance, no expansion of scope, and no cumulative effect that would pull the work back into SMA review.",
             None, None),
            ("p2-04", ["REQ"],
             "Prepare a defensible valuation estimate (construction cost basis) for the proposed development.",
             None,
             "↔ BPC § 1 PS-Form A (construction value)"),
            ("p2-05", ["REQ", "NEW"],
             "Apply current Act 125 thresholds: Minor ≤ $750,000 on non-shoreline parcels · Minor ≤ $500,000 on shoreline or impacted parcels · Above → Major / SMA Use Permit.",
             "For most South Maui oceanfront sites, the operative ceiling is $500,000.",
             None),
            ("p2-06", ["REQ"],
             "Independently assess whether the project may have a substantial adverse environmental or ecological effect (cumulative effects included). If yes → Major, regardless of valuation.",
             None, None),
            ("p2-07", ["COND"],
             "Flag \"Major-risk\" characteristics even if cost is low: seawalls/revetments, shoreline hardscape, major grading, new structures near shoreline, mapped erosion/flood exposure, access impacts, habitat/cultural concerns, or controversial public interest.",
             None, None),
        ],
    },
    {
        "num": "3",
        "title": "SMA Assessment Filing (MAPPS)",
        "subtitle": "The SMA Assessment is the first practical filing on Maui. "
                    "The Planning Director uses it to determine Exempt / Minor / "
                    "Major / Emergency / Inconsistent.",
        "items": [
            ("p3-01", ["REQ"],
             "Ownership documentation and owner's authorization (if applicant is not owner).",
             None,
             "↔ BPC § 1 Ownership & Authorization"),
            ("p3-02", ["REQ"],
             "TMK, parcel area, and location map.",
             None, None),
            ("p3-03", ["REQ"],
             "Scaled development / site plan showing all sensitive features (shoreline, setback line, flood zone boundary, drainage, access, vegetation, cultural features).",
             None,
             "↔ BPC § 4 Site Plan (all subitems)"),
            ("p3-04", ["COND"],
             "Floor plans, sections, and elevations for any new or expanded structures.",
             None,
             "↔ BPC § 5 Architectural"),
            ("p3-05", ["REQ"],
             "Site photographs (existing conditions, shoreline, access, adjacent uses).",
             None, None),
            ("p3-06", ["REQ"],
             "Written project description and construction valuation estimate.",
             None, None),
            ("p3-07", ["REQ"],
             "Written impact analysis addressing HRS 205A-26 criteria: coastal resources, shoreline access, drainage, wastewater, erosion/flood/SLR exposure, views, landforms, cultural resources, cumulative impacts, plan/zoning consistency.",
             "This is where most applications succeed or fail — it builds the administrative record.",
             None),
            ("p3-08", ["REQ"],
             "Signed zoning / flood confirmation form.",
             None, None),
            ("p3-09", ["REQ"],
             "Attach the processed LUD form.",
             None, None),
            ("p3-10", ["COND"],
             "Chapter 343 (HEPA) materials (EA/EIS or agency decision documents) if environmental review is triggered.",
             None, None),
            ("p3-11", ["COND"],
             "Comments previously received from agencies or community organizations.",
             None, None),
            ("p3-12", ["REQ"],
             "Submit the entire package through MAPPS online portal (paper not accepted).",
             None,
             "↔ BPC § 1 MAPPS submission method"),
            ("p3-13", ["COND"],
             "Respond to Director's circulation to reviewing agencies (typical 30-day comment window).",
             None, None),
            ("p3-14", ["REQ"],
             "Provide applicant responses to agency comments until the Department deems the application complete.",
             None, None),
            ("p3-15", ["REQ"],
             "Receive written Director determination (Exempt / Minor / Major / Emergency / Inconsistent) within 30 calendar days of completeness.",
             None, None),
        ],
    },
    {
        "num": "4",
        "title": "Parallel Coastal & Environmental Reviews",
        "subtitle": "Almost every South Maui coastal project triggers at least "
                    "one of these alongside the SMA track.",
        "items": [
            ("p4-01", ["COND"],
             "File for Shoreline Setback Approval / Determination (SSAD) for work allowed within the shoreline setback area.",
             None,
             "↔ BPC § 4 Site Plan (coastal setback)"),
            ("p4-02", ["COND"],
             "File for Shoreline Setback Variance (SSV) for structures or activities not otherwise permitted in the setback area.",
             None, None),
            ("p4-03", ["COND"],
             "Obtain a state-certified shoreline survey (HRS 205A, DLNR) ONLY if one of three triggers applies; otherwise skip — the EHL is the default setback line.",
             "Under the 2024 Maui Island Shoreline Rule update, a certified shoreline survey is required only when: (1) the parcel has no mapped EHL and you need to establish the baseline for the default 200 ft / lot-depth-based setback; (2) the project team is requesting an alternate setback on an accreting or geologically erosion-resistant lot, in which case the EHL horizontal distance is measured from the certified shoreline instead; or (3) a Shoreline Setback Variance (SSV) is being filed under HRS 205A-43. If none of those apply and the EHL is mapped, the former \"abuts the shoreline → order a survey\" requirement has been removed and no survey is needed. Confirm the relevant trigger from Phase 1 items p1-06 and p1-07 before ordering.",
             "↔ BPC § 4 Site Plan (coastal setback)"),
            ("p4-04", ["COND"],
             "File and obtain Flood Development Permit before SMA Exemption or Minor approval issues.",
             None,
             "↔ BPC § 4 Site Plan (FEMA FIRM / BFE)"),
            ("p4-05", ["COND"],
             "Complete Chapter 343 environmental review (EA/EIS) if the project involves state land, state funds, shoreline area, conservation district, historic sites, or other HEPA triggers.",
             None, None),
            ("p4-06", ["COND"],
             "Archaeological Inventory Survey (AIS) / SHPD consultation if cultural resources are implicated.",
             None,
             "↔ BPC § 11 SHPD approval"),
            ("p4-07", ["COND"],
             "Initiate concurrent General Plan / Community Plan / zoning amendment if the Director finds the project inconsistent.",
             None, None),
        ],
    },
    {
        "num": "5A",
        "title": "SMA Minor Permit Path",
        "subtitle": "Use this track only if the Director determines the project "
                    "qualifies as Minor under current Act 125 thresholds AND has "
                    "no substantial adverse effect.",
        "items": [
            ("p5a-01", ["REQ"],
             "Confirm the SMA Assessment can serve as the Minor application (Maui's current procedure).",
             None, None),
            ("p5a-02", ["REQ"],
             "Ensure the impact narrative affirmatively supports the \"no substantial adverse environmental or ecological effect\" finding.",
             None, None),
            ("p5a-03", ["REQ"],
             "Receive Director's written Minor Permit decision (approve / approve with conditions / deny).",
             None, None),
            ("p5a-04", ["COND"],
             "Accept and document any permit conditions (BMPs, erosion control, wastewater, drainage, access, vegetation, etc.).",
             None,
             "↔ BPC § 10 Civil/Grading BMPs"),
            ("p5a-05", ["REQ"],
             "Confirm Director reports the approved Minor Permit to the Maui Planning Commission at its next regular meeting.",
             None, None),
            ("p5a-06", ["COND"],
             "Preserve appeal rights / track appeal window for any aggrieved party.",
             None, None),
        ],
    },
    {
        "num": "5B",
        "title": "SMA Use Permit (Major) Path",
        "subtitle": "Applies if valuation exceeds the Act 125 threshold or the "
                    "project may have a substantial adverse environmental / "
                    "ecological effect. Heard by the Maui Planning Commission.",
        "items": [
            ("p5b-01", ["REQ"],
             "File the SMA Use Permit (SM1) application through MAPPS with fully processed LUD attached.",
             None, None),
            ("p5b-02", ["REQ"],
             "Include all assessment-level materials plus a findings-ready record under HRS 205A-26.",
             None, None),
            ("p5b-03", ["REQ"],
             "Pay applicable Major Use Permit fees.",
             None, None),
            ("p5b-04", ["REQ"],
             "Department circulates to reviewing agencies; applicant responds in writing to all comments.",
             None, None),
            ("p5b-05", ["REQ"],
             "Department confirms the application is complete before scheduling hearing.",
             None, None),
            ("p5b-06", ["REQ"],
             "Prepare Notice of Application; publish after department review.",
             None, None),
            ("p5b-07", ["REQ"],
             "Post a 9 sq ft project sign at the property.",
             None, None),
            ("p5b-08", ["REQ"],
             "Mail hearing notice to owners of record within 500 ft of the subject parcel, not less than 30 calendar days before the hearing.",
             None, None),
            ("p5b-09", ["REQ"],
             "Director publishes public notice of hearing not less than 30 days before the hearing date.",
             None, None),
            ("p5b-10", ["REQ"],
             "Confirm the Department has notified the applicant of the hearing date at least 45 days prior.",
             None, None),
            ("p5b-11", ["REQ"],
             "Prepare a findings-based presentation demonstrating HRS 205A-26 compliance: minimized/offset impacts, consistency with Ch. 205A objectives, consistency with plans and zoning, and appropriate conditions.",
             None, None),
            ("p5b-12", ["COND"],
             "Coordinate testimony, expert witnesses (coastal, civil, cultural, biologist), and exhibits.",
             None, None),
            ("p5b-13", ["REQ"],
             "Attend the Maui Planning Commission hearing.",
             None, None),
            ("p5b-14", ["REQ"],
             "Receive written Decision and Order with terms, conditions, and findings (or denial if criteria not met).",
             None, None),
            ("p5b-15", ["COND"],
             "Track appeal window and preserve the administrative record.",
             None, None),
        ],
    },
    {
        "num": "6",
        "title": "Post-Approval & Sequencing With Building Plans",
        "subtitle": "Tie the SMA outcome into the parallel Building Plan submittal "
                    "workflow. This is where the two sister checklists must "
                    "lock together.",
        "items": [
            ("p6-01", ["REQ"],
             "Transcribe every SMA permit condition into the Building Permit Submission package — specifically into the site plan notes, civil/grading BMPs, and agency approvals section.",
             None,
             "↔ BPC § 4, § 10, § 11"),
            ("p6-02", ["REQ"],
             "Do not submit for Building Permit issuance until SMA approval (and any SSAD/SSV, Flood, Ch. 343) are in hand — other agencies cannot authorize development ahead of SMA.",
             None,
             "↔ BPC § 11 Planning Department / SMA Permit line"),
            ("p6-03", ["COND"],
             "Incorporate erosion control, BMP, drainage, wastewater, and landscape conditions into civil drawings and SWPPP.",
             None,
             "↔ BPC § 10 Civil/Grading BMPs"),
            ("p6-04", ["COND"],
             "Schedule any required pre-construction coastal monitoring, archaeological monitoring, or cultural protocol before ground disturbance.",
             None, None),
            ("p6-05", ["REQ"],
             "Maintain a compliance log of every SMA condition through construction and final inspection.",
             None, None),
            ("p6-06", ["COND"],
             "Track SMA permit expiration / extension rules and request extension before lapse if construction schedule slips.",
             None, None),
            ("p6-07", ["REQ"],
             "File any required final / close-out compliance reports with the Planning Department.",
             None, None),
        ],
    },
    {
        "num": "7",
        "title": "Common Traps — Final QC Pass",
        "subtitle": "Final sanity check — each of these has derailed South Maui "
                    "coastal projects.",
        "items": [
            ("p7-01", ["REQ"],
             "Confirm you are not relying on pre-2025 PDF thresholds ($500K general Major line). Use Act 125 split thresholds.",
             None, None),
            ("p7-02", ["REQ"],
             "Treat shoreline setback review as a parallel, not secondary, workflow.",
             None, None),
            ("p7-03", ["REQ"],
             "Do not assume a single-family residence or a \"repair\" is automatically exempt.",
             None, None),
            ("p7-04", ["REQ"],
             "Verify plan/zoning consistency before design is too far advanced to pivot.",
             None, None),
            ("p7-05", ["REQ"],
             "Document cumulative effects from any prior/adjacent work on the same compound or ownership.",
             None, None),
            ("p7-06", ["REQ"],
             "Confirm valuation basis is defensible and includes the full scope of work (no artificial splitting).",
             None, None),
            ("p7-07", ["REQ"],
             "Confirm the Building Permit Submission Checklist has the SMA reference lines populated in § 4 and § 11 before building permit submittal.",
             None,
             "↔ BPC § 4 + § 11"),
        ],
    },
]

# Cross-reference map section (appears at end)
XREF_MATRIX = [
    ("Phase 1 Due Diligence — SMA overlay, flood zone, shoreline, SHPD screening",
     "BPC § 4 Site Plan (SMA, FEMA flood zone, SHPD notations)"),
    ("Phase 1 LUD form (zoning + community plan + state land use)",
     "BPC § 11 Planning Department approval"),
    ("Phase 2 Threshold — valuation basis",
     "BPC § 1 PS-Form A construction value"),
    ("Phase 3 SMA Assessment — site plan, impact analysis, MAPPS submission",
     "BPC § 4 Site Plan, § 2 MAPPS digital standards"),
    ("Phase 3 Ownership/authorization documents",
     "BPC § 1 Ownership & Authorization, PS-Form B"),
    ("Phase 4 SSAD / SSV — shoreline setback",
     "BPC § 4 Site Plan coastal setback line"),
    ("Phase 4 Flood Development Permit",
     "BPC § 4 Site Plan FEMA flood zone / BFE"),
    ("Phase 4 AIS / SHPD consultation",
     "BPC § 4 Site Plan SHPD, § 11 SHPD approval"),
    ("Phase 5A/5B SMA decision",
     "BPC § 11 SMA Permit line (must precede building permit)"),
    ("Phase 6 Transcription of SMA conditions",
     "BPC § 4 (site plan notes), § 10 (Civil/BMPs), § 11 (Agency approvals)"),
    ("Phase 7 QC pass",
     "BPC § 12 Frequently Flagged QC pass"),
]

SOURCES = (
    "HRS Chapter 205A (Coastal Zone Management Law), Part II Special Management Areas · "
    "HRS § 205A-22 (definitions, as amended by Act 125, 2025) · "
    "HRS § 205A-26 (SMA approval criteria) · "
    "Maui Planning Commission SMA Rules, MC-12 Chapter 202 (amended effective August 25, 2024) · "
    "Maui County Planning Department — MAPPS Customer Self-Service portal (mapps.mauicounty.gov) · "
    "Maui County Planning — Maui Island Shoreline Rule Update (2024), EHL as default shoreline setback line · "
    "Maui County shoreline setback rules and Erosion Hazard Line framework (modeled by UH Climate Resilience Collaborative, projected erosion + 3.2 ft sea-level-rise assumption) · "
    "Maui County General Plan, Maui Island Plan, applicable Community Plans · "
    "Hawaiʻi Environmental Policy Act (HRS Chapter 343) · "
    "Maui County flood hazard rules (Flood Development Permit)"
)

DISCLAIMER = (
    "This checklist reflects publicly available Maui Planning Department "
    "requirements and firm experience as of the revision date. It is a "
    "working procedural tool, not legal advice. Rules, thresholds, and "
    "procedures change — confirm current requirements with the Maui Planning "
    "Department and qualified counsel before filing. Always verify "
    "parcel-specific overlays and current Community Plan status for South "
    "Maui before relying on any threshold determination."
)

# ----------------------------------------------------------------------------
# HTML GENERATION
# ----------------------------------------------------------------------------

def flag_badges_html(flags):
    out = []
    for f in flags:
        cls = {"REQ": "req", "COND": "cond", "NEW": "new"}[f]
        label = {"REQ": "REQ", "COND": "COND", "NEW": "NEW"}[f]
        out.append(f'<span class="flag {cls}">{label}</span>')
    return "".join(out)


def item_html(item):
    iid, flags, text, note, xref = item
    parts = [f'<div class="item"><input type="checkbox" id="{iid}">']
    parts.append(f'<label for="{iid}">')
    parts.append(flag_badges_html(flags))
    parts.append(htmlmod.escape(text))
    if note:
        parts.append(f'<span class="note">{htmlmod.escape(note)}</span>')
    if xref:
        parts.append(f'<span class="xref">{htmlmod.escape(xref)}</span>')
    parts.append("</label></div>")
    return "".join(parts)


def build_html():
    parts = []
    parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Oʻen Maui — SMA Permit Submission Checklist</title>
<style>
  :root{
    --bg:#f6f4ef;
    --ink:#1f2a36;
    --muted:#5a6875;
    --accent:#0d4f6e;
    --accent2:#2b7a9c;
    --required:#b5121b;
    --conditional:#b36b00;
    --new:#116530;
    --xref:#4a1f6e;
    --xref-bg:#efeaf5;
    --card:#ffffff;
    --line:#d9d3c4;
    --highlight:#fff6d6;
    --highlight-border:#e0b400;
  }
  *{box-sizing:border-box;}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
    background:var(--bg);
    color:var(--ink);
    margin:0;
    padding:0 0 80px 0;
    line-height:1.5;
  }
  header{
    background:linear-gradient(135deg,var(--accent) 0%,var(--accent2) 100%);
    color:#fff;
    padding:30px 40px 24px 40px;
    border-bottom:4px solid #083a52;
  }
  .brand{
    font-size:12px;
    letter-spacing:2px;
    text-transform:uppercase;
    opacity:0.9;
    margin-bottom:8px;
  }
  header h1{
    margin:0 0 4px 0;
    font-size:26px;
    letter-spacing:0.2px;
  }
  header .subtitle{
    font-size:14px;
    opacity:0.92;
  }
  header .tagrow{margin-top:10px;}
  header .tag{
    display:inline-block;
    background:rgba(255,255,255,0.15);
    padding:3px 10px;
    border-radius:12px;
    font-size:11.5px;
    margin-right:6px;
    margin-top:6px;
  }
  header .rev{
    position:absolute;top:18px;right:28px;
    font-size:11px;opacity:0.85;
  }
  header{position:relative;}
  main{
    max-width:1080px;
    margin:0 auto;
    padding:22px 28px;
  }
  .projectbar{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:10px;
    padding:14px 18px;
    margin:0 0 18px 0;
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:10px 18px;
    font-size:12px;
  }
  .projectbar .field{
    border-bottom:1px solid var(--line);
    padding-bottom:3px;
  }
  .projectbar .label{
    display:block;
    text-transform:uppercase;
    letter-spacing:1px;
    font-size:9.5px;
    color:var(--muted);
    margin-bottom:2px;
  }
  .legend{
    display:flex;
    flex-wrap:wrap;
    gap:14px;
    background:var(--card);
    border:1px solid var(--line);
    border-radius:10px;
    padding:12px 16px;
    margin:0 0 20px 0;
    font-size:12.5px;
  }
  .legend span{display:inline-flex;align-items:center;gap:6px;}
  .dot{
    width:10px;height:10px;border-radius:50%;display:inline-block;
  }
  .dot.req{background:var(--required);}
  .dot.cond{background:var(--conditional);}
  .dot.new{background:var(--new);}
  .dot.xref{background:var(--xref);}
  .alert{
    background:var(--highlight);
    border:1px solid var(--highlight-border);
    border-left:6px solid var(--highlight-border);
    padding:16px 20px;
    border-radius:8px;
    margin:0 0 22px 0;
  }
  .alert h2{
    margin:0 0 8px 0;
    font-size:16px;
    color:#6b4a00;
  }
  .alert ul{margin:6px 0 0 18px;padding:0;}
  .alert li{margin:4px 0;font-size:13px;}
  .alert li strong{color:#6b4a00;}
  section.phase{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:10px;
    margin:0 0 18px 0;
    padding:18px 24px 10px 24px;
    box-shadow:0 1px 2px rgba(0,0,0,0.03);
    break-inside:avoid;
  }
  section.phase h2{
    margin:0 0 3px 0;
    color:var(--accent);
    font-size:17px;
    border-bottom:2px solid var(--line);
    padding-bottom:7px;
  }
  section.phase .phase-sub{
    color:var(--muted);
    font-size:12.5px;
    margin:5px 0 12px 0;
    font-style:italic;
  }
  .item{
    display:flex;
    align-items:flex-start;
    gap:9px;
    padding:8px 6px;
    border-bottom:1px dashed #e8e3d4;
  }
  .item:last-child{border-bottom:none;}
  .item input[type=checkbox]{
    width:17px;
    height:17px;
    margin-top:3px;
    flex-shrink:0;
    accent-color:var(--accent);
    cursor:pointer;
  }
  .item label{
    flex:1;
    cursor:pointer;
    font-size:13.8px;
  }
  .flag{
    display:inline-block;
    font-size:9.5px;
    font-weight:700;
    letter-spacing:0.4px;
    padding:2px 6px;
    border-radius:10px;
    margin-right:6px;
    vertical-align:1px;
    text-transform:uppercase;
  }
  .flag.req{background:var(--required);color:#fff;}
  .flag.cond{background:var(--conditional);color:#fff;}
  .flag.new{background:var(--new);color:#fff;}
  .item label .note{
    display:block;
    color:var(--muted);
    font-size:12px;
    margin-top:3px;
  }
  .item label .xref{
    display:inline-block;
    background:var(--xref-bg);
    color:var(--xref);
    font-size:10.5px;
    padding:2px 7px;
    margin-top:4px;
    border-radius:3px;
    font-weight:600;
    letter-spacing:0.2px;
  }
  .item input[type=checkbox]:checked + label{
    text-decoration:line-through;
    color:#8a8578;
  }
  .controls{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin:10px 0 16px 0;
  }
  .controls button{
    font-family:inherit;
    font-size:12.5px;
    padding:7px 14px;
    border:1px solid var(--accent);
    background:#fff;
    color:var(--accent);
    border-radius:6px;
    cursor:pointer;
  }
  .controls button:hover{background:var(--accent);color:#fff;}
  .progress{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:8px;
    padding:9px 14px;
    margin:0 0 16px 0;
    font-size:12.5px;
    display:flex;
    align-items:center;
    gap:12px;
  }
  .bar{
    flex:1;
    height:9px;
    background:#e6e1d1;
    border-radius:6px;
    overflow:hidden;
  }
  .bar > div{
    height:100%;
    background:linear-gradient(90deg,#2b7a9c,#0d4f6e);
    width:0%;
    transition:width 0.25s ease;
  }
  .xref-matrix{
    width:100%;
    border-collapse:collapse;
    font-size:12.5px;
    margin-top:8px;
  }
  .xref-matrix th,.xref-matrix td{
    text-align:left;
    border:1px solid var(--line);
    padding:8px 10px;
    vertical-align:top;
  }
  .xref-matrix th{
    background:#eef4f7;
    color:var(--accent);
  }
  .sources{
    background:#fff;
    border:1px solid var(--line);
    border-radius:10px;
    padding:14px 18px;
    margin:0 0 16px 0;
    font-size:11.5px;
    color:var(--muted);
  }
  .sources h3{
    margin:0 0 6px 0;
    color:var(--accent);
    font-size:13px;
  }
  .signoff{
    font-size:11px;
    color:var(--muted);
    margin:14px 0 0 0;
    padding-top:10px;
    border-top:1px solid var(--line);
  }
  @media print{
    body{background:#fff;}
    .controls,.progress{display:none;}
    section.phase{break-inside:avoid;box-shadow:none;border:1px solid #999;}
    header{background:#0d4f6e !important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  }
</style>
</head>
<body>
""")

    parts.append(f"""<header>
  <div class="rev">{htmlmod.escape(DOC_REV)}</div>
  <div class="brand">{htmlmod.escape(BRAND_NAME)}</div>
  <h1>{htmlmod.escape(DOC_TITLE)}</h1>
  <div class="subtitle">{htmlmod.escape(DOC_SUBTITLE)}</div>
  <div class="tagrow">
    <span class="tag">HRS Ch. 205A</span>
    <span class="tag">MC-12 Ch. 202 (eff. Aug 25, 2024)</span>
    <span class="tag">Act 125 (2025)</span>
    <span class="tag">{htmlmod.escape(DOC_SISTER)}</span>
  </div>
</header>
<main>
  <div class="projectbar">
    <div class="field"><span class="label">Project Name</span>&nbsp;</div>
    <div class="field"><span class="label">Address</span>&nbsp;</div>
    <div class="field"><span class="label">TMK</span>&nbsp;</div>
    <div class="field"><span class="label">SMA Assessment No. (if known)</span>&nbsp;</div>
    <div class="field"><span class="label">Architect of Record</span>&nbsp;</div>
    <div class="field"><span class="label">Submission Date</span>&nbsp;</div>
    <div class="field"><span class="label">Prepared By</span>&nbsp;</div>
    <div class="field"><span class="label">Reviewer / Checker</span>&nbsp;</div>
    <div class="field"><span class="label">Filing Type (Exempt / Minor / Major)</span>&nbsp;</div>
  </div>

  <div class="legend">
    <span><span class="dot req"></span> <strong>REQ</strong> — Required</span>
    <span><span class="dot cond"></span> <strong>COND</strong> — Conditional / if triggered</span>
    <span><span class="dot new"></span> <strong>NEW</strong> — Recent rule change</span>
    <span><span class="dot xref"></span> <strong>↔ BPC</strong> — Cross-reference to Building Permit Checklist</span>
  </div>

  <div class="alert">
    <h2>⚠ Recent Rule Changes to Know Before Filing</h2>
    <ul>
""")

    for title, body in RECENT_CHANGES:
        parts.append(f"      <li><strong>{htmlmod.escape(title)}.</strong> {htmlmod.escape(body)}</li>\n")

    parts.append("""    </ul>
  </div>

  <div class="controls">
    <button onclick="checkAll(true)">Check All</button>
    <button onclick="checkAll(false)">Clear All</button>
    <button onclick="window.print()">Print / Save PDF</button>
  </div>

  <div class="progress">
    <span id="progressLabel">0 of 0 complete</span>
    <div class="bar"><div id="progressBar"></div></div>
    <span id="progressPct">0%</span>
  </div>
""")

    for sec in SECTIONS:
        parts.append(f'''
  <section class="phase">
    <h2>Phase {sec["num"]} — {htmlmod.escape(sec["title"])}</h2>
    <div class="phase-sub">{htmlmod.escape(sec["subtitle"])}</div>
''')
        for it in sec["items"]:
            parts.append("    " + item_html(it) + "\n")
        parts.append("  </section>\n")

    # Cross-reference matrix
    parts.append("""
  <section class="phase">
    <h2>Cross-Reference Matrix — SMA ↔ Building Permit Submission Checklist</h2>
    <div class="phase-sub">Read across: each SMA checklist phase ties to one or more sections of the Building Permit Submission Checklist so the two documents move in lockstep.</div>
    <table class="xref-matrix">
      <thead><tr><th style="width:52%">SMA Permit Checklist Item</th><th>Building Permit Submission Checklist Reference</th></tr></thead>
      <tbody>
""")
    for left, right in XREF_MATRIX:
        parts.append(f"        <tr><td>{htmlmod.escape(left)}</td><td>{htmlmod.escape(right)}</td></tr>\n")
    parts.append("      </tbody>\n    </table>\n  </section>\n")

    parts.append(f"""
  <div class="sources">
    <h3>Sources &amp; References</h3>
    {htmlmod.escape(SOURCES)}
  </div>

  <div class="signoff">
    Prepared by {htmlmod.escape(BRAND_NAME)} · {htmlmod.escape(PREPARED_BY)} · {htmlmod.escape(DOC_REV)}<br>
    {htmlmod.escape(DISCLAIMER)}
  </div>
</main>

<script>
  const boxes = document.querySelectorAll('input[type="checkbox"]');
  const bar = document.getElementById('progressBar');
  const label = document.getElementById('progressLabel');
  const pct = document.getElementById('progressPct');
  function updateProgress(){{
    const total = boxes.length;
    const done = Array.from(boxes).filter(b=>b.checked).length;
    const p = total === 0 ? 0 : Math.round((done/total)*100);
    bar.style.width = p + '%';
    label.textContent = done + ' of ' + total + ' complete';
    pct.textContent = p + '%';
    try{{
      const state = {{}};
      boxes.forEach(b=>state[b.id]=b.checked);
      localStorage.setItem('oenMauiSmaChecklist', JSON.stringify(state));
    }}catch(e){{}}
  }}
  function checkAll(val){{
    boxes.forEach(b=>b.checked=val);
    updateProgress();
  }}
  boxes.forEach(b=>b.addEventListener('change',updateProgress));
  try{{
    const saved = JSON.parse(localStorage.getItem('oenMauiSmaChecklist')||'{{}}');
    boxes.forEach(b=>{{ if(saved[b.id]) b.checked = true; }});
  }}catch(e){{}}
  updateProgress();
</script>
</body>
</html>
""")
    return "".join(parts)


# ----------------------------------------------------------------------------
# PDF GENERATION (reportlab)
# ----------------------------------------------------------------------------

def build_pdf(out_path):
    doc = BaseDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=1.0 * inch,
        bottomMargin=0.75 * inch,
        title=f"{BRAND_NAME} — {DOC_TITLE}",
        author=BRAND_NAME,
        subject="Maui SMA Permit Submission Procedural Checklist",
    )

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="normal",
    )

    def _header_footer(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(COLOR_ACCENT)
        canvas.rect(0, letter[1] - 0.85 * inch, letter[0], 0.85 * inch, fill=1, stroke=0)
        # Brand small
        canvas.setFillColor(white)
        canvas.setFont(FONT_REG, 7)
        canvas.drawString(0.6 * inch, letter[1] - 0.32 * inch, BRAND_NAME.upper())
        # Doc title
        canvas.setFont(FONT_BOLD, 11)
        canvas.drawString(0.6 * inch, letter[1] - 0.5 * inch, DOC_TITLE)
        # Sub
        canvas.setFont(FONT_REG, 8)
        canvas.drawString(0.6 * inch, letter[1] - 0.64 * inch, DOC_SUBTITLE)
        # Rev right
        canvas.setFont(FONT_REG, 7.5)
        canvas.drawRightString(letter[0] - 0.6 * inch, letter[1] - 0.32 * inch, DOC_REV)
        canvas.drawRightString(letter[0] - 0.6 * inch, letter[1] - 0.46 * inch, DOC_SCOPE)
        canvas.drawRightString(letter[0] - 0.6 * inch, letter[1] - 0.60 * inch, DOC_SISTER)

        # Footer
        canvas.setStrokeColor(COLOR_LINE)
        canvas.setLineWidth(0.5)
        canvas.line(0.6 * inch, 0.55 * inch, letter[0] - 0.6 * inch, 0.55 * inch)
        canvas.setFillColor(COLOR_MUTED)
        canvas.setFont(FONT_REG, 7.5)
        canvas.drawString(0.6 * inch, 0.40 * inch,
                          f"{BRAND_NAME} · {PREPARED_BY}")
        canvas.drawRightString(letter[0] - 0.6 * inch, 0.40 * inch,
                               f"Page {doc.page}")
        canvas.drawString(0.6 * inch, 0.28 * inch,
                          "Sister document: Building Permit Submission Checklist. Not legal advice — verify current Maui Planning requirements before filing.")
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_header_footer),
    ])

    styles = getSampleStyleSheet()

    # Custom styles
    style_section = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=COLOR_ACCENT,
        spaceBefore=8,
        spaceAfter=2,
        leading=14,
    )
    style_section_sub = ParagraphStyle(
        "SectionSub",
        parent=styles["Normal"],
        fontName=FONT_IT,
        fontSize=8.5,
        textColor=COLOR_MUTED,
        spaceBefore=0,
        spaceAfter=6,
        leading=11,
    )
    style_item = ParagraphStyle(
        "Item",
        parent=styles["Normal"],
        fontName=FONT_REG,
        fontSize=9,
        textColor=COLOR_INK,
        leading=11.5,
        spaceBefore=1,
        spaceAfter=2,
    )
    style_note = ParagraphStyle(
        "Note",
        parent=styles["Normal"],
        fontName=FONT_IT,
        fontSize=7.8,
        textColor=COLOR_MUTED,
        leading=10,
        leftIndent=0,
        spaceBefore=1,
        spaceAfter=1,
    )
    style_xref = ParagraphStyle(
        "Xref",
        parent=styles["Normal"],
        fontName=FONT_BOLD,
        fontSize=7.3,
        textColor=COLOR_XREF,
        leading=9,
        leftIndent=0,
        spaceBefore=1,
        spaceAfter=3,
    )
    style_alert_title = ParagraphStyle(
        "AlertTitle",
        parent=styles["Heading3"],
        fontName=FONT_BOLD,
        fontSize=11,
        textColor=HexColor("#6b4a00"),
        spaceAfter=4,
    )
    style_alert_body = ParagraphStyle(
        "AlertBody",
        parent=styles["Normal"],
        fontName=FONT_REG,
        fontSize=8.5,
        textColor=COLOR_INK,
        leading=11,
        leftIndent=10,
        bulletIndent=0,
        spaceAfter=2,
    )
    style_label_small = ParagraphStyle(
        "LabelSmall",
        parent=styles["Normal"],
        fontName=FONT_REG,
        fontSize=6.5,
        textColor=COLOR_MUTED,
        leading=8,
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName=FONT_REG,
        fontSize=8.5,
        textColor=COLOR_INK,
        leading=11,
        spaceAfter=4,
    )
    style_sources = ParagraphStyle(
        "Sources",
        parent=styles["Normal"],
        fontName=FONT_REG,
        fontSize=7.5,
        textColor=COLOR_MUTED,
        leading=10,
    )
    style_disclaimer = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName=FONT_IT,
        fontSize=7,
        textColor=COLOR_MUTED,
        leading=9,
    )

    def flag_inline(flags):
        """Return reportlab-flavored inline flag HTML for Paragraph."""
        pieces = []
        colors = {"REQ": "#b5121b", "COND": "#b36b00", "NEW": "#116530"}
        for f in flags:
            c = colors[f]
            pieces.append(
                f'<font backColor="{c}" color="white"><b>&nbsp;{f}&nbsp;</b></font>'
            )
        return "".join(pieces) + "&nbsp;"

    story = []

    # ---- Project info bar ----
    proj_data = [
        [Paragraph("<b>PROJECT NAME</b>", style_label_small), "", Paragraph("<b>ADDRESS</b>", style_label_small), "", Paragraph("<b>TMK</b>", style_label_small), ""],
        [Paragraph("<b>SMA ASSESSMENT NO.</b>", style_label_small), "", Paragraph("<b>ARCHITECT OF RECORD</b>", style_label_small), "", Paragraph("<b>SUBMISSION DATE</b>", style_label_small), ""],
        [Paragraph("<b>PREPARED BY</b>", style_label_small), "", Paragraph("<b>REVIEWER / CHECKER</b>", style_label_small), "", Paragraph("<b>FILING TYPE</b>", style_label_small), ""],
    ]
    proj_tbl = Table(proj_data, colWidths=[0.95*inch, 1.45*inch, 0.95*inch, 1.45*inch, 0.95*inch, 1.45*inch])
    proj_tbl.setStyle(TableStyle([
        ("LINEBELOW", (1,0), (1,-1), 0.5, COLOR_LINE),
        ("LINEBELOW", (3,0), (3,-1), 0.5, COLOR_LINE),
        ("LINEBELOW", (5,0), (5,-1), 0.5, COLOR_LINE),
        ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
    ]))
    story.append(proj_tbl)
    story.append(Spacer(1, 8))

    # ---- Legend row ----
    legend_data = [[
        Paragraph('<font backColor="#b5121b" color="white"><b>&nbsp;REQ&nbsp;</b></font> Required', style_body),
        Paragraph('<font backColor="#b36b00" color="white"><b>&nbsp;COND&nbsp;</b></font> Conditional', style_body),
        Paragraph('<font backColor="#116530" color="white"><b>&nbsp;NEW&nbsp;</b></font> Recent rule change', style_body),
        Paragraph('<font color="#4a1f6e"><b>↔ BPC</b></font> Cross-ref → Building Permit Checklist', style_body),
    ]]
    legend_tbl = Table(legend_data, colWidths=[1.55*inch, 1.55*inch, 1.85*inch, 2.3*inch])
    legend_tbl.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, COLOR_LINE),
        ("BACKGROUND", (0,0), (-1,-1), COLOR_CARD),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(legend_tbl)
    story.append(Spacer(1, 10))

    # ---- Recent changes alert ----
    alert_flow = [Paragraph("⚠ Recent Rule Changes to Know Before Filing", style_alert_title)]
    for title, body in RECENT_CHANGES:
        alert_flow.append(Paragraph(f"• <b>{title}.</b> {body}", style_alert_body))
    alert_tbl = Table([[alert_flow]], colWidths=[7.3*inch])
    alert_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), COLOR_HIGHLIGHT),
        ("LINEBEFORE", (0,0), (0,0), 3, COLOR_HIGHLIGHT_BORDER),
        ("BOX", (0,0), (-1,-1), 0.5, COLOR_HIGHLIGHT_BORDER),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(alert_tbl)
    story.append(Spacer(1, 12))

    # ---- Phase sections ----
    for sec in SECTIONS:
        section_title = Paragraph(
            f'Phase {sec["num"]} — {sec["title"]}',
            style_section,
        )
        section_sub = Paragraph(sec["subtitle"], style_section_sub)
        section_rule = HRFlowable(width="100%", thickness=0.7, color=COLOR_LINE, spaceBefore=1, spaceAfter=5)

        rows = []
        for iid, flags, text, note, xref in sec["items"]:
            # Checkbox cell
            cb = Paragraph('<font size="11">☐</font>', style_item)
            # Text cell
            lines = [Paragraph(f'{flag_inline(flags)}{text}', style_item)]
            if note:
                lines.append(Paragraph(note, style_note))
            if xref:
                lines.append(Paragraph(xref, style_xref))
            rows.append([cb, lines])

        tbl = Table(rows, colWidths=[0.22*inch, 7.08*inch])
        tstyle = TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ])
        for i in range(len(rows) - 1):
            tstyle.add("LINEBELOW", (0,i), (-1,i), 0.25, HexColor("#e8e3d4"))
        tbl.setStyle(tstyle)

        group = KeepTogether([section_title, section_sub, section_rule, tbl, Spacer(1, 6)])
        story.append(group)

    # ---- Cross-reference matrix ----
    xref_title = Paragraph(
        "Cross-Reference Matrix — SMA ↔ Building Permit Submission Checklist",
        style_section,
    )
    xref_sub = Paragraph(
        "Read across: each SMA checklist phase ties to one or more sections of the Building Permit Submission Checklist so the two documents move in lockstep.",
        style_section_sub,
    )
    xref_rule = HRFlowable(width="100%", thickness=0.7, color=COLOR_LINE, spaceBefore=1, spaceAfter=5)

    xref_rows = [[
        Paragraph("<b>SMA Permit Checklist Item</b>", style_body),
        Paragraph("<b>Building Permit Submission Checklist Reference</b>", style_body),
    ]]
    for left, right in XREF_MATRIX:
        xref_rows.append([
            Paragraph(left, style_body),
            Paragraph(right, style_body),
        ])
    xref_tbl = Table(xref_rows, colWidths=[3.8*inch, 3.5*inch], repeatRows=1)
    xref_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HexColor("#eef4f7")),
        ("TEXTCOLOR", (0,0), (-1,0), COLOR_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.4, COLOR_LINE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))

    story.append(KeepTogether([xref_title, xref_sub, xref_rule]))
    story.append(xref_tbl)
    story.append(Spacer(1, 12))

    # ---- Sources ----
    story.append(Paragraph("<b>Sources &amp; References</b>", style_section))
    story.append(HRFlowable(width="100%", thickness=0.7, color=COLOR_LINE, spaceBefore=1, spaceAfter=5))
    story.append(Paragraph(SOURCES, style_sources))
    story.append(Spacer(1, 10))

    # ---- Disclaimer / signoff ----
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_LINE, spaceBefore=4, spaceAfter=4))
    story.append(Paragraph(
        f"Prepared by {BRAND_NAME} · {PREPARED_BY} · {DOC_REV}",
        style_disclaimer,
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph(DISCLAIMER, style_disclaimer))

    doc.build(story)


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    outputs_dir = "/sessions/nice-great-dijkstra/mnt/outputs"
    admin_dir = "/sessions/nice-great-dijkstra/mnt/Admin/Permit Forms and Checklist"

    html_path_local = os.path.join(outputs_dir, "Maui_SMA_Permit_Checklist.html")
    pdf_path_local  = os.path.join(outputs_dir, "Maui_SMA_Permit_Checklist.pdf")

    html_path_admin = os.path.join(admin_dir, "Oʻen Maui — Maui SMA Permit Checklist.html")
    pdf_path_admin  = os.path.join(admin_dir, "Oʻen Maui — Maui SMA Permit Checklist.pdf")

    html = build_html()
    with open(html_path_local, "w", encoding="utf-8") as f:
        f.write(html)
    with open(html_path_admin, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML written: {html_path_local}")
    print(f"HTML written: {html_path_admin}")

    build_pdf(pdf_path_local)
    print(f"PDF written: {pdf_path_local}")

    import shutil
    shutil.copy(pdf_path_local, pdf_path_admin)
    print(f"PDF written: {pdf_path_admin}")

    # Count items
    total = sum(len(s["items"]) for s in SECTIONS)
    print(f"Total checklist items: {total}")
