"""Kiểm tra nhất quán giữa dữ liệu dự án, BEP và các phụ lục."""

from __future__ import annotations

import re
from datetime import date

from . import PLACEHOLDER
from .compose import Issue, block_texts, compose, doc_infos
from .models import Project

_DATE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")


def parse_date(s: str) -> date | None:
    m = _DATE.match(s or "")
    if not m:
        return None
    try:
        return date(int(m[3]), int(m[2]), int(m[1]))
    except ValueError:
        return None


def check_dates(p: Project) -> list[Issue]:
    out = []
    rounds = [(r.name, parse_date(r.date)) for r in p.delivery.rounds]
    known = [(n, d) for n, d in rounds if d]
    for (n1, d1), (n2, d2) in zip(known, known[1:]):
        if d2 < d1:
            out.append(Issue("error", "Chuyển giao thông tin", f"Ngày đợt '{n2}' ({d2:%d/%m/%Y}) sớm hơn đợt '{n1}' ({d1:%d/%m/%Y})"))
    for row in p.delivery.midp:
        ds = [parse_date(x) for x in row.dates.split(";")] if row.dates else []
        good = [d for d in ds if d]
        if any(b < a for a, b in zip(good, good[1:])):
            out.append(Issue("error", "MIDP", f"Ngày chuyển giao của '{row.file}' không tăng dần: {row.dates}"))
    for row in p.delivery.tidp:
        s, f = parse_date(row.start), parse_date(row.finish)
        if s and f and f < s:
            out.append(Issue("error", "TIDP", f"'{row.task}': ngày hoàn thành trước ngày bắt đầu"))
    return out


def _model_codes(p: Project) -> set[str]:
    return {f.code.strip() for f in p.models.files if f.code.strip()}


def check_models(p: Project) -> list[Issue]:
    out = []
    codes = _model_codes(p)
    for row in p.delivery.midp:
        f = row.file.strip()
        if re.search(r"-(M3|FM|CM)-", f) and f not in codes:
            out.append(Issue("error", "MIDP", f"Mô hình '{f}' không có trong danh mục mô hình và mã hiệu"))
    for row in p.delivery.tidp:
        for f in re.split(r"[,;\s]+", row.product):
            if re.search(r"-(M3|FM|CM)-", f) and f not in codes:
                out.append(Issue("error", "TIDP", f"Mô hình '{f}' không có trong danh mục mô hình và mã hiệu"))
    return out


def check_naming(p: Project) -> list[Issue]:
    out = []
    rx = p.naming.regex.strip()
    if not rx:
        return out
    try:
        pat = re.compile(rx)
    except re.error as e:
        return [Issue("error", "Quy ước đặt tên", f"Biểu thức kiểm tra tên không hợp lệ: {e}")]
    names = [(f"Mã hiệu mô hình", f.code) for f in p.models.files]
    names += [("Mã hiệu tài liệu", d.code) for d in p.doc.documents if d.enabled]
    names += [("MIDP", m.file) for m in p.delivery.midp]
    for where, n in names:
        n = n.strip()
        if n and PLACEHOLDER not in n and not pat.match(n):
            out.append(Issue("warn", where, f"'{n}' không khớp cú pháp đặt tên của dự án"))
    return out


def check_revision(p: Project) -> list[Issue]:
    out = []
    rev = p.doc.revision.strip()
    if p.doc.revisions and p.doc.revisions[-1].rev.strip() != rev:
        out.append(Issue("error", "Kiểm soát tài liệu", f"Phiên bản hiện hành '{rev}' khác dòng cuối của bảng kiểm soát phiên bản ('{p.doc.revisions[-1].rev}')"))
    txt = p.doc.issue_text
    if rev and txt and not re.search(rf"(?<![A-Za-z0-9]){re.escape(rev)}(?![A-Za-z0-9])", txt):
        out.append(Issue("error", "Kiểm soát tài liệu", f"Dòng phiên bản ở cuối trang '{txt}' không chứa ký hiệu phiên bản '{rev}'"))
    return out


def check_raci(p: Project) -> list[Issue]:
    out = []
    n = len(p.org.raci_roles)
    for t in p.org.raci:
        vals = [v.strip() for v in t.values.split(";")]
        if len(vals) != n:
            out.append(Issue("error", "Ma trận RACI", f"{t.ref}: có {len(vals)} giá trị, cần {n} (theo số vai trò)"))
        a = sum(1 for v in vals if "A" in v.replace(" ", "").split(","))
        if a != 1:
            out.append(Issue("error", "Ma trận RACI", f"{t.ref} {t.task}: cần đúng một vai trò A, hiện có {a}"))
    return out


def check_cde(p: Project) -> list[Issue]:
    n = len([r for r in p.cde.perm_roles.split(";") if r.strip()])
    return [
        Issue("error", "Ma trận phân quyền", f"{r.folder}: có {len(r.values.split(';'))} giá trị, cần {n}")
        for r in p.cde.perms
        if len(r.values.split(";")) != n
    ]


def check_docs(p: Project) -> list[Issue]:
    out = []
    infos = doc_infos(p)
    if not any(i.kind == "bep" for i in infos):
        out.append(Issue("error", "Kiểm soát tài liệu", "Danh mục tài liệu phát hành không có BEP"))
    seen = {}
    for i in infos:
        if i.code and i.code in seen:
            out.append(Issue("error", "Kiểm soát tài liệu", f"Mã hiệu '{i.code}' dùng cho cả {seen[i.code]} và {i.doc}"))
        seen[i.code] = i.doc
    return out


def check_placeholders(p: Project) -> list[Issue]:
    out = []
    for info in doc_infos(p):
        doc = compose(p, info.doc)
        out.extend(doc.issues)
        where = {s.sid: f"{s.number} {s.title}" for s in doc.sections}
        counts: dict[str, int] = {}
        for sid, text in block_texts(doc):
            if PLACEHOLDER in text or "«" in text:
                counts[sid] = counts.get(sid, 0) + 1
        for sid, c in counts.items():
            out.append(Issue("info", f"{info.label or 'BEP'} – mục {where.get(sid, sid)}", f"còn {c} chỗ chưa điền («…»)"))
    return out


def validate(p: Project) -> list[Issue]:
    out: list[Issue] = []
    for fn in (check_docs, check_revision, check_dates, check_models, check_naming, check_raci, check_cde, check_placeholders):
        out.extend(fn(p))
    order = {"error": 0, "warn": 1, "info": 2}
    return sorted(out, key=lambda i: order[i.level])
