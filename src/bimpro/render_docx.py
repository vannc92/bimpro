"""Cây tài liệu -> tệp Word (.docx).

Định dạng (style, đánh số tự động, đầu/cuối trang, lề, bìa) lấy từ khuôn ``library/base.docx``,
được chép từ bản BEP mẫu do người dùng chỉnh tay. Muốn đổi định dạng thì sửa style trong khuôn,
không sửa trong mã:

- Heading 1–4 đánh số tự động (1. / 1.1. / 1.1.1. / 1.); chương cấp 1 có nền tối, chữ trắng.
- Body Text 1..4: đoạn văn theo cấp tiêu đề hiện hành (thụt lề khác nhau).
- Body Text 21 / 22: gạch đầu dòng; BANG / HINH VE: chú thích bảng, hình (tự đánh số).
- Bìa là một section riêng, không đầu/cuối trang; phần còn lại đánh số trang từ 1.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, Twips

from . import LIBRARY_DIR
from .compose import Bullet, Doc, Figure, Heading, Para, Table
from .models import Project

BASE = LIBRARY_DIR / "base.docx"
_INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")

# trang bìa (section 1) và trang nội dung (section 2) theo bản mẫu, đơn vị twip
_COVER_SECT = (
    '<w:sectPr {ns}><w:pgSz w:w="11907" w:h="16840" w:code="9"/>'
    '<w:pgMar w:top="1418" w:right="1134" w:bottom="1418" w:left="1701" w:header="680" w:footer="680" w:gutter="0"/>'
    '<w:cols w:space="720"/><w:docGrid w:linePitch="354"/></w:sectPr>'
)
_LANDSCAPE = dict(w=16838, h=11906, top=1411, bottom=1411, left=1418, right=1134)

_BODY_STYLE = {1: "Body Text 1", 2: "Body Text 2", 3: "Body Text 3", 4: "Body Text 4"}
_TABLE_HEADER_FILL = "D9D9D9"
_ROW_HEIGHT = 432  # twip, chiều cao tối thiểu một dòng bảng (bản mẫu)


# ------------------------------------------------------------------ tiện ích XML


def _shade(cell, color=_TABLE_HEADER_FILL):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def _row_props(row, header=False):
    row.height = Twips(_ROW_HEIGHT)
    if header:
        el = OxmlElement("w:tblHeader")
        el.set(qn("w:val"), "true")
        row._tr.get_or_add_trPr().append(el)


def _runs(paragraph, text: str, size=None, bold=None, italic=None):
    """Thêm chữ có **đậm** và *nghiêng* vào đoạn; không đặt phông (theo style)."""
    for part in _INLINE.split(text):
        if not part:
            continue
        b, i = bold, italic
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part, b = part[2:-2], True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part, i = part[1:-1], True
        run = paragraph.add_run(part)
        if size:
            run.font.size = Pt(size)
        if b is not None:
            run.bold = b
        if i is not None:
            run.italic = i


def _page_break(d):
    p = d.add_paragraph()
    p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run().add_break(WD_BREAK.PAGE)


def _fldchar(paragraph, kind: str):
    run = paragraph.add_run()
    el = OxmlElement("w:fldChar")
    el.set(qn("w:fldCharType"), kind)
    run._r.append(el)
    return run


# ------------------------------------------------------------------ đầu trang, cuối trang


def _hf_run(text: str, italic=False) -> str:
    rpr = "<w:rPr>" + ("<w:i/><w:iCs/>" if italic else "") + '<w:sz w:val="20"/></w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


_HF_TAB = '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:tab/></w:r>'
_HF_PAGE = (
    '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
    '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>1</w:t></w:r>'
    '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>'
)


def _hf_para(style: str, width: int, runs: str, border: str | None = None) -> str:
    pbdr = ""
    if border == "bottom":
        pbdr = '<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:pBdr>'
    elif border == "top":
        pbdr = '<w:pBdr><w:top w:val="single" w:sz="4" w:space="1" w:color="auto"/></w:pBdr>'
    return (
        f"<w:p {nsdecls('w')}><w:pPr><w:pStyle w:val=\"{style}\"/>{pbdr}"
        f'<w:tabs><w:tab w:val="clear" w:pos="4680"/><w:tab w:val="clear" w:pos="9360"/>'
        f'<w:tab w:val="right" w:pos="{width}"/></w:tabs>'
        '<w:spacing w:before="0" w:after="0"/><w:rPr><w:sz w:val="20"/></w:rPr></w:pPr>'
        f"{runs}</w:p>"
    )


def _fill_part(part_element, paragraphs: list[str]):
    for p in list(part_element):
        part_element.remove(p)
    for xml in paragraphs:
        part_element.append(parse_xml(xml))


def _header_footer(section, project: Project, doc: Doc, width: int):
    g = project.general
    owner = g.owner_short or "«…»"
    author = g.author_short or "«…»"
    name = g.name_short or g.name or "«…»"
    title = g.header_title or g.report_title or "«…»"
    _fill_part(
        section.header._element,
        [
            _hf_para("Header", width, _hf_run(owner) + _HF_TAB + _hf_run(f"Dự án {name}", italic=True)),
            _hf_para("Header", width, _hf_run(author) + _HF_TAB + _hf_run(title), border="bottom"),
        ],
    )
    label = f"{doc.info.label} – {doc.info.short}" if doc.info.label else doc.info.short
    _fill_part(
        section.footer._element,
        [
            _hf_para("Footer", width, _hf_run(label) + _HF_TAB + _hf_run("Trang ") + _HF_PAGE, border="top"),
            _hf_para("Footer", width, _hf_run(project.doc.issue_text or "«…»"), border="top"),
        ],
    )


# ------------------------------------------------------------------ bìa, mục lục


def _centered(d, text, size=None, bold=None, after=None):
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if after is not None:
        p.paragraph_format.space_after = Twips(after)
    _runs(p, text, size, bold)
    return p


def _cover(d, project: Project, doc: Doc):
    g, c = project.general, project.doc
    owner = next((x.name for x in g.parties if x.short == g.owner_short), g.owner_short)
    _centered(d, (owner or "«CHỦ ĐẦU TƯ»").upper(), bold=True)
    _centered(d, (g.author_name or "«ĐƠN VỊ LẬP»").upper(), bold=True, after=1200)
    _centered(d, f"DỰ ÁN {(g.name or '«…»').upper()}", 16, True)
    if g.package:
        _centered(d, g.package)
    _centered(d, g.report_title or "«…»", bold=True, after=960)
    _centered(d, doc.full_title, 20, True, after=240)
    if doc.info.code:
        _centered(d, f"Mã hiệu: {doc.info.code}", 12)
    _centered(d, c.month or "«…»", after=1200)

    signers = [("Thực hiện", c.prepared_by), ("Kiểm tra", c.checked_by)]
    if c.approved_by:
        signers.append(("Phê duyệt", c.approved_by))
    t = d.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for cell, text in zip(t.rows[0].cells, ("", "Họ và tên", "Ngày", "Ký tên")):
        _cell_text(cell, text, None, True, WD_ALIGN_PARAGRAPH.CENTER, tight=True)
        _shade(cell)
    for role, name in signers:
        cells = t.add_row().cells
        _cell_text(cells[0], f"{role}:", None, True, tight=True)
        _cell_text(cells[1], name or "«…»", tight=True)
        _cell_text(cells[2], c.sign_date or "", align=WD_ALIGN_PARAGRAPH.CENTER, tight=True)
        cells[3].paragraphs[0].paragraph_format.space_after = Twips(360)
    _fix_widths(t, [Twips(2268)] * 4)
    # kết thúc section bìa: đoạn trống mang dấu ngắt section (không đầu/cuối trang)
    d.add_paragraph()._p.get_or_add_pPr().append(parse_xml(_COVER_SECT.format(ns=nsdecls("w"))))


def _toc(d, doc: Doc):
    """Trường mục lục của Word; kết quả tạm (chưa có số trang) để xem được khi chưa cập nhật."""
    _centered(d, "MỤC LỤC", bold=True)
    heads = [b for b in doc.blocks if isinstance(b, Heading) and b.level <= 3]
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
        p.style = d.styles[f"toc {h.level}"]
        _runs(p, f"{h.number}.\t{h.text}")
    _fldchar(p, "end")
    _page_break(d)


# ------------------------------------------------------------------ bảng, hình


def _cell_text(cell, text: str, size=None, bold=None, align=None, tight=False):
    lines = text.split("\n") if text else [""]
    for k, line in enumerate(lines):
        p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
        p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(1)
        if align is not None:
            p.alignment = align
        _runs(p, line, size, bold)


def _table(d, b: Table, width: int, size):
    if b.caption:
        d.add_paragraph(b.caption, style="BANG")
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
    _row_props(hdr, header=True)
    for k, cell in enumerate(hdr.cells):
        _cell_text(cell, b.header[k] if k < len(b.header) else "", size, True, WD_ALIGN_PARAGRAPH.CENTER)
        _shade(cell)
    for row in b.rows:
        r = t.add_row()
        _row_props(r)
        cells = r.cells
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


def _fix_widths(t, col_w):
    """Bề rộng cột cố định (Word và LibreOffice cùng hiển thị đúng)."""
    tblw = t._tbl.tblPr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        t._tbl.tblPr.append(tblw)
    tblw.set(qn("w:w"), str(int(sum(col_w) / 635)))
    tblw.set(qn("w:type"), "dxa")
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
        p.paragraph_format.keep_with_next = True  # giữ chú thích cùng trang với hình
        p.add_run().add_picture(str(path), width=int(width * 0.95))
    else:
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = p.paragraph_format.space_after = Twips(1200)
        run = p.add_run(f"«Chèn hình: {b.caption}»")
        run.font.size = Pt(12)
        run.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
        d.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.add_paragraph(b.caption, style="HINH VE")


# ------------------------------------------------------------------ dựng tài liệu


def _body_section(d, landscape: bool) -> int:
    """Chỉnh section nội dung (section cuối) theo hướng giấy; trả về bề rộng vùng chữ (twip)."""
    sec = d.sections[-1]
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Twips(_LANDSCAPE["w"]), Twips(_LANDSCAPE["h"])
        sec.top_margin, sec.bottom_margin = Twips(_LANDSCAPE["top"]), Twips(_LANDSCAPE["bottom"])
        sec.left_margin, sec.right_margin = Twips(_LANDSCAPE["left"]), Twips(_LANDSCAPE["right"])
    return int((sec.page_width - sec.left_margin - sec.right_margin) / 635)


def _clear_body(d):
    body = d.element.body
    keep = body.sectPr
    for el in list(body):
        if el is not keep:
            body.remove(el)


def _update_fields_on_open(d):
    """Thêm <w:updateFields/> đúng vị trí trong w:settings (Word kiểm tra thứ tự phần tử)."""
    st = d.settings.element
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    for tag in ("hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids"):
        nxt = st.find(qn(f"w:{tag}"))
        if nxt is not None:
            nxt.addprevious(upd)
            return
    st.append(upd)


def render(project: Project, doc: Doc, out: Path, base: Path | None = None) -> Path:
    """Xuất ``doc`` ra tệp ``out``. ``base`` là thư mục dự án (để tìm tệp ảnh)."""
    base = base or Path(".")
    landscape = doc.orientation == "landscape"
    d = Document(str(BASE))
    _clear_body(d)
    width_tw = _body_section(d, landscape)
    width = width_tw * 635
    tsize = 11 if landscape else None  # bảng khổ ngang thu chữ lại; khổ đứng dùng cỡ chữ của style

    _cover(d, project, doc)
    _toc(d, doc)
    _header_footer(d.sections[-1], project, doc, width_tw)

    first_h1 = True
    ctx = 1  # cấp tiêu đề hiện hành, quyết định style đoạn văn
    blocks = doc.blocks
    for i, b in enumerate(blocks):
        if isinstance(b, Heading):
            if b.level == 1 and not first_h1 and doc.info.kind == "bep":
                _page_break(d)
            first_h1 = False
            ctx = b.level
            p = d.add_paragraph(style=f"Heading {b.level}")
            run = p.add_run(b.text)
            if b.level == 1:  # chữ trắng trên nền tối do style; color=auto để Word tự đảo màu
                color = OxmlElement("w:color")
                color.set(qn("w:val"), "auto")
                run._r.get_or_add_rPr().append(color)
        elif isinstance(b, Para):
            if b.style == "minor":
                ctx = 4
                _runs(d.add_paragraph(style="Heading 4"), b.text)
                continue
            p = d.add_paragraph(style=_BODY_STYLE[min(ctx, 4)])
            if b.style == "syntax":
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.line_spacing = 1.1
                _runs(p, b.text, bold=True)
            else:
                _runs(p, b.text)
        elif isinstance(b, Bullet):
            deep = ctx >= 3
            p = d.add_paragraph(style="Body Text 22" if deep else "Body Text 21")
            if b.level == 2:
                ppr = p._p.get_or_add_pPr()
                num = ppr.get_or_add_numPr()
                num.get_or_add_ilvl().val = 1
                num.get_or_add_numId().val = 5 if deep else 4
                p.paragraph_format.left_indent = Twips(2160 if deep else 1440)
                p.paragraph_format.first_line_indent = Twips(-360)
            _runs(p, b.text)
        elif isinstance(b, Table):
            _table(d, b, width, tsize)
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            if nxt is None or isinstance(nxt, Table):
                d.add_paragraph().paragraph_format.space_after = Pt(0)  # tách hai bảng liền nhau
        elif isinstance(b, Figure):
            _figure(d, b, base, width)

    # yêu cầu Word cập nhật mục lục khi mở tệp
    _update_fields_on_open(d)
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
