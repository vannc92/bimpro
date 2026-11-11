import shutil
from pathlib import Path

import pytest
from docx import Document
from fastapi.testclient import TestClient

from bimpro.sources import Index, inventory

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs(tmp_path):
    d = tmp_path / "input"
    (d / "YCKT").mkdir(parents=True)
    (d / "model").mkdir()
    doc = Document()
    doc.add_paragraph("3.3.4. Mức độ phát triển mô hình thông tin công trình (LOD) cho dự án ở mức 350.")
    doc.add_paragraph("Phần mềm Revit, Phiên bản: 2024.")
    doc.save(d / "YCKT" / "chuong_v.docx")
    (d / "model" / "DH3MR.KT-PECC3-BEP-ZZ-ZZ-0001.rvt").write_bytes(b"x")
    return d


def test_index_search_and_rescan(tmp_path, inputs):
    idx = Index(tmp_path / "db" / "s.db")
    st = idx.scan([str(inputs), str(tmp_path / "khong_co")])
    assert st["new"] == 2 and st["missing_roots"]
    hits = idx.search("LOD")
    assert hits and "350" in hits[0].snippet and hits[0].page == 1
    assert idx.search("mức độ phát triển")  # cụm có dấu
    assert idx.scan([str(inputs)])["unchanged"] == 2  # quét lại không trích lại
    inv = inventory(idx)
    assert [Path(f.path).name for f in inv["model"]] == ["DH3MR.KT-PECC3-BEP-ZZ-ZZ-0001.rvt"]
    idx.close()


def test_web_flow(tmp_path, inputs, monkeypatch):
    shutil.copytree(ROOT / "projects" / "_mau_tkcs", tmp_path / "projects" / "_mau_tkcs")
    monkeypatch.setenv("BIMPRO_PROJECTS", str(tmp_path / "projects"))
    from bimpro.web.app import app

    c = TestClient(app)
    assert c.get("/").status_code == 200
    r = c.post("/new", data={"src": "_mau_tkcs", "new_id": "t1", "title": "Thử"}, follow_redirects=False)
    assert r.status_code == 303
    for g in ("general", "org", "models", "cde", "naming", "doc", "sources"):
        assert c.get(f"/p/t1/g/{g}").status_code == 200
    # lưu nhóm dữ liệu dạng lưới: dòng trống bị bỏ, thứ tự giữ nguyên
    r = c.post("/p/t1/g/schedule", data={
        "g.milestones.0.task": "Lập TKBVTC", "g.milestones.0.time": "10/2026",
        "g.milestones.1.task": "", "g.milestones.1.time": "",
        "g.milestones.2.task": "Thi công", "g.milestones.2.time": "11/2026",
    })
    assert r.status_code == 200
    from bimpro import store
    assert [m.task for m in store.load("t1").schedule.milestones] == ["Lập TKBVTC", "Thi công"]
    c.post("/p/t1/g/sources", data={"l.folders": str(inputs)})
    c.post("/p/t1/sources/scan")
    hits = c.get("/p/t1/search", params={"q": "LOD"}).json()
    assert hits and hits[0]["name"] == "chuong_v.docx"
    assert c.get("/p/t1/doc/bep").status_code == 200
    assert c.get("/p/t1/check").status_code == 200
    c.post("/p/t1/export")
    assert len(list((tmp_path / "projects" / "t1" / "output").glob("*.docx"))) == 5
