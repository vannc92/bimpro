"""Giao diện web chạy cục bộ."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import typing
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .. import store
from ..compose import compose, doc_infos, library_docs, load_template, stages
from ..models import GROUPS, Override
from ..render_docx import output_name, render
from ..render_html import render as render_html
from ..sources import KEYWORDS, index_for, inventory
from ..validate import validate

HERE = Path(__file__).parent
app = FastAPI(title="bimpro – Biên soạn BEP")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
tpl = Jinja2Templates(directory=HERE / "templates")
tpl.env.globals["GROUPS"] = GROUPS


# ------------------------------------------------------------------ mô tả form


def _kind(ann) -> tuple[str, type | None]:
    origin = typing.get_origin(ann)
    if origin is list:
        (arg,) = typing.get_args(ann)
        if arg is str:
            return "lines", None
        return "grid", arg
    if isinstance(ann, type) and issubclass(ann, BaseModel):
        return "nested", ann
    if ann is bool:
        return "bool", None
    return "text", None


def describe(cls: type[BaseModel]) -> list[dict]:
    out = []
    for name, f in cls.model_fields.items():
        kind, sub = _kind(f.annotation)
        extra = f.json_schema_extra or {}
        item = {"name": name, "title": f.title or name, "kind": kind, "long": bool(extra.get("long"))}
        if sub is not None:
            item["cols"] = describe(sub)
        out.append(item)
    return out


def parse_form(cls: type[BaseModel], form) -> dict:
    data: dict = {}
    for item in describe(cls):
        n, k = item["name"], item["kind"]
        if k == "text":
            data[n] = form.get(f"f.{n}", "")
        elif k == "bool":
            data[n] = form.get(f"f.{n}") == "1"
        elif k == "lines":
            data[n] = [x.strip() for x in form.get(f"l.{n}", "").splitlines() if x.strip()]
        elif k == "nested":
            data[n] = {c["name"]: form.get(f"n.{n}.{c['name']}") == "1" for c in item["cols"]}
        elif k == "grid":
            rows: dict[int, dict] = {}
            pat = re.compile(rf"^g\.{n}\.(\d+)\.(\w+)$")
            for key in form.keys():
                m = pat.match(key)
                if m:
                    rows.setdefault(int(m[1]), {})[m[2]] = form.get(key)
            out = []
            for i in sorted(rows):
                r = rows[i]
                row = {}
                for c in item["cols"]:
                    if c["kind"] == "bool":
                        row[c["name"]] = r.get(c["name"]) == "1"
                    else:
                        row[c["name"]] = (r.get(c["name"]) or "").strip()
                if any(v for v in row.values() if not isinstance(v, bool)):
                    out.append(row)
            data[n] = out
    return data


# ------------------------------------------------------------------ tiện ích


def _load(pid: str):
    try:
        return store.load(pid)
    except (FileNotFoundError, ValueError):
        raise HTTPException(404, "Không tìm thấy dự án")


def _ctx(request, project=None, **kw):
    return {"request": request, "p": project, "stages": stages(), **kw}


# ------------------------------------------------------------------ trang


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    projects = store.list_projects()
    return tpl.TemplateResponse(request, "index.html", _ctx(request, projects=projects))


@app.post("/new")
def new_project(src: str = Form(...), new_id: str = Form(...), title: str = Form("")):
    try:
        p = store.clone(src, new_id.strip(), title.strip())
    except ValueError as e:
        raise HTTPException(400, str(e))
    return RedirectResponse(f"/p/{p.id}", 303)


@app.get("/p/{pid}", response_class=HTMLResponse)
def project_home(request: Request, pid: str):
    p = _load(pid)
    issues = validate(p)
    return tpl.TemplateResponse(
        request, "project.html", _ctx(request, p, docs=doc_infos(p), issues=issues, all_docs=library_docs())
    )


@app.post("/p/{pid}/meta")
async def save_meta(request: Request, pid: str):
    p = _load(pid)
    form = await request.form()
    p.title = form.get("title", p.title)
    if form.get("stage") in stages():
        p.stage = form.get("stage")
    store.save(p)
    return RedirectResponse(f"/p/{pid}", 303)


@app.get("/p/{pid}/g/{group}", response_class=HTMLResponse)
def group_form(request: Request, pid: str, group: str):
    p = _load(pid)
    if group not in GROUPS:
        raise HTTPException(404)
    label, cls = GROUPS[group]
    return tpl.TemplateResponse(
        request,
        "group.html",
        _ctx(request, p, group=group, label=label, fields=describe(cls), data=getattr(p, group),
             keywords=KEYWORDS.get(group, []), cites=p.citations, saved=request.query_params.get("saved")),
    )


@app.post("/p/{pid}/g/{group}")
async def group_save(request: Request, pid: str, group: str):
    p = _load(pid)
    if group not in GROUPS:
        raise HTTPException(404)
    _, cls = GROUPS[group]
    form = await request.form()
    setattr(p, group, cls.model_validate(parse_form(cls, form)))
    for key in form.keys():
        if key.startswith("cite.") and form.get(key):
            p.citations[f"{group}.{key[5:]}"] = form.get(key)
    store.save(p)
    return RedirectResponse(f"/p/{pid}/g/{group}?saved=1", 303)


@app.post("/p/{pid}/image")
async def upload_image(pid: str, field: str = Form(...), file: UploadFile = Form(...)):
    p = _load(pid)
    if field not in {"org.chart_image", "coordination.process_image"}:
        raise HTTPException(400)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg"}:
        raise HTTPException(400, "Chỉ nhận ảnh PNG/JPG")
    name = field.split(".")[1] + ext
    (store.project_dir(pid) / name).write_bytes(await file.read())
    group, attr = field.split(".")
    setattr(getattr(p, group), attr, name)
    store.save(p)
    return RedirectResponse(f"/p/{pid}/g/{group}?saved=1", 303)


# -------------------------------------------------- tài liệu: xem trước, sửa mục


@app.get("/p/{pid}/doc/{doc}", response_class=HTMLResponse)
def doc_view(request: Request, pid: str, doc: str):
    p = _load(pid)
    if doc not in library_docs():
        raise HTTPException(404)
    d = compose(p, doc)
    return tpl.TemplateResponse(
        request, "doc.html", _ctx(request, p, d=d, html=render_html(d), docs=doc_infos(p), doc=doc)
    )


@app.get("/p/{pid}/doc/{doc}/sec/{sid}", response_class=HTMLResponse)
def sec_edit(request: Request, pid: str, doc: str, sid: str):
    p = _load(pid)
    sec = next((s for s in load_template(doc).sections if s.sid == sid), None)
    if sec is None:
        raise HTTPException(404)
    ov = p.overrides.get(doc, {}).get(sid)
    return tpl.TemplateResponse(request, "section.html", _ctx(request, p, doc=doc, sec=sec, ov=ov))


@app.post("/p/{pid}/doc/{doc}/sec/{sid}")
async def sec_save(request: Request, pid: str, doc: str, sid: str):
    p = _load(pid)
    sec = next((s for s in load_template(doc).sections if s.sid == sid), None)
    if sec is None:
        raise HTTPException(404)
    form = await request.form()
    action = form.get("action")
    ovs = p.overrides.setdefault(doc, {})
    if action == "reset":
        ovs.pop(sid, None)
    else:
        body = form.get("body", "").replace("\r\n", "\n")
        enabled = form.get("enabled") == "1"
        ov = Override(enabled=enabled, body=None if body.strip() == sec.source.strip() else body)
        if ov.enabled and ov.body is None:
            ovs.pop(sid, None)
        else:
            ovs[sid] = ov
    if not ovs:
        p.overrides.pop(doc, None)
    store.save(p)
    return RedirectResponse(f"/p/{pid}/doc/{doc}#s-{sid}", 303)


# -------------------------------------------------- kiểm tra, xuất


@app.get("/p/{pid}/check", response_class=HTMLResponse)
def check(request: Request, pid: str):
    p = _load(pid)
    return tpl.TemplateResponse(request, "check.html", _ctx(request, p, issues=validate(p)))


@app.post("/p/{pid}/export")
def export(pid: str, doc: str = Form("")):
    p = _load(pid)
    base = store.project_dir(pid)
    for info in doc_infos(p):
        if doc and info.doc != doc:
            continue
        d = compose(p, info.doc)
        render(p, d, base / "output" / output_name(p, d), base)
    return RedirectResponse(f"/p/{pid}/files", 303)


@app.get("/p/{pid}/files", response_class=HTMLResponse)
def files(request: Request, pid: str):
    p = _load(pid)
    out = store.project_dir(pid) / "output"
    items = sorted(out.glob("*.docx"), key=lambda f: f.name) if out.exists() else []
    return tpl.TemplateResponse(request, "files.html", _ctx(request, p, items=items))


@app.get("/p/{pid}/files/{name}")
def download(pid: str, name: str):
    path = (store.project_dir(pid) / "output" / name).resolve()
    if path.parent != (store.project_dir(pid) / "output").resolve() or not path.exists():
        raise HTTPException(404)
    return FileResponse(path, filename=name)


# -------------------------------------------------- hồ sơ đầu vào


@app.get("/p/{pid}/sources", response_class=HTMLResponse)
def sources_page(request: Request, pid: str):
    p = _load(pid)
    idx = index_for(store.project_dir(pid))
    try:
        inv = inventory(idx)
    finally:
        idx.close()
    return tpl.TemplateResponse(
        request, "sources.html", _ctx(request, p, inv=inv, stats=request.query_params.get("stats"))
    )


@app.post("/p/{pid}/sources/scan")
def sources_scan(pid: str):
    p = _load(pid)
    idx = index_for(store.project_dir(pid))
    try:
        st = idx.scan(p.sources.folders)
    finally:
        idx.close()
    msg = f"Mới/cập nhật {st['new']}, không đổi {st['unchanged']}, đã xóa {st['removed']}"
    if st["missing_roots"]:
        msg += " · Không tìm thấy: " + "; ".join(st["missing_roots"])
    return RedirectResponse(f"/p/{pid}/sources?stats={msg}", 303)


@app.get("/p/{pid}/search")
def search(pid: str, q: str = ""):
    _load(pid)
    idx = index_for(store.project_dir(pid))
    try:
        hits = idx.search(q)
    finally:
        idx.close()
    return JSONResponse([{"file": h.file, "name": Path(h.file).name, "page": h.page, "snippet": h.snippet} for h in hits])


@app.post("/p/{pid}/open")
def open_file(pid: str, path: str = Form(...)):
    """Mở tệp gốc bằng chương trình mặc định (chỉ tệp đã có trong chỉ mục)."""
    _load(pid)
    idx = index_for(store.project_dir(pid))
    try:
        known = {f.path for f in idx.files()}
    finally:
        idx.close()
    if path not in known:
        raise HTTPException(404)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])
    return JSONResponse({"ok": True})
