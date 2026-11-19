#!/usr/bin/env python3
"""Build the student's memo TEMPLATE and the DRAFT EXHIBITS as Word files.

  python build_docs.py --ledger L.json --exhibits exhibits.json --out /mnt/user-data/outputs

The memo template contains structure, prompts and guidance only: never analysis.
The exhibits file renders what Claude drafted from the student's own interview evidence
(exhibits.json, see references/exhibits.md), with every Impact Summary left blank.
"""
import argparse, json, os, datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1B, 0x2A, 0x4A); GREY = RGBColor(0x7F, 0x7F, 0x7F); GOLD = RGBColor(0x9A, 0x7B, 0x12)


def base_doc():
    d = Document()
    for s in d.sections:
        s.page_width, s.page_height = Inches(8.5), Inches(11)
        s.left_margin = s.right_margin = Inches(1); s.top_margin = s.bottom_margin = Inches(1)
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 12)):
        h = d.styles[name]; h.font.name = "Calibri"; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = NAVY
    return d


def para(d, text="", bold=False, italic=False, color=None, size=None, style=None, after=6):
    p = d.add_paragraph(style=style) if style else d.add_paragraph()
    if text:
        r = p.add_run(text); r.bold = bold; r.italic = italic
        if color is not None: r.font.color.rgb = color
        if size: r.font.size = Pt(size)
    p.paragraph_format.space_after = Pt(after)
    return p


def prompt(d, text, style=None):
    """Grey [bracketed] placeholder the student replaces."""
    return para(d, f"[{text}]", color=GREY, style=style)


def guide(d, text):
    return para(d, f"Guide: {text}", italic=True, color=GREY, size=10)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hex_fill); tcPr.append(sh)


def table(d, columns, rows):
    t = d.add_table(rows=1, cols=len(columns)); t.style = "Table Grid"
    for i, c in enumerate(columns):
        cell = t.rows[0].cells[i]; cell.text = ""; r = cell.paragraphs[0].add_run(str(c)); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); shade(cell, "1B2A4A")
    for row in rows:
        cells = t.add_row().cells
        for i in range(len(columns)):
            v = row[i] if i < len(row) else ""
            cells[i].text = ""
            txt = str(v)
            r = cells[i].paragraphs[0].add_run(txt)
            if "[gap" in txt.lower():
                r.font.color.rgb = RGBColor(0xA8, 0x32, 0x3E); r.italic = True
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def boxed(d, lines, title):
    t = d.add_table(rows=1, cols=1); t.style = "Table Grid"; c = t.rows[0].cells[0]; shade(c, "FFF9E6")
    c.text = ""; r = c.paragraphs[0].add_run(title); r.bold = True
    for ln in lines:
        p = c.add_paragraph(ln, style="List Bullet")
    d.add_paragraph()


def impact(d, title):
    para(d, f"Impact Summary: {title}", bold=True, after=2)
    prompt(d, "In your own words: what this exhibit shows, and how it affects the decision. Do not restate the exhibit.")


# ---------------------------------------------------------------- memo template
def memo_template(L, out):
    c = L["case"]; a = c["assignment"]; m = c.get("memo", {}); qs = a["questions"]
    d = base_doc()
    boxed(d, [
        "Replace every grey [bracketed] prompt with your own text, then change the text color to black.",
        "Delete every grey \"Guide:\" line. They explain what each section needs and are not part of the memo.",
        "Keep the sections in this order. No cover page, and never write in the first person.",
        f"Length: {a.get('deliverable', 'see the assignment')}",
        "Cite exhibits by letter (for example, \"see Exhibit E\"). The draft exhibits Interview-IQ built from your interviews are in a separate file: check every figure, rewrite them as yours, and write every Impact Summary yourself.",
        "Follow the course AI policy. Interview-IQ gives you structure and evidence; the analysis, recommendations and wording must be yours.",
    ], "How to use this template (delete this box before you submit)")
    para(d, c["title"], bold=True, size=18, color=NAVY, after=0)
    para(d, "Case Analysis Memo", size=12, color=NAVY, after=10)
    for k, v in (("TO:", m.get("to", "[Recipient name and title]")), ("FROM:", "[Your name and title]"), ("DATE:", "[Date of submission]"),
                 ("SUBJECT:", m.get("subject", "[Clear, specific topic of the decision]")), ("CC:", m.get("cc", "[Other recipients, if applicable]"))):
        p = para(d, after=2); r = p.add_run(k + "\t"); r.bold = True
        r2 = p.add_run(v); r2.font.color.rgb = GREY if v.startswith("[") else NAVY

    d.add_heading("Key Issues", 1)
    prompt(d, "Paragraph 1: the central problem that requires a decision, and the questions management needs answered.")
    prompt(d, "Paragraph 2: the required goals the recommended solution must achieve.")
    guide(d, "One to two paragraphs. Do not mention your recommendations here, and do not repeat case facts management already knows.")

    d.add_heading("Recommendations", 1)
    recs = ["Your decision: approve the full plan, approve a modified plan (say exactly what it is), or reject entry.",
            "The two or three things that must go right for your recommendation to succeed.",
            "The risks that could undermine it, and how the board should monitor them."]
    for r in recs:
        prompt(d, r, style="List Number")
    guide(d, "Numbered and specific. Do not explain your rationale here; it belongs in the Analysis.")

    d.add_heading("Decision Criteria", 1)
    prompt(d, "Short paragraph: the criteria the board will use to judge the alternatives, how each ties to a required goal, and how they are weighted. Refer to Exhibit L.")
    guide(d, "Criteria are indicators that a goal has been achieved. Include only criteria that serve this decision.")

    d.add_heading("Analysis", 1)
    prompt(d, "One or two sentences that explain the two parts: Section 1 answers the key questions from the evidence in the exhibits; Section 2 tests the recommendation against its alternatives.")
    d.add_heading("Section 1: Key Questions", 2)
    exhibit_hint = {"Q1": "Exhibit E (Five Forces)", "Q2": "Exhibits I (VRIN) and K (SWOT)", "Q3": "Exhibit J-1 (Unit Economics and Financial Ratios)",
                    "Q4": "Exhibits P-1 (Scenario Inputs) and P-2 (Competitor Responses)", "Q5": "Exhibits L, M and N"}
    for q in qs[:-1] if len(qs) > 1 else qs:
        para(d, f"Question {q['id'][1:]}: {q['title']}" + (f" (about {q['words']} words)" if q.get("words") else ""), bold=True, after=2)
        guide(d, q["prompt"])
        prompt(d, "Answer first, in one sentence.")
        prompt(d, "Supporting evidence: about three reasons, each citing the executive who said it and the exhibit that shows it" + (f" ({exhibit_hint[q['id']]})" if q["id"] in exhibit_hint else "") + ".")
        prompt(d, "Where the executives disagree, which source is more credible and why.")
    last = qs[-1]
    d.add_heading("Section 2: Recommendations", 2)
    para(d, f"Recommendation: {last['title']}" + (f" (about {last['words']} words)" if last.get("words") else ""), bold=True, after=2)
    guide(d, last["prompt"])
    prompt(d, "The issue and the alternatives: one short paragraph that defines the decision and the alternatives you evaluate.")
    for alt in m.get("alternatives", ["Alternative 1", "Alternative 2", "Alternative 3"]):
        p = d.add_paragraph(style="List Bullet"); r = p.add_run(alt + ". "); r.bold = True
        r2 = p.add_run("[Pro: … Con: … Cite the interviews and exhibits.]"); r2.font.color.rgb = GREY
    prompt(d, "Which alternative scores highest in the Decision Matrix (Exhibit M), and why it is superior to the others.")
    prompt(d, "What must go right (two or three conditions), and the early-warning signs the board should monitor.")
    guide(d, "Report the facts; do not predict the outcome. Cover every viable alternative, including doing nothing where relevant.")

    d.add_heading("Conclusion", 1)
    prompt(d, "One to two paragraphs: your key recommendations, and how the decision criteria support them.")
    guide(d, "Never state a belief or feeling, and never predict results that depend on factors outside management's control.")

    d.add_heading("Exhibits", 1)
    guide(d, "Exhibits A, B, L and M are yours to build. The others are drafted in your Interview-IQ Exhibits file from your own interviews: verify, edit and paste them here, and write each Impact Summary yourself.")
    d.add_heading("Exhibit A. Guiding Questions", 2)
    for i in range(1, 4):
        prompt(d, f"Q{i}: Question"); prompt(d, "Response: clear analysis and answer")
    guide(d, "Examples: What is the core problem? Who are the key stakeholders? What are the time constraints? What resources are available? What are the key success metrics?")
    impact(d, "Guiding Questions")
    d.add_heading("Exhibit B. Key Issues", 2)
    prompt(d, "Central problem"); para(d, "Management questions", bold=True, after=2)
    for q in qs:
        prompt(d, f"{q['id']} {q['title']}: restate the question in your own words", style="List Bullet")
    para(d, "Required goals", bold=True, after=2)
    for i in range(3):
        prompt(d, "Goal", style="List Bullet")
    impact(d, "Key Issues")
    d.add_heading("Exhibit L. Decision Criteria and Weights", 2)
    table(d, ["Criterion", "Required goal it measures", "Weight (1–5)", "Why this weight"], [["[ ]", "[ ]", "[ ]", "[ ]"]] * 4)
    impact(d, "Decision Criteria")
    d.add_heading("Exhibit M. Decision Matrix", 2)
    alts = m.get("alternatives", ["Alternative 1", "Alternative 2", "Alternative 3"])
    table(d, ["Criterion (weight)"] + [f"Alt {i + 1}" for i in range(len(alts))], [["[criterion (w)]"] + ["[1–10]"] * len(alts)] * 4 + [["Weighted total"] + ["[ ]"] * len(alts)])
    para(d, "Alternatives: " + "; ".join(f"Alt {i + 1} = {x}" for i, x in enumerate(alts)), size=9, color=GREY)
    impact(d, "Decision Matrix")
    para(d, "Exhibits C, E, I, J-1, K, N, P-1 and P-2: see your Interview-IQ Exhibits file.", italic=True, color=GREY)
    f = os.path.join(out, f"InterviewIQ_Memo_Template_{c['id']}.docx"); d.save(f); return f


# ---------------------------------------------------------------- draft exhibits
def exhibits_doc(L, E, out):
    c = L["case"]; d = base_doc()
    para(d, f"{c['title']} — Draft Exhibits", bold=True, size=18, color=NAVY, after=2)
    para(d, f"Built by Interview-IQ from {L.get('student', 'the student')}'s interviews · {datetime.date.today():%B %d, %Y}", size=10, color=GREY, after=10)
    boxed(d, [
        "These are drafts built only from your own interview evidence and the case background. Each claim names its source.",
        "Red [gap] entries mark evidence you still need. Ask a follow-up, check the case, or leave the cell out.",
        "Check every figure, rewrite the exhibits in your own words, and decide what to keep.",
        "Every Impact Summary is blank on purpose: writing it is how you show you understand the exhibit.",
    ], "How to use these drafts")
    for ex in E.get("exhibits", []):
        d.add_heading(f"Exhibit {ex['letter']}. {ex['title']}", 2)
        if ex.get("purpose"):
            para(d, ex["purpose"], italic=True, color=GREY, size=10)
        if ex.get("table"):
            table(d, ex["table"]["columns"], ex["table"]["rows"])
        for b in ex.get("bullets", []):
            d.add_paragraph(b, style="List Bullet")
        if ex.get("note"):
            para(d, ex["note"], size=10, color=GREY)
        impact(d, ex["title"])
    if E.get("gaps"):
        d.add_heading("Evidence gaps to close", 2)
        for g in E["gaps"]:
            d.add_paragraph(g, style="List Bullet")
    f = os.path.join(out, f"InterviewIQ_Draft_Exhibits_{c['id']}.docx"); d.save(f); return f


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True); ap.add_argument("--exhibits"); ap.add_argument("--out", default="/mnt/user-data/outputs")
    ap.add_argument("--template-only", action="store_true")
    a = ap.parse_args()
    L = json.load(open(a.ledger, encoding="utf-8")); os.makedirs(a.out, exist_ok=True)
    print("Wrote", memo_template(L, a.out))
    if not a.template_only:
        if not a.exhibits:
            raise SystemExit("--exhibits is required unless --template-only")
        print("Wrote", exhibits_doc(L, json.load(open(a.exhibits, encoding="utf-8")), a.out))
