"""Cây tài liệu -> HTML xem trước (cùng nguồn với bản Word)."""

from __future__ import annotations

import re
from html import escape

from .compose import Bullet, Doc, Figure, Heading, Para, Table


def _inline(text: str) -> str:
    t = escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"«[^»]*»", lambda m: f'<mark class="ph">{m[0]}</mark>', t)
    return t.replace("\n", "<br>")


def render(doc: Doc) -> str:
    out = [f'<h1 class="doc-title">{escape(doc.full_title)}</h1>']
    sid = None
    for b in doc.blocks:
        if b.sid != sid:
            if sid is not None:
                out.append("</div>")
            out.append(f'<div class="sec" data-sid="{b.sid}" id="s-{b.sid}">')
            sid = b.sid
        if isinstance(b, Heading):
            out.append(f"<h{b.level + 1}>{b.number}. {_inline(b.text)}</h{b.level + 1}>")
        elif isinstance(b, Para):
            cls = {"syntax": "syntax", "minor": "minor"}.get(b.style, "")
            out.append(f'<p class="{cls}">{_inline(b.text)}</p>')
        elif isinstance(b, Bullet):
            out.append(f'<p class="b{b.level}">{"−" if b.level == 1 else "+"} {_inline(b.text)}</p>')
        elif isinstance(b, Table):
            if b.caption:
                out.append(f'<p class="cap">Bảng {b.number}. {_inline(b.caption)}</p>')
            out.append("<table><thead><tr>" + "".join(f"<th>{_inline(h)}</th>" for h in b.header) + "</tr></thead><tbody>")
            for row in b.rows:
                if isinstance(row, tuple):
                    out.append(f'<tr class="grp"><td colspan="{len(b.header)}">{_inline(row[1])}</td></tr>')
                else:
                    out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table>")
        elif isinstance(b, Figure):
            img = f'<div class="fig">{"Ảnh: " + escape(b.image) if b.image else "«Chèn hình»"}</div>'
            out.append(img + f'<p class="cap">Hình {b.number}. {_inline(b.caption)}</p>')
    if sid is not None:
        out.append("</div>")
    return "\n".join(out)
