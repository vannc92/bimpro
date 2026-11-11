"""Đọc/ghi dự án: mỗi dự án là một thư mục chứa ``project.yaml``."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import yaml

from .models import Project


def projects_dir() -> Path:
    return Path(os.environ.get("BIMPRO_PROJECTS", "projects")).resolve()


def project_dir(pid: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", pid):
        raise ValueError(f"Mã dự án không hợp lệ: {pid!r}")
    return projects_dir() / pid


class _Dumper(yaml.SafeDumper):
    pass


def _str(dumper, data):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_Dumper.add_representer(str, _str)


def load_path(path: Path) -> Project:
    path = Path(path)
    if path.is_dir():
        path = path / "project.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    project = Project.model_validate(data)
    project.id = path.parent.name
    return project


def load(pid: str) -> Project:
    return load_path(project_dir(pid))


def save(project: Project) -> Path:
    d = project_dir(project.id)
    d.mkdir(parents=True, exist_ok=True)
    data = project.model_dump(exclude={"id"})
    text = yaml.dump(data, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=110)
    path = d / "project.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def list_projects() -> list[Project]:
    out = []
    root = projects_dir()
    if root.exists():
        for d in sorted(root.iterdir()):
            if (d / "project.yaml").exists():
                out.append(load_path(d))
    return out


def clone(src: str, new_id: str, title: str = "") -> Project:
    dst = project_dir(new_id)
    if dst.exists():
        raise ValueError(f"Dự án {new_id!r} đã tồn tại")
    project = load(src)
    project.id = new_id
    project.is_template = False
    project.title = title or new_id
    project.citations = {}
    save(project)
    # chép ảnh (sơ đồ tổ chức, lưu đồ) nếu có
    for f in project_dir(src).iterdir():
        if f.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            shutil.copy2(f, dst / f.name)
    return project
