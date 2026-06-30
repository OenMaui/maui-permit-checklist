#!/usr/bin/env python3
"""
build_bpc_pdf.py
────────────────
Single-source PDF generator for the Oʻen Maui Building Permit Submission
Checklist. The authoritative source is the HTML file (kept in the Admin
folder); this script parses it with BeautifulSoup and renders a
brand-consistent, print-ready PDF via ReportLab.

Run from anywhere. Paths are resolved relative to two fixed locations:
    HTML (source of truth) →
        /Users/erik/Documents/Ø'en MAUI Architecture + Design/Admin/
        Permit Forms and Checklist/
        Oʻen Maui — Building Permit Submission Checklist.html
    PDF (output) →
        same folder, matching filename with .pdf extension

Why single-source? v1.3 renumbering caught us once; going forward the HTML
is edited, this script re-runs, and the PDF stays in lock-step.
"""

from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ────────────────────────────────────────────────────────────────────────────
# Font setup — DejaVu Sans so ʻokina (U+02BB) and other Unicode chars render.
# ────────────────────────────────────────────────────────────────────────────
_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
try:
    pdfmetrics.registerFont(TTFont("Body", f"{_FONT_DIR}/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("Body-Bold", f"{_FONT_DIR}/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Body-Oblique", f"{_FONT_DIR}/DejaVuSans-Oblique.ttf"))
    pdfmetrics.registerFont(
        TTFont("Body-BoldOblique", f"{_FONT_DIR}/DejaVuSans-BoldOblique.ttf")
    )
    registerFontFamily(
        "Body",
        normal="Body",
        bold="Body-Bold",
        italic="Body-Oblique",
        boldItalic="Body-BoldOblique",
    )
    FONT_REG = "Body"
    FONT_BOLD = "Body-Bold"
    FONT_IT = "Body-Oblique"
    FONT_BI = "Body-BoldOblique"
except Exception:
    # Fallback if DejaVu not available — characters outside Helvetica will
    # render as boxes, but layout will still be correct.
    FONT_REG = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    FONT_IT = "Helvetica-Oblique"
    FONT_BI = "Helvetica-BoldOblique"


# ────────────────────────────────────────────────────────────────────────────
# Brand palette — mirrors build_sma_checklist.py so the two PDFs read as a
# matched set when printed side-by-side.
# ────────────────────────────────────────────────────────────────────────────
BRAND = {
    "ink":    colors.HexColor("#1f2937"),   # slate-800
    "muted":  colors.HexColor("#6b7280"),   # slate-500
    "rule":   colors.HexColor("#e5e7eb"),
    "band":   colors.HexColor("#0f3a52"),   # Oʻen Maui ocean navy
    "band_t": colors.HexColor("#ffffff"),
    "accent": colors.HexColor("#0d9488"),   # teal
    "sand":   colors.HexColor("#faf6ef"),
    # Tag colors — mirror the HTML palette exactly
    "tag_req_bg":   colors.HexColor("#dbeafe"), "tag_req_fg":   colors.HexColor("#1d4ed8"),
    "tag_flag_bg":  colors.HexColor("#fee2e2"), "tag_flag_fg":  colors.HexColor("#b91c1c"),
    "tag_cond_bg":  colors.HexColor("#fef3c7"), "tag_cond_fg":  colors.HexColor("#92400e"),
    "tag_shpd_bg":  colors.HexColor("#ede9fe"), "tag_shpd_fg":  colors.HexColor("#5b21b6"),
    "tag_sma_bg":   colors.HexColor("#d1fae5"), "tag_sma_fg":   colors.HexColor("#065f46"),
    "tag_xref_bg":  colors.HexColor("#ecfdf5"), "tag_xref_fg":  colors.HexColor("#065f46"),
    "tag_upd_bg":   colors.HexColor("#fef3c7"), "tag_upd_fg":   colors.HexColor("#92400e"),
    # Section accents (left border strip)
    "s_admin":  colors.HexColor("#0f3a52"),
    "s_mapps":  colors.HexColor("#0d9488"),
    "s_gen":    colors.HexColor("#1f6f8b"),
    "s_site":   colors.HexColor("#047857"),
    "s_arch":   colors.HexColor("#7c3aed"),
    "s_struct": colors.HexColor("#6b21a8"),
    "s_sep":    colors.HexColor("#be123c"),
    "s_energy": colors.HexColor("#ca8a04"),
    "s_mep":    colors.HexColor("#2563eb"),
    "s_civil":  colors.HexColor("#92400e"),
    "s_agency": colors.HexColor("#0f766e"),
    "s_flag":   colors.HexColor("#b91c1c"),
    "s_notes":  colors.HexColor("#334155"),
}


# ────────────────────────────────────────────────────────────────────────────
# Styles
# ────────────────────────────────────────────────────────────────────────────
def _style(name, **kw):
    base = dict(
        name=name,
        fontName=FONT_REG,
        fontSize=9.5,
        leading=12.5,
        textColor=BRAND["ink"],
    )
    base.update(kw)
    return ParagraphStyle(**base)


STY_TITLE    = _style("Title",    fontName=FONT_BOLD, fontSize=18, leading=22, textColor=BRAND["band_t"])
STY_SUBTITLE = _style("Subtitle", fontName=FONT_REG,  fontSize=10, leading=13, textColor=BRAND["band_t"])
STY_META     = _style("Meta",     fontName=FONT_IT,   fontSize=8.5, leading=11, textColor=BRAND["muted"])
STY_H2       = _style("H2",       fontName=FONT_BOLD, fontSize=12.5, leading=15, textColor=colors.white, spaceAfter=2)
STY_SUBH     = _style("SubH",     fontName=FONT_BOLD, fontSize=8.5,  leading=11,
                       textColor=BRAND["muted"], spaceBefore=4, spaceAfter=1)
STY_BODY     = _style("Body",     fontSize=9.3, leading=12.2)
STY_BODY_TIGHT = _style("BodyTight", fontSize=9.3, leading=12, spaceAfter=0)
STY_NOTE     = _style("Note",     fontName=FONT_IT, fontSize=8.3, leading=10.8,
                       textColor=BRAND["muted"], leftIndent=14, spaceAfter=2)
STY_FLAG_NOTE = _style("FlagNote", fontName=FONT_BI, fontSize=8.3, leading=10.8,
                       textColor=colors.HexColor("#b91c1c"), leftIndent=14, spaceAfter=2)
STY_CHANGE   = _style("Change",   fontSize=8.7, leading=11.5, leftIndent=10, spaceAfter=3)
STY_SRC      = _style("Sources",  fontSize=7.8, leading=10, textColor=BRAND["muted"])
STY_FOOT     = _style("Foot",     fontName=FONT_IT, fontSize=7.5, leading=9.5, textColor=BRAND["muted"])


# ────────────────────────────────────────────────────────────────────────────
# Tag rendering — produces a little coloured inline "pill" via Paragraph
# <font> markup, matching the HTML badges.
# ────────────────────────────────────────────────────────────────────────────
TAG_COLORS = {
    "req":     ("tag_req_bg",   "tag_req_fg",   "REQ"),
    "cond":    ("tag_cond_bg",  "tag_cond_fg",  "COND"),
    "flag":    ("tag_flag_bg",  "tag_flag_fg",  "FLAGGED"),
    "shpd":    ("tag_shpd_bg",  "tag_shpd_fg",  "SHPD"),
    "sma":     ("tag_sma_bg",   "tag_sma_fg",   "SMA"),
    "xref":    ("tag_xref_bg",  "tag_xref_fg",  None),  # label taken from text
    "updated": ("tag_upd_bg",   "tag_upd_fg",   "UPDATED"),
}


def _tag_inline(cls: str, text: str) -> str:
    bg_key, fg_key, default_label = TAG_COLORS.get(cls, ("tag_req_bg", "tag_req_fg", cls.upper()))
    fg = BRAND[fg_key].hexval()[2:]  # strip '0x'
    label = text.strip() if default_label is None else default_label
    label = _html_esc(label)
    # Use a small bold label, tinted; the background "pill" effect is fudged with
    # a thin underline of the same color. Good enough; the badge colour is what
    # the eye reads on a checklist.
    return f'<b><font color="#{fg}" size="7.6">[{label}]</font></b> '


def _html_esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


# ────────────────────────────────────────────────────────────────────────────
# Convert an HTML .main-text / .note node into a Paragraph-safe markup string.
# We preserve <strong>/<em>, convert <span class="tag x">…</span> into inline
# bracket labels, and escape everything else.
# ────────────────────────────────────────────────────────────────────────────
def _render_inline(node: Tag) -> str:
    if isinstance(node, NavigableString):
        return _html_esc(str(node))
    out = []
    for child in node.children:
        if isinstance(child, NavigableString):
            out.append(_html_esc(str(child)))
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        cls = " ".join(child.get("class", []))
        if name == "span" and "tag" in cls:
            tag_cls = next((c for c in child.get("class", []) if c != "tag"), "")
            out.append(_tag_inline(tag_cls, child.get_text(" ", strip=True)))
        elif name in ("strong", "b"):
            out.append(f"<b>{_render_inline(child)}</b>")
        elif name in ("em", "i"):
            out.append(f"<i>{_render_inline(child)}</i>")
        elif name == "code":
            out.append(f'<font face="{FONT_REG}">{_render_inline(child)}</font>')
        elif name == "br":
            out.append("<br/>")
        else:
            out.append(_render_inline(child))
    text = "".join(out)
    # Collapse runs of whitespace
    return re.sub(r"\s+", " ", text).strip()


# ────────────────────────────────────────────────────────────────────────────
# Section icon/color mapping based on HTML class
# ────────────────────────────────────────────────────────────────────────────
SECTION_CLASS_MAP = {
    "s-admin":  ("s_admin",  "📋"),
    "s-site":   ("s_site",   "🗺"),
    "s-arch":   ("s_arch",   "📐"),
    "s-struct": ("s_struct", "🏗"),
    "s-sep":    ("s_sep",    "🧱"),
    "s-energy": ("s_energy", "⚡"),
    "s-mep":    ("s_mep",    "🔧"),
    "s-civil":  ("s_civil",  "🌊"),
    "s-agency": ("s_agency", "🏢"),
    "s-flag":   ("s_flag",   "⚠"),
}


def _section_color(section_classes: list[str]) -> colors.Color:
    for cls in section_classes:
        if cls in SECTION_CLASS_MAP:
            return BRAND[SECTION_CLASS_MAP[cls][0]]
    # Heuristic fallback by number in title
    return BRAND["accent"]


# ────────────────────────────────────────────────────────────────────────────
# Parse the HTML and return a dict with everything we need to render.
# ────────────────────────────────────────────────────────────────────────────
def parse_bpc_html(html_path: Path) -> dict:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    # "firm" block — use the text after the <span>Architecture + Design</span>
    firm_el = soup.select_one(".firm")
    firm_brand = "Oʻen Maui Architecture + Design"
    if firm_el is not None:
        brand_main = firm_el.find(text=True, recursive=False)
        sub = firm_el.select_one("span")
        main_txt = (brand_main or "").strip() or "Oʻen Maui"
        sub_txt = (sub.get_text(" ", strip=True) if sub else "Architecture + Design")
        firm_brand = f"{main_txt} {sub_txt}".strip()

    title = _text(soup.select_one(".doc-title")) or "Building Permit Submission Checklist"

    # Pull everything inside .doc-meta *except* the .doc-title sub-element,
    # and use the last line (the revision) as our header meta — the body of
    # the page already carries the change log so we don't need to repeat
    # everything here.
    meta_el = soup.select_one(".doc-meta")
    meta = ""
    if meta_el is not None:
        parts = []
        for child in meta_el.children:
            if isinstance(child, Tag) and "doc-title" in child.get("class", []):
                continue
            if isinstance(child, NavigableString):
                s = str(child).strip()
                if s:
                    parts.append(s)
            elif isinstance(child, Tag):
                if child.name == "br":
                    continue
                s = child.get_text(" ", strip=True)
                if s:
                    parts.append(s)
        # Last part is the revision line (e.g. "Rev. April 2026 — v1.4")
        rev = next((p for p in reversed(parts) if "Rev." in p or "v1" in p), "")
        meta = rev

    # Change log entries
    changes = []
    for li in soup.select(".change-banner li"):
        changes.append(_render_inline(li))

    # Sections
    sections = []
    for sec in soup.select(".section"):
        sec_classes = sec.get("class", [])
        title_el = sec.select_one(".sec-title")
        sec_title = _text(title_el) if title_el else ""
        sub = _text(sec.select_one(".sec-count")) or ""
        items = []
        for node in sec.select_one(".items").children if sec.select_one(".items") else []:
            if not isinstance(node, Tag):
                continue
            cls = " ".join(node.get("class", []))
            if "sub-head" in cls:
                items.append(("subhead", _text(node)))
            elif "item" in cls:
                body = node.select_one(".body")
                if body is None:
                    continue
                main_el = body.select_one(".main-text")
                main = _render_inline(main_el) if main_el else ""
                notes = [_render_inline(n) for n in body.select(".note")]
                flag_notes = [_render_inline(n) for n in body.select(".flag-note")]
                items.append(("item", main, notes, flag_notes))
            elif "flag-note" in cls:
                items.append(("flag", _render_inline(node)))
        sections.append(
            dict(
                classes=sec_classes,
                title=sec_title,
                subtitle=sub,
                items=items,
            )
        )

    return dict(firm=firm_brand, title=title, meta=meta, changes=changes, sections=sections)


def _text(el) -> str:
    return el.get_text(" ", strip=True) if el is not None else ""


# ────────────────────────────────────────────────────────────────────────────
# Page template — header band with firm + title, footer with page numbers.
# ────────────────────────────────────────────────────────────────────────────
def _draw_page_chrome(canv, doc, firm: str, title: str, meta: str):
    canv.saveState()
    w, h = LETTER
    # Top band
    band_h = 0.72 * inch
    canv.setFillColor(BRAND["band"])
    canv.rect(0, h - band_h, w, band_h, fill=1, stroke=0)
    canv.setFillColor(BRAND["band_t"])
    canv.setFont(FONT_BOLD, 13)
    canv.drawString(0.6 * inch, h - 0.32 * inch, firm)
    canv.setFont(FONT_REG, 10)
    canv.drawString(0.6 * inch, h - 0.52 * inch, title)
    canv.setFont(FONT_IT, 8.5)
    canv.drawRightString(w - 0.6 * inch, h - 0.52 * inch, meta)

    # Footer
    canv.setStrokeColor(BRAND["rule"])
    canv.setLineWidth(0.6)
    canv.line(0.6 * inch, 0.6 * inch, w - 0.6 * inch, 0.6 * inch)
    canv.setFillColor(BRAND["muted"])
    canv.setFont(FONT_IT, 7.8)
    canv.drawString(0.6 * inch, 0.42 * inch,
                    "Oʻen Maui Architecture + Design · Building Permit Submission Checklist")
    canv.drawRightString(w - 0.6 * inch, 0.42 * inch,
                         f"Page {canv.getPageNumber()}")
    canv.restoreState()


# ────────────────────────────────────────────────────────────────────────────
# Build the flowable story
# ────────────────────────────────────────────────────────────────────────────
def _section_header_flowable(title: str, subtitle: str, color: colors.Color) -> Table:
    t = Table(
        [[Paragraph(f'<font color="white"><b>{_html_esc(title)}</b></font>', STY_H2),
          Paragraph(f'<font color="#e5e7eb"><i>{_html_esc(subtitle)}</i></font>',
                    _style("HSub", fontSize=8.5, leading=11, textColor=colors.white))]],
        colWidths=[4.8 * inch, 2.5 * inch],
    )
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )
    return t


def _item_flowable(main: str, notes: list[str], flag_notes: list[str]) -> KeepTogether:
    # Checkbox + text in a 2-col table
    row = [
        Paragraph("☐", _style("CB", fontSize=11.5, leading=13)),
        Paragraph(main, STY_BODY),
    ]
    t = Table([row], colWidths=[0.26 * inch, 6.9 * inch])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    flow = [t]
    for n in notes:
        flow.append(Paragraph(n, STY_NOTE))
    for n in flag_notes:
        flow.append(Paragraph("⚠ " + n, STY_FLAG_NOTE))
    flow.append(Spacer(1, 2))
    return KeepTogether(flow)


def build_story(data: dict):
    story = []

    # Intro: blurb + change log
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "This checklist is the working pre-submittal QC document for building "
            "permit packages filed with the County of Maui Department of Public "
            "Works, Development Services Administration (DSA), via the MAPPS "
            "portal. Use it alongside the Oʻen Maui — Maui SMA Permit Checklist "
            "for any project inside the Special Management Area.",
            STY_BODY,
        )
    )
    story.append(Spacer(1, 8))
    story.append(Paragraph("Change Log", _style("H3", fontName=FONT_BOLD, fontSize=10.5, textColor=BRAND["band"])))
    story.append(HRFlowable(width="100%", thickness=0.6, color=BRAND["rule"], spaceAfter=4))
    for c in data["changes"]:
        story.append(Paragraph("• " + c, STY_CHANGE))
    story.append(Spacer(1, 8))

    # Sections
    for sec in data["sections"]:
        color = _section_color(sec["classes"])
        story.append(Spacer(1, 6))
        story.append(
            _section_header_flowable(sec["title"], sec["subtitle"], color)
        )
        story.append(Spacer(1, 4))
        for node in sec["items"]:
            if node[0] == "subhead":
                story.append(Paragraph(node[1].upper(), STY_SUBH))
            elif node[0] == "item":
                _, main, notes, flag_notes = node
                if not main:
                    continue
                story.append(_item_flowable(main, notes, flag_notes))
            elif node[0] == "flag":
                story.append(Paragraph("⚠ " + node[1], STY_FLAG_NOTE))

    # Sources / disclaimer
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.8, color=BRAND["band"], spaceAfter=6))
    story.append(
        Paragraph(
            "<b>Companion documents.</b> This checklist is designed to work in "
            "tandem with the <i>Oʻen Maui — Maui SMA Permit Checklist</i>. "
            "Cross-references marked <b>[↔ SMA Phase X]</b> inside an item point "
            "to the corresponding task in the SMA checklist so that Phase 1–7 "
            "SMA work is tracked in the sister document rather than duplicated here.",
            STY_BODY_TIGHT,
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "<i>This document is a working procedural tool, not legal advice. "
            "Confirm current Maui County DSA and Planning Department requirements "
            "before each filing. Prepared by Oʻen Maui Architecture + "
            "Design.</i>",
            STY_FOOT,
        )
    )
    return story


# ────────────────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────────────────
def build_pdf(html_path: Path, pdf_path: Path):
    data = parse_bpc_html(html_path)

    def on_page(canv, doc):
        _draw_page_chrome(canv, doc, data["firm"], data["title"], data["meta"])

    frame = Frame(
        0.6 * inch,
        0.75 * inch,
        LETTER[0] - 1.2 * inch,
        LETTER[1] - 1.55 * inch,
        id="main",
        showBoundary=0,
    )
    doc = BaseDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        title="Oʻen Maui — Building Permit Submission Checklist",
        author="Oʻen Maui Architecture + Design",
        subject="Maui County building permit pre-submittal QC",
        keywords="Maui building permit MAPPS DSA checklist",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    story = build_story(data)
    doc.build(story)


def _find_admin_dir() -> Path:
    """Locate the 'Permit Forms and Checklist' folder relative to this script,
    so the generator works on any machine without hardcoded session paths."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if parent.name == "Permit Forms and Checklist":
            return parent
    # Fallback: the folder two levels above this script (<root>/_generators/<script>)
    return here.parents[1]


def main():
    # Explicit override:  build_bpc_pdf.py [HTML_PATH] [PDF_PATH]
    if len(sys.argv) == 3:
        src, out = Path(sys.argv[1]), Path(sys.argv[2])
        print(f"Reading {src}")
        print(f"Writing {out}")
        build_pdf(src, out)
        print("Done.")
        return

    # No args: refresh BOTH the standalone admin PDF and the website download PDF.
    admin_dir = _find_admin_dir()
    site_root = admin_dir / "_site_staging"
    jobs = [
        (admin_dir / "Oʻen Maui — Building Permit Submission Checklist.html",
         admin_dir / "Oʻen Maui — Building Permit Submission Checklist.pdf",
         "admin standalone"),
        (site_root / "checklists" / "building-permit.html",
         site_root / "downloads" / "Oen-Maui-Building-Permit-Submission-Checklist.pdf",
         "website download"),
    ]
    built = 0
    for src, out, label in jobs:
        if not src.exists():
            print(f"(skipped {label} — source not found: {src})")
            continue
        print(f"Reading {src}")
        print(f"Writing {out}  [{label}]")
        build_pdf(src, out)
        built += 1
    if built == 0:
        sys.exit("No BPC source HTML found near this script.")
    print("Done.")


if __name__ == "__main__":
    main()
