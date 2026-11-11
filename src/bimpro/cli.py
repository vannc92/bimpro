"""Dòng lệnh: ``bimpro build <thư mục dự án>`` và ``bimpro serve``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import store
from .compose import compose, doc_infos
from .render_docx import output_name, render
from .validate import validate


def build(path: Path, only: str | None = None) -> list[Path]:
    project = store.load_path(path)
    base = Path(path) if Path(path).is_dir() else Path(path).parent
    out = []
    for info in doc_infos(project):
        if only and info.doc != only:
            continue
        doc = compose(project, info.doc)
        out.append(render(project, doc, base / "output" / output_name(project, doc), base))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bimpro")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Xuất BEP và phụ lục ra .docx")
    b.add_argument("project", type=Path)
    b.add_argument("--doc", help="Chỉ xuất một tài liệu (ví dụ bep, pl_raci)")
    c = sub.add_parser("check", help="Kiểm tra nhất quán")
    c.add_argument("project", type=Path)
    s = sub.add_parser("serve", help="Chạy giao diện web")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args(argv)

    if a.cmd == "build":
        for p in build(a.project, a.doc):
            print(p)
    elif a.cmd == "check":
        issues = validate(store.load_path(a.project))
        for i in issues:
            print(f"[{i.level}] {i.where}: {i.message}")
        sys.exit(1 if any(i.level == "error" for i in issues) else 0)
    elif a.cmd == "serve":
        import uvicorn

        uvicorn.run("bimpro.web.app:app", host=a.host, port=a.port)


if __name__ == "__main__":
    main()
