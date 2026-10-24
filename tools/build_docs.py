"""Build the SCMS design documents (PDF) from their Markdown sources.

Usage:
    py -3.12 tools/build_docs.py            # build both documents
    py -3.12 tools/build_docs.py --check    # parse the sources only

Sources live in "SCMS Documents/source/"; PDFs are written to
"SCMS Documents/". Only reportlab is required (see requirements-docs.txt).

The sources use a deliberately small Markdown subset. Anything outside it
stops the build with a file:line message, so no content is dropped silently:

    # / ## / ###        headings (bookmarked in the PDF outline)
    plain lines         paragraphs (consecutive lines are joined)
    - item              bullet list (indent a continuation line by 2 spaces)
    1. item             numbered list
    | a | b |           pipe table; the second line must be a |---|---| rule,
                        use \\| for a literal pipe inside a cell
    **bold**  `code`    the only inline formatting; a backslash-n inside
                        a table cell is a forced line break
    @widths 20 30 50    relative column widths for the NEXT table
    @cover ... @endcover   centred title block (org, department, title, ...)
    @pagebreak          start a new page
    @landscape / @portrait   start a new page in that orientation

Text must be encodable in Windows-1252 because the built-in PDF fonts are
used; characters outside that set (arrows, for example) are rejected.

The output is reproducible: reportlab's "invariant" mode fixes the PDF
timestamps and document id, so the same sources give the same bytes.
"""
import argparse
import re
import sys
from pathlib import Path

from reportlab import rl_config

rl_config.invariant = 1  # must be set before any canvas is created

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "SCMS Documents" / "source"
OUT_DIR = ROOT / "SCMS Documents"

DOCUMENTS = {
    "sad_v1.1.md": (
        "SCMS_SAD_v1.1.pdf",
        "Software Architecture and Design Specification",
        "SCMS SAD v1.1",
    ),
    "srs_v1.1.md": (
        "SCMS_SRS_v1.1.pdf",
        "Software Requirements Specification",
        "SCMS SRS v1.1",
    ),
}

MARGIN = 0.75 * inch
FOOTER_Y = 0.45 * inch

BLUE = colors.HexColor("#2F5597")
BLUE_LIGHT = colors.HexColor("#4472C4")
HEADER_FILL = colors.HexColor("#D9E2F3")
GREY = colors.HexColor("#555555")

BODY = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5, leading=12.5,
                      spaceAfter=5)
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=8.5, leading=10.5,
                      spaceAfter=0)
CELL_HEAD = ParagraphStyle("CellHead", parent=CELL, fontName="Helvetica-Bold")
HEADINGS = {
    1: ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, leading=19,
                      textColor=BLUE, spaceBefore=14, spaceAfter=6,
                      keepWithNext=1),
    2: ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11.5,
                      leading=15, textColor=BLUE_LIGHT, spaceBefore=10,
                      spaceAfter=4, keepWithNext=1),
    3: ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10, leading=13,
                      textColor=BLUE_LIGHT, spaceBefore=8, spaceAfter=3,
                      keepWithNext=1),
}
COVER_STYLES = [
    ParagraphStyle("Cover1", parent=BODY, fontName="Helvetica-Bold",
                   fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=2),
    ParagraphStyle("Cover2", parent=BODY, fontName="Helvetica-Bold",
                   fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=10),
    ParagraphStyle("Cover3", parent=BODY, fontName="Helvetica-Bold",
                   fontSize=21, leading=26, alignment=TA_CENTER, spaceAfter=10),
]
COVER_REST = ParagraphStyle("CoverRest", parent=BODY, fontName="Helvetica-Bold",
                            fontSize=9.5, leading=12.5, alignment=TA_CENTER,
                            spaceAfter=1)


class SourceError(Exception):
    """A problem in a Markdown source, reported as file:line: message."""

    def __init__(self, path, line, message):
        super().__init__(f"{path}:{line}: {message}")


class Heading(Paragraph):
    """A heading that remembers its level and text for the PDF outline."""

    def __init__(self, level, markup, plain):
        super().__init__(markup, HEADINGS[level])
        self.level = level
        self.plain = plain


# --------------------------------------------------------------------------
# Inline text
# --------------------------------------------------------------------------

def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def inline(text, path, line):
    """Turn the supported inline Markdown into reportlab paragraph markup."""
    try:
        text.encode("cp1252")
    except UnicodeEncodeError as exc:
        bad = text[exc.start]
        raise SourceError(
            path, line,
            f"character {bad!r} (U+{ord(bad):04X}) is not supported by the "
            "built-in PDF fonts; use plain ASCII or Windows-1252 text",
        )

    out = []
    bold = False
    code = False
    for token in re.split(r"(\*\*|`)", text):
        if token == "**":
            if code:
                raise SourceError(path, line, "'**' inside a code span")
            bold = not bold
            out.append("<b>" if bold else "</b>")
        elif token == "`":
            code = not code
            out.append('<font face="Courier" size="8.5">' if code
                       else "</font>")
        else:
            if not code and "*" in token:
                raise SourceError(
                    path, line,
                    "unsupported '*' (only **bold** and `code` are supported)",
                )
            out.append(escape(token).replace("\\n", "<br/>"))
    if bold or code:
        raise SourceError(path, line, "unterminated ** or ` marker")
    return "".join(out)


def plain_text(text):
    return text.replace("**", "").replace("`", "")


# --------------------------------------------------------------------------
# Markdown parsing
# --------------------------------------------------------------------------

RULE_RE = re.compile(r"^\|(\s*:?-{3,}:?\s*\|)+$")
HEADING_RE = re.compile(r"^(#{1,3}) (\S.*)$")
BULLET_RE = re.compile(r"^- (\S.*)$")
ORDERED_RE = re.compile(r"^(\d+)\. (\S.*)$")
REJECTED_PREFIXES = ("```", ">", "<", "![", "* ", "+ ", "---", "===", "~~~")


def split_row(line, path, number):
    body = line.strip()
    if not (body.startswith("|") and body.endswith("|")) or body == "|":
        raise SourceError(path, number, "table row must start and end with '|'")
    body = body[1:-1]
    cells = [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", body)]
    return cells


class Builder:
    def __init__(self, path):
        self.path = path
        self.story = []
        self.orientation = "portrait"
        self.pending_widths = None

    def avail_width(self):
        page = landscape(letter) if self.orientation == "landscape" else letter
        return page[0] - 2 * MARGIN

    def add_table(self, rows, first_line):
        cols = len(rows[0])
        for offset, row in enumerate(rows):
            if len(row) != cols:
                raise SourceError(
                    self.path, first_line + offset,
                    f"table row has {len(row)} cells, expected {cols}",
                )
        widths = self.pending_widths
        self.pending_widths = None
        if widths is None:
            widths = [1] * cols
        if len(widths) != cols:
            raise SourceError(
                self.path, first_line,
                f"@widths gives {len(widths)} values for {cols} columns",
            )
        total = float(sum(widths))
        col_widths = [self.avail_width() * w / total for w in widths]

        data = []
        for index, row in enumerate(rows):
            style = CELL_HEAD if index == 0 else CELL
            data.append([
                Paragraph(inline(cell, self.path, first_line + index
                                 + (1 if index else 0)), style)
                for cell in row
            ])
        table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_FILL),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        # Keep the heading(s) and intro line in front of a table from being
        # stranded at the bottom of a page, without forcing the whole table
        # onto the next page: start a new page only if little room is left.
        if self.story and isinstance(self.story[-1], Paragraph):
            start = len(self.story) - 1
            while start > 0 and isinstance(self.story[start - 1], Heading):
                start -= 1
            self.story[-1].keepWithNext = 0
            self.story.insert(start, CondPageBreak(1.6 * inch))
        self.story.append(table)
        self.story.append(Spacer(1, 8))

    def add_list(self, items, ordered, start, first_line):
        flow = [
            ListItem(Paragraph(inline(text, self.path, line), BODY),
                     leftIndent=16)
            for text, line in items
        ]
        if ordered:
            lst = ListFlowable(flow, bulletType="1", start=start,
                               bulletFormat="%s.", leftIndent=16,
                               bulletFontName="Helvetica", bulletFontSize=9.5)
        else:
            lst = ListFlowable(flow, bulletType="bullet", start="•",
                               leftIndent=16, bulletFontName="Helvetica",
                               bulletFontSize=9.5)
        self.story.append(lst)
        self.story.append(Spacer(1, 4))

    def add_cover(self, lines):
        if len(lines) < 3:
            raise SourceError(self.path, lines[0][1] if lines else 0,
                              "@cover needs at least three lines")
        self.story.append(Spacer(1, 0.2 * inch))
        for index, (text, number) in enumerate(lines):
            style = (COVER_STYLES[index] if index < len(COVER_STYLES)
                     else COVER_REST)
            self.story.append(Paragraph(inline(text, self.path, number), style))


def parse(path):
    """Parse one Markdown source into a list of flowables."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").split("\n")
    b = Builder(str(path))
    para = []          # (text, line)
    items = []         # list items
    list_kind = None   # "bullet" | "ordered"
    list_start = 1
    i = 0

    def flush_para():
        nonlocal para
        if para:
            joined = " ".join(t for t, _ in para)
            b.story.append(Paragraph(inline(joined, b.path, para[0][1]), BODY))
            para = []

    def flush_list():
        nonlocal items, list_kind, list_start
        if items:
            b.add_list(items, list_kind == "ordered", list_start, items[0][1])
            items, list_kind, list_start = [], None, 1

    while i < len(lines):
        raw = lines[i]
        number = i + 1
        line = raw.rstrip()
        i += 1

        if not line.strip():
            flush_para()
            flush_list()
            continue

        if raw.startswith("\t"):
            raise SourceError(b.path, number, "tab indentation is not supported")

        # --- directives -----------------------------------------------
        if line.startswith("@"):
            flush_para()
            flush_list()
            word, _, rest = line.partition(" ")
            if word == "@pagebreak" and not rest:
                b.story.append(PageBreak())
            elif word in ("@landscape", "@portrait") and not rest:
                b.orientation = word[1:]
                b.story.append(NextPageTemplate(b.orientation))
                b.story.append(PageBreak())
            elif word == "@widths":
                try:
                    b.pending_widths = [float(v) for v in rest.split()]
                except ValueError:
                    raise SourceError(b.path, number, "@widths needs numbers")
                if not b.pending_widths or min(b.pending_widths) <= 0:
                    raise SourceError(b.path, number,
                                      "@widths needs positive numbers")
            elif word == "@cover" and not rest:
                cover = []
                while True:
                    if i >= len(lines):
                        raise SourceError(b.path, number,
                                          "@cover without @endcover")
                    entry = lines[i].rstrip()
                    i += 1
                    if entry == "@endcover":
                        break
                    if entry.strip():
                        cover.append((entry.strip(), i))
                b.add_cover(cover or [("", number)])
            else:
                raise SourceError(b.path, number,
                                  f"unknown directive {line!r}")
            continue

        # --- headings -------------------------------------------------
        if line.startswith("#"):
            match = HEADING_RE.match(line)
            if not match:
                raise SourceError(
                    b.path, number,
                    "unsupported heading (use '# ', '## ' or '### ' + text)")
            flush_para()
            flush_list()
            level = len(match.group(1))
            heading = match.group(2)
            b.story.append(Heading(level, inline(heading, b.path, number),
                                   plain_text(heading)))
            continue

        # --- tables ---------------------------------------------------
        if line.startswith("|"):
            flush_para()
            flush_list()
            first = number
            block = [(line, number)]
            while i < len(lines) and lines[i].startswith("|"):
                block.append((lines[i].rstrip(), i + 1))
                i += 1
            if len(block) < 3 or not RULE_RE.match(block[1][0]):
                raise SourceError(
                    b.path, first,
                    "table needs a header row, a |---| rule and a body row")
            rows = [split_row(block[0][0], b.path, first)]
            rows += [split_row(t, b.path, n) for t, n in block[2:]]
            cols = len(rows[0])
            rule_cells = len(re.findall(r":?-{3,}:?", block[1][0]))
            if rule_cells != cols:
                raise SourceError(b.path, block[1][1],
                                  "rule row does not match the header cells")
            b.add_table(rows, first)
            continue

        # --- lists ----------------------------------------------------
        bullet = BULLET_RE.match(line)
        ordered = ORDERED_RE.match(line)
        if bullet or ordered:
            flush_para()
            kind = "bullet" if bullet else "ordered"
            if items and kind != list_kind:
                flush_list()
            if not items:
                list_kind = kind
                list_start = int(ordered.group(1)) if ordered else 1
            items.append(((bullet or ordered).group(bullet and 1 or 2), number))
            continue

        if line.startswith("  ") and items:
            last_text, last_no = items[-1]
            items[-1] = (last_text + " " + line.strip(), last_no)
            continue

        # --- paragraphs -----------------------------------------------
        if line.startswith(REJECTED_PREFIXES) or "](" in line:
            raise SourceError(
                b.path, number,
                "unsupported Markdown (quotes, code fences, HTML, images, "
                "links and other bullet markers are not supported)")
        if line.startswith(" "):
            raise SourceError(b.path, number,
                              "unexpected indentation outside a list")
        flush_list()
        para.append((line, number))

    flush_para()
    flush_list()
    return b.story


# --------------------------------------------------------------------------
# PDF rendering
# --------------------------------------------------------------------------

def make_canvas_class(footer_title):
    class NumberedCanvas(canvas.Canvas):
        """Canvas that writes 'Page X of Y' once the page count is known."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_states = []

        def showPage(self):
            self._saved_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved_states)
            for state in self._saved_states:
                self.__dict__.update(state)
                self._draw_footer(total)
                super().showPage()
            super().save()

        def _draw_footer(self, total):
            width = self._pagesize[0]
            self.setFont("Helvetica", 8)
            self.setFillColor(GREY)
            self.drawCentredString(
                width / 2, FOOTER_Y,
                f"{footer_title}  |  Page {self._pageNumber} of {total}")

    return NumberedCanvas


class Document(BaseDocTemplate):
    """Document template that builds the PDF outline from headings."""

    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self._last_level = -1
        self._count = 0

    def afterFlowable(self, flowable):
        if isinstance(flowable, Heading):
            self._count += 1
            key = f"heading-{self._count}"
            level = min(flowable.level - 1, self._last_level + 1)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.plain, key, level, closed=0)
            self._last_level = level


def render(story, out_path, title, footer_title):
    portrait = letter
    wide = landscape(letter)
    bottom = MARGIN + 0.1 * inch

    def frame(size, name):
        return Frame(MARGIN, bottom, size[0] - 2 * MARGIN,
                     size[1] - MARGIN - bottom, id=name,
                     leftPadding=0, rightPadding=0, topPadding=0,
                     bottomPadding=0)

    doc = Document(
        str(out_path), pagesize=portrait, title=title,
        author="Project Team", subject="Smart Complaint Management System",
        creator="tools/build_docs.py (reportlab)",
    )
    doc.addPageTemplates([
        PageTemplate(id="portrait", frames=[frame(portrait, "p")],
                     pagesize=portrait),
        PageTemplate(id="landscape", frames=[frame(wide, "l")],
                     pagesize=wide),
    ])
    doc.build(story, canvasmaker=make_canvas_class(footer_title))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--source", type=Path, default=SOURCE_DIR,
                        help="directory holding the Markdown sources")
    parser.add_argument("--out", type=Path, default=OUT_DIR,
                        help="directory for the generated PDFs")
    parser.add_argument("--check", action="store_true",
                        help="parse the sources and stop; write nothing")
    args = parser.parse_args(argv)

    failed = False
    for source_name, (pdf_name, title, footer) in DOCUMENTS.items():
        source = args.source / source_name
        try:
            story = parse(source)
            if args.check:
                print(f"OK    {source} ({len(story)} flowables)")
                continue
            out_path = args.out / pdf_name
            render(story, out_path, title, footer)
            print(f"wrote {out_path}")
        except SourceError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            failed = True
        except FileNotFoundError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            failed = True
        except Exception as exc:  # layout failures, e.g. a row taller than a page
            print(f"ERROR building {pdf_name}: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
