"""Build meghallgatas_felkeszules.docx from docs/meghallgatas_felkeszules.md.

Handles the Markdown subset used in that file: headings, paragraphs, bullets,
numbered items, checkboxes, tables, quotes, code blocks, **bold**, *italic*
and `code`. Plain-text formulas get real sub- and superscripts: η_th, ṁ_f and
N2_idle become subscripts, OPR^(−(γ−1)/γ) and 26,96^0,2857 superscripts.
Requires python-docx.
"""
import os
import re

from docx import Document
from docx.shared import Cm, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'docs', 'meghallgatas_felkeszules.md')
TARGET = os.path.join(ROOT, 'meghallgatas_felkeszules.docx')

INLINE = re.compile(r'(\*\*.+?\*\*|`[^`]+`|\*[^*\s][^*]*\*)')
# A subscript follows a letter or digit: η_th, V_0, N2_idle.
SUBSCRIPT = re.compile(r'(?<=[^\W_])_([^\W_]+)')
# A superscript is ^ followed by a bracketed group or a (signed) number/word.
SUPERSCRIPT = re.compile(r'\^(?:\(|([−-]?[\d,.]*\d|[^\W_]+))')


def add_formula_text(paragraph, text, size=None):
    """Add text, turning _x into subscript and ^(...) / ^x into superscript."""
    runs = []  # (text, kind)
    pos = 0
    while pos < len(text):
        sub = SUBSCRIPT.search(text, pos)
        sup = SUPERSCRIPT.search(text, pos)
        match = min((m for m in (sub, sup) if m), key=lambda m: m.start(), default=None)
        if match is None:
            runs.append((text[pos:], None))
            break
        runs.append((text[pos:match.start()], None))
        if match.re is SUBSCRIPT:
            runs.append((match.group(1), 'sub'))
            pos = match.end()
        elif match.group(1) is not None:
            runs.append((match.group(1), 'sup'))
            pos = match.end()
        else:  # bracketed exponent: take everything up to the matching ')'
            depth, end = 1, match.end()
            while end < len(text) and depth:
                depth += {'(': 1, ')': -1}.get(text[end], 0)
                end += 1
            runs.append((text[match.end():end - 1], 'sup'))
            pos = end
    for chunk, kind in runs:
        if not chunk:
            continue
        run = paragraph.add_run(chunk)
        run.font.subscript = kind == 'sub'
        run.font.superscript = kind == 'sup'
        if size:
            run.font.size = Pt(size)


def add_inline(paragraph, text, size=None):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('`') and part.endswith('`'):
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Courier New'
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        else:
            add_formula_text(paragraph, part, size)
            continue
        if size:
            run.font.size = Pt(size)


def split_row(line):
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def add_table(doc, rows):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = 'Table Grid'
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            paragraph = table.cell(r, c).paragraphs[0]
            add_inline(paragraph, f'**{text}**' if r == 0 and text else text, size=9)
    doc.add_paragraph()


def build(lines):
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)
    section = doc.sections[0]
    section.left_margin = section.right_margin = Cm(2.0)
    section.top_margin = section.bottom_margin = Cm(2.0)

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line == '---':
            i += 1
        elif line.startswith('```'):
            i += 1
            while not lines[i].startswith('```'):
                paragraph = doc.add_paragraph()
                run = paragraph.add_run(lines[i].rstrip())
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
                i += 1
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                row = split_row(lines[i])
                if not all(re.fullmatch(r':?-+:?', cell) for cell in row):
                    rows.append(row)
                i += 1
            add_table(doc, rows)
        elif line.startswith('# '):
            doc.add_paragraph(line[2:], style='Title')
            i += 1
        elif line.startswith('## '):
            doc.add_heading(line[3:], level=1)
            i += 1
        elif line.startswith('### '):
            doc.add_heading(line[4:], level=2)
            i += 1
        elif line.startswith('> '):
            paragraph = doc.add_paragraph()
            paragraph.paragraph_format.left_indent = Cm(0.8)
            add_inline(paragraph, f'*{line[2:]}*' if '`' not in line else line[2:])
            i += 1
        elif line.startswith('- [ ] '):
            add_inline(doc.add_paragraph(style='List Paragraph'), '☐ ' + line[6:])
            i += 1
        elif line.startswith('- '):
            add_inline(doc.add_paragraph(style='List Bullet'), line[2:])
            i += 1
        elif re.match(r'\d+\. ', line):
            add_inline(doc.add_paragraph(style='List Paragraph'), line)
            i += 1
        else:
            add_inline(doc.add_paragraph(), line)
            i += 1
    return doc


if __name__ == '__main__':
    with open(SOURCE, encoding='utf-8') as f:
        build(f.read().splitlines()).save(TARGET)
    print(f'Wrote {TARGET}')
