"""Ghép tài liệu: dự án + thư viện mẫu -> cây tài liệu trung gian.

Mẫu tài liệu là tệp ``library/documents/<mã>.md``:

    ---
    title: KẾ HOẠCH THỰC HIỆN BIM (BEP)
    short: Kế hoạch thực hiện BIM
    kind: bep            # hoặc appendix
    ---
    # ma-muc | TIÊU ĐỀ CHƯƠNG
    ## ma-muc-con | Tiêu đề mục {when: p.bim.features.clash}
    Nội dung mục: Markdown rút gọn + biến Jinja2.

Cú pháp nội dung:
    - ý cấp 1            + ý cấp 2 (thụt 2 dấu cách)
    [Bảng#ma|10,30,60] Tên bảng      (dòng kế tiếp là bảng ``|`` hoặc ``{{ tbl(...) }}``)
    [Hình#ma] Tên hình
    > cú pháp/ví dụ canh giữa        ### tiêu đề nhỏ không đánh số
    @[ma] -> "Bảng 3"/"Hình 1"       @sec[ma-muc] -> "mục 5.2"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined
from jinja2.exceptions import TemplateError

from . import LIBRARY_DIR, PLACEHOLDER
from .models import Project

# ------------------------------------------------------------------ cây tài liệu


@dataclass
class Heading:
    level: int
    number: str
    text: str
    sid: str


@dataclass
class Para:
    text: str
    sid: str
    style: str = "body"  # body | syntax | minor


@dataclass
class Bullet:
    text: str
    sid: str
    level: int = 1


@dataclass
class Table:
    sid: str
    caption: str = ""
    ref: str = ""
    number: int = 0
    widths: list[float] = field(default_factory=list)
    header: list[str] = field(default_factory=list)
    rows: list = field(default_factory=list)  # list[list[str]] hoặc ("group", nhãn)


@dataclass
class Figure:
    sid: str
    caption: str
    ref: str = ""
    number: int = 0
    image: str = ""


@dataclass
class Issue:
    level: str  # error | warn | info
    where: str
    message: str


@dataclass
class Section:
    sid: str
    title: str
    level: int
    number: str = ""
    enabled: bool = True
    overridden: bool = False
    source: str = ""  # nội dung gốc trong thư viện
    when: str = ""


@dataclass
class DocInfo:
    doc: str
    code: str
    label: str  # "" với BEP, "PL-01" với phụ lục
    title: str
    short: str
    summary: str
    kind: str


@dataclass
class Doc:
    info: DocInfo
    orientation: str
    blocks: list
    sections: list[Section]
    issues: list[Issue]

    @property
    def full_title(self) -> str:
        if self.info.kind == "appendix":
            return f"PHỤ LỤC {self.info.label[3:]} – {self.info.title.upper()}"
        return self.info.title


# ------------------------------------------------------------------ thư viện


@lru_cache(maxsize=None)
def stages() -> dict:
    return yaml.safe_load((LIBRARY_DIR / "stages.yaml").read_text(encoding="utf-8"))


_HEAD = re.compile(r"^(#{1,3}) ([a-z0-9\-]+) \| (.+?)(?:\s*\{when:\s*(.+?)\})?\s*$")


@dataclass
class Template:
    doc: str
    meta: dict
    sections: list[Section]


def library_docs() -> list[str]:
    return sorted(p.stem for p in (LIBRARY_DIR / "documents").glob("*.md"))


@lru_cache(maxsize=None)
def load_template(doc: str) -> Template:
    path = LIBRARY_DIR / "documents" / f"{doc}.md"
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        _, fm, text = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    sections: list[Section] = []
    body: list[str] = []
    for line in text.splitlines():
        m = _HEAD.match(line)
        if m:
            if sections:
                sections[-1].source = "\n".join(body).strip("\n")
            body = []
            sections.append(Section(sid=m[2], title=m[3], level=len(m[1]), when=m[4] or ""))
        else:
            body.append(line)
    if sections:
        sections[-1].source = "\n".join(body).strip("\n")
    return Template(doc, meta, sections)


def doc_infos(project: Project) -> list[DocInfo]:
    """Danh mục tài liệu phát hành; số phụ lục sinh theo thứ tự, không gõ tay."""
    out, n = [], 0
    for ref in project.doc.documents:
        if not ref.enabled or ref.doc not in library_docs():
            continue
        meta = load_template(ref.doc).meta
        kind = meta.get("kind", "appendix")
        label = ""
        if kind == "appendix":
            n += 1
            label = f"PL-{n:02d}"
        out.append(
            DocInfo(ref.doc, ref.code, label, meta.get("title", ref.doc), meta.get("short", ""),
                    meta.get("summary", ""), kind)
        )
    return out


# ------------------------------------------------------------------ Jinja


class _Tables:
    """Bảng sinh từ dữ liệu: mẫu chèn dấu mốc, bộ phân tích đổi lại thành khối Table."""

    def __init__(self):
        self.items: list[tuple[list[str], list]] = []

    def tbl(self, headers, rows):
        rows = list(rows)
        if not rows:
            rows = [[PLACEHOLDER] * len(headers)]
        self.items.append((list(headers), rows))
        return f"\x02T{len(self.items) - 1}\x02"


def _cell(v) -> str:
    if isinstance(v, bool):
        return "X" if v else ""
    return "" if v is None else str(v).strip()


def _get(it, a: str) -> str:
    """Giá trị ô; ô trống hiện «…» trừ khi tên cột có hậu tố '?' (được phép trống)."""
    optional = a.endswith("?")
    v = _cell(getattr(it, a.rstrip("?"), ""))
    return v if v or optional else PLACEHOLDER


def rows(items, *attrs):
    """Danh sách đối tượng -> các dòng bảng. '#' là số thứ tự."""
    out = []
    for i, it in enumerate(items, 1):
        out.append([str(i) if a == "#" else _get(it, a) for a in attrs])
    return out


def grows(items, group_attr, *attrs, restart=True):
    """Như ``rows`` nhưng chèn dòng nhóm mỗi khi giá trị ``group_attr`` đổi."""
    out, last, i = [], object(), 0
    for it in items:
        g = getattr(it, group_attr)
        if g != last:
            if g:
                out.append(("group", g))
            last = g
            if restart:
                i = 0
        i += 1
        out.append([str(i) if a == "#" else _get(it, a) for a in attrs])
    return out


def split(value: str) -> list[str]:
    return [s.strip() for s in (value or "").split(";")]


def _finalize(v):
    return PLACEHOLDER if v is None or v == "" else v


def context(project: Project) -> dict:
    st = stages().get(project.stage) or {"code": project.stage, "name": project.stage}
    st = {"code": project.stage, **st}
    infos = doc_infos(project)
    by_doc = {d.doc: d for d in infos}

    def pl(doc):
        d = by_doc.get(doc)
        return d.label if d else f"«?{doc}»"

    def code(doc):
        d = by_doc.get(doc)
        return d.code if d and d.code else PLACEHOLDER

    return {
        "p": project,
        "A": project.general.author_role or "Tư vấn",
        "CDE": project.cde.name or PLACEHOLDER,
        "LOD": project.bim.lod or PLACEHOLDER,
        "stage": st,
        "f": project.bim.features,
        "docs": infos,
        "appendices": [d for d in infos if d.kind == "appendix"],
        "pl": pl,
        "code": code,
        "rows": rows,
        "grows": grows,
        "split": split,
        "PH": PLACEHOLDER,
    }


def _env() -> Environment:
    env = Environment(undefined=StrictUndefined, finalize=_finalize, trim_blocks=True,
                      lstrip_blocks=True, keep_trailing_newline=False)
    env.filters["split"] = split
    return env


# ------------------------------------------------------------------ phân tích nội dung

_CAP = re.compile(r"^\[(Bảng|Hình)(?:#([\w\-]+))?(?:\|([\d,\. ]+))?\]\s*(.*)$")
_TMARK = re.compile(r"^\x02T(\d+)\x02$")


def _cells(line: str) -> list[str]:
    parts = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [p.strip().replace("\\|", "|").replace("<br>", "\n") for p in parts]


def parse_body(text: str, sid: str, tables: _Tables, figures: dict[str, str]) -> list:
    blocks: list = []
    para: list[str] = []
    pending: Table | None = None
    lines = text.splitlines()
    i = 0

    def flush():
        if para:
            blocks.append(Para(" ".join(para), sid))
            para.clear()

    def new_table() -> Table:
        nonlocal pending
        t = pending or Table(sid)
        pending = None
        return t

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1
        if not line:
            flush()
            continue
        m = _CAP.match(line)
        if m:
            flush()
            kind, ref, widths, caption = m.groups()
            if kind == "Hình":
                blocks.append(Figure(sid, caption, ref or "", image=figures.get(ref or "", "")))
            else:
                pending = Table(sid, caption, ref or "")
                if widths:
                    pending.widths = [float(w) for w in widths.split(",") if w.strip()]
            continue
        m = _TMARK.match(line)
        if m:
            flush()
            t = new_table()
            t.header, t.rows = tables.items[int(m[1])]
            blocks.append(t)
            continue
        if line.startswith("|"):
            flush()
            t = new_table()
            grid = [line]
            while i < len(lines) and lines[i].strip().startswith("|"):
                grid.append(lines[i].strip())
                i += 1
            for k, g in enumerate(grid):
                if re.fullmatch(r"\|[\s\-:|]+\|?", g):
                    continue
                cells = _cells(g)
                if k == 0:
                    t.header = cells
                elif len(cells) == 1 and cells[0].startswith(">>"):
                    t.rows.append(("group", cells[0][2:].strip()))
                else:
                    t.rows.append(cells)
            blocks.append(t)
            continue
        if raw.startswith("- "):
            flush()
            blocks.append(Bullet(line[2:].strip(), sid, 1))
            continue
        if re.match(r"^\s{2,}[+\-] ", raw):
            flush()
            blocks.append(Bullet(line[2:].strip(), sid, 2))
            continue
        if line.startswith("### "):
            flush()
            blocks.append(Para(line[4:].strip(), sid, "minor"))
            continue
        if line.startswith("> "):
            flush()
            blocks.append(Para(line[2:].strip(), sid, "syntax"))
            continue
        para.append(line)
    flush()
    return blocks


# ------------------------------------------------------------------ ghép


def _when(expr: str, env: Environment, ctx: dict) -> bool:
    if not expr:
        return True
    return bool(env.compile_expression(expr)(**ctx))


_REF = re.compile(r"@\[([\w\-]+)\]")
_SEC = re.compile(r"@sec\[([\w\-]+)\]")


def compose(project: Project, doc: str) -> Doc:
    tpl = load_template(doc)
    ctx = context(project)
    env = _env()
    infos = {d.doc: d for d in ctx["docs"]}
    info = infos.get(doc)
    if info is None:
        meta = tpl.meta
        info = DocInfo(doc, "", "PL-??" if meta.get("kind") == "appendix" else "",
                       meta.get("title", doc), meta.get("short", ""), meta.get("summary", ""),
                       meta.get("kind", "appendix"))
    ctx["doc"] = info
    overrides = project.overrides.get(doc, {})
    figures = {"so-do-to-chuc": project.org.chart_image, "quy-trinh": project.coordination.process_image}

    issues: list[Issue] = []
    blocks: list = []
    sections: list[Section] = []
    counters = [0, 0, 0]
    skip_below: int | None = None

    for src in tpl.sections:
        ov = overrides.get(src.sid)
        sec = Section(src.sid, src.title, src.level, source=src.source, when=src.when)
        if skip_below is not None and src.level > skip_below:
            sec.enabled = False
            sections.append(sec)
            continue
        skip_below = None
        try:
            active = _when(src.when, env, ctx)
        except TemplateError as e:
            issues.append(Issue("error", src.sid, f"Điều kiện hiển thị lỗi: {e}"))
            active = True
        if not active:
            skip_below = src.level
            continue  # không thuộc giai đoạn/nội dung này: không liệt kê
        if ov and not ov.enabled:
            sec.enabled = False
            skip_below = src.level
            sections.append(sec)
            continue

        counters[src.level - 1] += 1
        for k in range(src.level, 3):
            counters[k] = 0
        sec.number = ".".join(str(c) for c in counters[: src.level])
        body_src = src.source
        if ov and ov.body is not None:
            body_src = ov.body
            sec.overridden = True
        tables = _Tables()
        local = {**ctx, "tbl": tables.tbl}
        try:
            title = env.from_string(src.title).render(**local)
            body = env.from_string(body_src).render(**local)
        except TemplateError as e:
            issues.append(Issue("error", f"{sec.number} {src.title}", f"Lỗi mẫu nội dung: {e}"))
            title, body = src.title, body_src
        sec.title = title
        sections.append(sec)
        blocks.append(Heading(src.level, sec.number, title, src.sid))
        blocks.extend(parse_body(body, src.sid, tables, figures))

    _number_and_link(blocks, sections, issues)
    return Doc(info, tpl.meta.get("orientation", "portrait"), blocks, sections, issues)


def _number_and_link(blocks: list, sections: list[Section], issues: list[Issue]) -> None:
    refs: dict[str, str] = {}
    nt = nf = 0
    for b in blocks:
        if isinstance(b, Table) and b.caption:
            nt += 1
            b.number = nt
            if b.ref:
                refs[b.ref] = f"Bảng {nt}"
        elif isinstance(b, Figure):
            nf += 1
            b.number = nf
            if b.ref:
                refs[b.ref] = f"Hình {nf}"
    secs = {s.sid: s.number for s in sections if s.enabled and s.number}
    where = {s.sid: f"{s.number} {s.title}" for s in sections}

    def fix(text: str, sid: str) -> str:
        def r(m):
            if m[1] in refs:
                return refs[m[1]]
            issues.append(Issue("error", where.get(sid, sid), f"Tham chiếu tới bảng/hình không tồn tại: {m[1]}"))
            return f"«?{m[1]}»"

        def s(m):
            if m[1] in secs:
                return f"mục {secs[m[1]]}"
            issues.append(Issue("error", where.get(sid, sid), f"Tham chiếu tới mục không tồn tại hoặc đã tắt: {m[1]}"))
            return f"«?{m[1]}»"

        return _REF.sub(r, _SEC.sub(s, text))

    for b in blocks:
        if isinstance(b, (Para, Bullet, Heading)):
            b.text = fix(b.text, b.sid)
        elif isinstance(b, Table):
            b.rows = [
                row if isinstance(row, tuple) else [fix(c, b.sid) for c in row] for row in b.rows
            ]


def block_texts(doc: Doc):
    """Duyệt mọi đoạn chữ trong tài liệu: (mã mục, chuỗi)."""
    for b in doc.blocks:
        if isinstance(b, (Para, Bullet, Heading)):
            yield b.sid, b.text
        elif isinstance(b, Figure):
            yield b.sid, b.caption
        elif isinstance(b, Table):
            yield b.sid, b.caption
            for row in b.rows:
                if isinstance(row, tuple):
                    yield b.sid, row[1]
                else:
                    for c in row:
                        yield b.sid, c
