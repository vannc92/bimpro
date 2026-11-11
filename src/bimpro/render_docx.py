"""Cây tài liệu -> tệp Word (.docx)."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from .compose import Bullet, Doc, Figure, Heading, Para, Table
from .models import Project

FONT = "Times New Roman"
_INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")


# ------------------------------------------------------------------ tiện ích XML


def _set_font(style_or_run, size=None, bold=None, italic=None):
    f = style_or_run.font
    f.name = FONT
    rpr = style_or_run.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(a), FONT)
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic


def _field(paragraph, instr: str, placeholder: str = ""):
    run = paragraph.add_run()
    for kind in ("begin", None, "separate", "text", "end"):
        if kind is None:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = instr
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = placeholder
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run._r.append(el)
    return run


def _border(paragraph, side: str):
    ppr = paragraph._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), "6")
    el.set(qn("w:space"), "1")
    el.set(qn("w:color"), "000000")
    bdr.append(el)
    ppr.append(bdr)


def _shade(cell, color="D9D9D9"):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def _repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)


def _runs(paragraph, text: str, size=None, bold=None, italic=None):
    """Thêm chữ có **đậm** và *nghiêng* vào đoạn."""
    for part in _INLINE.split(text):
        if not part:
            continue
        b, i = bold, italic
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part, b = part[2:-2], True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part, i = part[1:-1], True
        _set_font(paragraph.add_run(part), size, b, i)


# ------------------------------------------------------------------ dựng tài liệu


def _styles(d):
    for name in ("Header", "Footer"):
        ppr = d.styles[name].element.pPr
        if ppr is not None and ppr.find(qn("w:tabs")) is not None:
            ppr.remove(ppr.find(qn("w:tabs")))
    normal = d.styles["Normal"]
    _set_font(normal, 13)
    pf = normal.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(3), Pt(3), 1.15
    for name, size, italic in (("Heading 1", 13, False), ("Heading 2", 13, False), ("Heading 3", 13, True)):
        st = d.styles[name]
        _set_font(st, size, True, italic)
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(12 if name == "Heading 1" else 8)
        st.paragraph_format.space_after = Pt(4)
        st.paragraph_format.keep_with_next = True


def _page(section, landscape: bool):
    w, h = Cm(21.0), Cm(29.7)
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = h, w
    else:
        section.page_width, section.page_height = w, h
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin, section.right_margin = Cm(3 if not landscape else 2), Cm(2)
    section.header_distance = section.footer_distance = Cm(1)


def _text_width(section) -> int:
    return section.page_width - section.left_margin - section.right_margin


def _header_footer(section, project: Project, doc: Doc):
    width = _text_width(section)
    g = project.general
    hp = section.header.paragraphs[0]
    hp.paragraph_format.tab_stops.add_tab_stop(width // 2, WD_TAB_ALIGNMENT.CENTER)
    hp.paragraph_format.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
    _runs(hp, f"{g.owner_short or '«…»'}\tDự án {g.name or '«…»'}\t{g.author_short or '«…»'}", 10)
    hp2 = section.header.add_paragraph()
    hp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _runs(hp2, g.report_title or "«…»", 10)
    _border(hp2, "bottom")

    fp = section.footer.paragraphs[0]
    fp.paragraph_format.tab_stops.add_tab_stop(width // 2, WD_TAB_ALIGNMENT.CENTER)
    fp.paragraph_format.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
    _border(fp, "top")
    label = f"{doc.info.label} – {doc.info.short}" if doc.info.label else doc.info.short
    _runs(fp, f"{label}\tTrang ", 10)
    _set_font(_field(fp, "PAGE", "1"), 10)
    _runs(fp, f"\t{project.doc.issue_text or '«…»'}", 10)


def _centered(d, text, size, bold=True, space_after=6):
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    _runs(p, text, size, bold)
    return p


def _cover(d, project: Project, doc: Doc):
    g, c = project.general, project.doc
    owner = next((x.name for x in g.parties if x.short == g.owner_short), g.owner_short)
    _centered(d, (owner or "«CHỦ ĐẦU TƯ»").upper(), 13)
    _centered(d, (g.author_name or "«ĐƠN VỊ LẬP»").upper(), 13, space_after=60)
    _centered(d, f"DỰ ÁN {(g.name or '«…»').upper()}", 16)
    if g.package:
        _centered(d, g.package, 13, bold=False)
    _centered(d, g.report_title or "«…»", 13, space_after=48)
    _centered(d, doc.full_title, 20, space_after=12)
    if doc.info.code:
        _centered(d, f"Mã hiệu: {doc.info.code}", 12, bold=False)
    _centered(d, c.month or "«…»", 13, bold=False, space_after=60)

    signers = [("Thực hiện", c.prepared_by), ("Kiểm tra", c.checked_by)]
    if c.approved_by:
        signers.append(("Phê duyệt", c.approved_by))
    t = d.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, text in zip(t.rows[0].cells, ("", "Họ và tên", "Ngày", "Ký tên")):
        _cell_text(cell, text, 12, True, WD_ALIGN_PARAGRAPH.CENTER)
        _shade(cell)
    for role, name in signers:
        cells = t.add_row().cells
        _cell_text(cells[0], f"{role}:", 12, True)
        _cell_text(cells[1], name or "«…»", 12)
        _cell_text(cells[2], c.sign_date or "", 12, align=WD_ALIGN_PARAGRAPH.CENTER)
        cells[3].paragraphs[0].paragraph_format.space_after = Pt(18)
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def _fldchar(paragraph, kind: str):
    run = paragraph.add_run()
    el = OxmlElement("w:fldChar")
    el.set(qn("w:fldCharType"), kind)
    run._r.append(el)
    return run


def _toc(d, doc: Doc):
    """Trường mục lục của Word; kết quả tạm (không số trang) để xem được khi chưa cập nhật."""
    _centered(d, "MỤC LỤC", 14)
    heads = [b for b in doc.blocks if isinstance(b, Heading) and b.level <= 2]
    first = d.add_paragraph()
    _fldchar(first, "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    first.add_run()._r.append(instr)
    _fldchar(first, "separate")
    p = first
    for k, h in enumerate(heads):
        if k:
            p = d.add_paragraph()
        p.paragraph_format.left_indent = Cm(0 if h.level == 1 else 0.6)
        p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(1)
        _runs(p, f"{h.number}. {h.text}", 12, h.level == 1)
    _fldchar(p, "end")
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def _cell_text(cell, text: str, size=12, bold=None, align=None):
    lines = text.split("\n") if text else [""]
    for k, line in enumerate(lines):
        p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
        p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        if align is not None:
            p.alignment = align
        _runs(p, line, size, bold)


def _table(d, b: Table, width: int, size: int):
    if b.caption:
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        _runs(p, f"Bảng {b.number}. {b.caption}", 12, True)
    ncol = max(len(b.header), max((len(r) for r in b.rows if not isinstance(r, tuple)), default=1))
    t = d.add_table(rows=1, cols=ncol)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    weights = b.widths if len(b.widths) == ncol else _auto_widths(b, ncol)
    total = sum(weights)
    col_w = [int(width * w / total) for w in weights]
    floor = int(Cm(1.0))  # cột hẹp nhất vẫn đủ chỗ cho số thứ tự hai chữ số
    for k, w in enumerate(col_w):
        if w < floor:
            big = col_w.index(max(col_w))
            col_w[big] -= floor - w
            col_w[k] = floor
    hdr = t.rows[0]
    _repeat_header(hdr)
    for k, cell in enumerate(hdr.cells):
        _cell_text(cell, b.header[k] if k < len(b.header) else "", size, True, WD_ALIGN_PARAGRAPH.CENTER)
        _shade(cell)
    for row in b.rows:
        cells = t.add_row().cells
        if isinstance(row, tuple):
            merged = cells[0].merge(cells[-1])
            _cell_text(merged, row[1], size, True)
            _shade(merged, "F2F2F2")
            continue
        for k, cell in enumerate(cells):
            text = row[k] if k < len(row) else ""
            short = len(text) <= 6 and "\n" not in text
            _cell_text(cell, text, size, align=WD_ALIGN_PARAGRAPH.CENTER if short else None)
    _fix_widths(t, col_w)
    d.add_paragraph().paragraph_format.space_after = Pt(0)


def _fix_widths(t, col_w):
    tblpr = t._tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        tblpr.append(tblw)
    tblw.set(qn("w:w"), str(int(sum(col_w) / 635)))
    tblw.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.append(layout)
    for k, gc in enumerate(t._tbl.tblGrid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(col_w[min(k, len(col_w) - 1)] / 635)))
    for row in t.rows:
        for k, cell in enumerate(row.cells):
            cell.width = col_w[min(k, len(col_w) - 1)]


def _auto_widths(b: Table, ncol: int) -> list[float]:
    """Ước lượng bề rộng cột theo độ dài nội dung (giới hạn 6..45 ký tự)."""
    w = [6.0] * ncol
    for row in [b.header] + [r for r in b.rows if not isinstance(r, tuple)]:
        for k, c in enumerate(row[:ncol]):
            longest = max((len(x) for x in c.split("\n")), default=0)
            w[k] = max(w[k], min(45.0, float(longest)))
    return w


def _figure(d, b: Figure, base: Path, width: int):
    path = base / b.image if b.image else None
    if path and path.exists():
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=int(width * 0.95))
    else:
        t = d.add_table(rows=1, cols=1)
        t.style = "Table Grid"
        cell = t.rows[0].cells[0]
        _cell_text(cell, f"«Chèn hình: {b.caption}»", 12, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell.paragraphs[0].paragraph_format.space_before = Pt(60)
        cell.paragraphs[0].paragraph_format.space_after = Pt(60)
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _runs(p, f"Hình {b.number}. {b.caption}", 12, True)


def render(project: Project, doc: Doc, out: Path, base: Path | None = None) -> Path:
    """Xuất ``doc`` ra tệp ``out``. ``base`` là thư mục dự án (để tìm tệp ảnh)."""
    base = base or Path(".")
    landscape = doc.orientation == "landscape"
    d = Document()
    _styles(d)
    sec = d.sections[0]
    _page(sec, landscape)
    sec.different_first_page_header_footer = True
    _header_footer(sec, project, doc)
    width = _text_width(sec)
    tsize = 11 if landscape else 12

    _cover(d, project, doc)
    _toc(d, doc)

    first_h1 = True
    for b in doc.blocks:
        if isinstance(b, Heading):
            if b.level == 1 and not first_h1 and doc.info.kind == "bep":
                d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            first_h1 = False
            d.add_heading(f"{b.number}. {b.text}", level=b.level)
        elif isinstance(b, Para):
            p = d.add_paragraph()
            if b.style == "syntax":
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _runs(p, b.text, 12, True)
            elif b.style == "minor":
                p.paragraph_format.keep_with_next = True
                _runs(p, b.text, None, True)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.first_line_indent = Cm(1)
                _runs(p, b.text)
        elif isinstance(b, Bullet):
            p = d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            indent = Cm(1.0 if b.level == 1 else 1.8)
            p.paragraph_format.left_indent = indent + Cm(0.6)
            p.paragraph_format.first_line_indent = -Cm(0.6)
            p.paragraph_format.tab_stops.add_tab_stop(indent + Cm(0.6))
            _runs(p, ("−" if b.level == 1 else "+") + "\t" + b.text)
        elif isinstance(b, Table):
            _table(d, b, width, tsize)
        elif isinstance(b, Figure):
            _figure(d, b, base, width)

    # yêu cầu Word cập nhật mục lục khi mở tệp
    settings = d.settings.element
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    settings.append(upd)
    d.core_properties.title = doc.full_title
    d.core_properties.author = project.general.author_short
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def output_name(project: Project, doc: Doc) -> str:
    stem = doc.info.code or doc.info.doc
    suffix = doc.info.label.replace("-", "") if doc.info.label else "BEP"
    rev = project.doc.revision
    name = f"{stem}_{suffix}" + (f"_{rev}" if rev else "")
    return re.sub(r'[\\/:*?"<>|\s]+', "-", name) + ".docx"
