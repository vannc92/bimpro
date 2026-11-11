import re
from pathlib import Path

import pytest
from docx import Document

from bimpro import PLACEHOLDER, store
from bimpro.compose import Heading, Table, compose, doc_infos
from bimpro.models import ModelFile, MidpRow, RaciTask, Round
from bimpro.render_docx import render
from bimpro.validate import validate

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "projects" / "_mau_tkcs"


@pytest.fixture
def p():
    return store.load_path(TEMPLATE)


def headings(doc, level=1):
    return [b.text for b in doc.blocks if isinstance(b, Heading) and b.level == level]


def test_bep_outline_matches_reference(p):
    doc = compose(p, "bep")
    assert headings(doc) == [
        "GIỚI THIỆU CHUNG",
        "MỤC TIÊU VÀ NỘI DUNG ÁP DỤNG BIM CHO DỰ ÁN",
        "SƠ ĐỒ TỔ CHỨC, VAI TRÒ, TRÁCH NHIỆM VÀ NHÂN SỰ THAM GIA",
        "QUẢN LÝ DỮ LIỆU VÀ TRAO ĐỔI THÔNG TIN",
        "QUY TRÌNH PHỐI HỢP",
        "KIỂM SOÁT CHẤT LƯỢNG VÀ NGHIỆM THU MÔ HÌNH",
        "AN TOÀN THÔNG TIN",
    ]
    assert not doc.issues, doc.issues


def test_appendix_labels_follow_order(p):
    assert [d.label for d in doc_infos(p)] == ["", "PL-01", "PL-02", "PL-03", "PL-04"]
    p.doc.documents[1].enabled = False  # tắt RACI -> các phụ lục sau đánh số lại
    assert [d.label for d in doc_infos(p)] == ["", "PL-01", "PL-02", "PL-03"]
    bep = compose(p, "bep")
    texts = " ".join(b.text for b in bep.blocks if hasattr(b, "text"))
    assert "«?pl_raci»" in texts  # tham chiếu tới phụ lục đã tắt được làm lộ ra


def test_clash_section_only_when_enabled(p):
    assert "xung-dot" not in {s.sid for s in compose(p, "bep").sections}
    p.bim.features.clash = True
    p.coordination.clashes = []
    doc = compose(p, "bep")
    assert "Phát hiện và xử lý xung đột" in headings(doc, 2)
    assert not [i for i in doc.issues if i.level == "error"]


def test_section_override_and_disable(p):
    from bimpro.models import Override

    p.overrides = {"bep": {"nang-luc": Override(body="Nội dung riêng."), "sao-luu": Override(enabled=False)}}
    doc = compose(p, "bep")
    secs = {s.sid: s for s in doc.sections}
    assert secs["nang-luc"].overridden and not secs["sao-luu"].enabled
    assert "Sao lưu, phục hồi và lưu trữ" not in headings(doc, 2)


def test_empty_cells_show_placeholder(p):
    doc = compose(p, "bep")
    t = next(b for b in doc.blocks if isinstance(b, Table) and b.ref == "nhan-su")
    assert t.rows[0][1] == PLACEHOLDER


def test_validate_catches_errors(p):
    assert not [i for i in validate(p) if i.level == "error"]
    p.delivery.rounds = [Round(name="#1", date="15/11/2026"), Round(name="#2", date="30/10/2026")]
    p.delivery.midp.append(MidpRow(file="XXX_FS-PECC2-TB-M3-CV-0101"))
    p.org.raci.append(RaciTask(ref="Z1", task="Thử", values="A;A;R;I;I;I;I;I"))
    p.doc.issue_text = "Ấn bản 1 - Tháng 11/2026"
    msgs = " | ".join(i.message for i in validate(p) if i.level == "error")
    assert "sớm hơn" in msgs
    assert "không có trong danh mục mô hình" in msgs
    assert "đúng một vai trò A" in msgs
    assert "không chứa ký hiệu phiên bản" in msgs
    p.models.files.append(ModelFile(code="XXX_FS-PECC2-TB-M3-CV-0101"))
    assert "không có trong danh mục mô hình" not in " ".join(i.message for i in validate(p))


def test_render_docx(p, tmp_path):
    for info in doc_infos(p):
        doc = compose(p, info.doc)
        out = render(p, doc, tmp_path / f"{info.doc}.docx", TEMPLATE)
        d = Document(str(out))
        caps = [x.text for x in d.paragraphs if re.match(r"Bảng \d+\. ", x.text)]
        assert len(caps) == len([b for b in doc.blocks if isinstance(b, Table) and b.caption])
        heads = [x.text for x in d.paragraphs if x.style.name == "Heading 1"]
        assert heads == [f"{n}. {t}" for n, t in enumerate(headings(doc), 1)]
