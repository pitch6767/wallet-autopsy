"""Petit convertisseur markdown -> PDF (titres, paragraphes, tableaux, encadres) pour les rapports bot95."""
import sys, re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

src, outf, titre_pied = sys.argv[1], sys.argv[2], sys.argv[3]
F, FB = "Helvetica", "Helvetica-Bold"
p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if os.path.exists(p):
    pdfmetrics.registerFont(TTFont("DV", p)); pdfmetrics.registerFont(TTFont("DVB", p.replace("Sans.ttf", "Sans-Bold.ttf"))); F, FB = "DV", "DVB"
ss = getSampleStyleSheet()
BLEU = colors.HexColor("#1F3864")
ST = {"#": ParagraphStyle("h1", parent=ss["Heading1"], fontName=FB, fontSize=16, spaceAfter=8, textColor=BLEU),
      "##": ParagraphStyle("h2", parent=ss["Heading2"], fontName=FB, fontSize=12.5, spaceBefore=10, spaceAfter=5, textColor=BLEU),
      "###": ParagraphStyle("h3", parent=ss["Heading3"], fontName=FB, fontSize=10.5, spaceBefore=6, spaceAfter=4, textColor=BLEU)}
P = ParagraphStyle("p", parent=ss["BodyText"], fontName=F, fontSize=9.3, leading=13.2, spaceAfter=5)
BOX = ParagraphStyle("box", parent=P, backColor=colors.HexColor("#FFF4E5"), borderPadding=6, spaceBefore=4, spaceAfter=8)
CEL = ParagraphStyle("c", parent=P, fontSize=7.3, leading=8.8, spaceAfter=0)
HEAD = ParagraphStyle("hh", parent=CEL, fontName=FB, textColor=colors.white)


def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w])([+−-]\d[\d' ]*(?:[.,]\d+)?\s?\$)", lambda m: f"<font color='{'#c0362c' if m.group(1)[0] in '−-' else '#12805c'}'>{m.group(1)}</font>", t)
    return t


def table(rows):
    n = len(rows[0]); W = A4[0] - 28 * mm
    first = 9 * mm if rows[0][0].strip() == '#' else (min(70 * mm, W * 0.38) if n > 3 else W * 0.45)
    widths = [first] + [(W - first) / (n - 1)] * (n - 1)
    cs = ParagraphStyle("cs", parent=CEL, fontSize=6.3, leading=7.6) if n > 10 else CEL
    hs = ParagraphStyle("hs", parent=HEAD, fontSize=6.3, leading=7.6) if n > 10 else HEAD
    data = [[Paragraph(inline(c), hs) for c in rows[0]]] + [[Paragraph(inline(c), cs) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), BLEU), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BFBFBF")),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")])]))
    return t


S, rows = [], []
for line in open(src, encoding="utf-8").read().split("\n") + [""]:
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells): rows.append(cells)
        continue
    if rows: S += [table(rows), Spacer(1, 6)]; rows = []
    if not line.strip(): continue
    if line.strip() == "---PAGE---": S.append(PageBreak()); continue
    m = re.match(r"(#{1,3})\s+(.*)", line)
    if m: S.append(Paragraph(inline(m.group(2)), ST[m.group(1)])); continue
    if line.startswith("> "): S.append(Paragraph(inline(line[2:]), BOX)); continue
    if line.startswith("- "): S.append(Paragraph("• " + inline(line[2:]), P)); continue
    S.append(Paragraph(inline(line), P))


def pied(c, d):
    c.saveState(); c.setFont(F, 7); c.setFillColor(colors.grey)
    c.drawString(14 * mm, 8 * mm, titre_pied); c.drawRightString(A4[0] - 14 * mm, 8 * mm, f"page {d.page}"); c.restoreState()


SimpleDocTemplate(outf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm, title=titre_pied).build(S, onFirstPage=pied, onLaterPages=pied)
print(outf)
