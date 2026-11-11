"""Kết nối thư mục hồ sơ đầu vào: quét, lập chỉ mục toàn văn, tra cứu trích dẫn.

Chỉ đọc hồ sơ gốc. Chỉ mục lưu ở ``projects/<id>/.index/sources.db`` (SQLite FTS5).
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from pathlib import Path

TEXT_EXT = {".pdf", ".docx", ".xlsx", ".txt", ".md"}
MODEL_EXT = {".rvt", ".ifc", ".nwd", ".nwc", ".nwf", ".rfa"}
DRAWING_EXT = {".dwg", ".dxf"}

# bộ từ khóa gợi ý theo nhóm dữ liệu
KEYWORDS: dict[str, list[str]] = {
    "general": ["tên dự án", "địa điểm", "quy mô", "chủ đầu tư", "cấp công trình", "nhóm dự án"],
    "basis": ["Nghị định", "Quyết định", "TCVN", "ISO 19650", "hợp đồng", "tiêu chuẩn"],
    "schedule": ["tiến độ", "thời gian thực hiện", "ngày kể từ", "hoàn thành"],
    "bim": ["BIM", "mô hình thông tin", "4D", "5D", "va chạm", "hoàn công", "bóc tách khối lượng"],
    "org": ["nhân sự", "Quản lý BIM", "Điều phối BIM", "vai trò", "trách nhiệm"],
    "models": ["LOD", "mức độ chi tiết", "mức độ phát triển", "hạng mục", "hiện hữu", "mô hình"],
    "cde": ["CDE", "môi trường dữ liệu chung", "lưu trữ", "phân quyền"],
    "delivery": ["giao nộp", "bàn giao", "định dạng", "IFC", "báo cáo BIM"],
    "coordination": ["phần mềm", "Revit", "Navisworks", "hệ tọa độ", "VN-2000", "xung đột"],
    "naming": ["đặt tên", "mã hiệu", "quy ước", "Originator"],
    "doc": ["phiên bản", "phê duyệt", "chấp thuận"],
}


@dataclass
class Hit:
    file: str
    page: int
    snippet: str


@dataclass
class FileInfo:
    path: str
    kind: str  # text | model | drawing | other
    size: int
    pages: int = 0
    status: str = ""  # "", "không đọc được chữ", "lỗi: ..."


def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s)


# ------------------------------------------------------------------ trích chữ


def extract(path: Path) -> list[str]:
    """Danh sách trang (chuỗi). Word/Excel: mỗi ~3000 ký tự / mỗi sheet là một trang."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            import pdfplumber

            with pdfplumber.open(str(path)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
        except ImportError:
            from pypdf import PdfReader

            pages = [p.extract_text() or "" for p in PdfReader(str(path)).pages]
        return [norm(re.sub(r"\(cid:\d+\)", "", t)) for t in pages]
    if ext == ".docx":
        from docx import Document

        d = Document(str(path))
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                parts.append(" | ".join(c.text for c in row.cells))
        return _chunk(norm("\n".join(parts)))
    if ext == ".xlsx":
        from openpyxl import load_workbook

        wb = load_workbook(str(path), read_only=True, data_only=True)
        pages = []
        for ws in wb.worksheets:
            lines = []
            for row in ws.iter_rows(values_only=True):
                cells = [str(c) for c in row if c not in (None, "")]
                if cells:
                    lines.append(" | ".join(cells))
            pages.append(norm(f"[{ws.title}]\n" + "\n".join(lines)))
        return pages
    return _chunk(norm(path.read_text(encoding="utf-8", errors="ignore")))


def _chunk(text: str, size: int = 3000) -> list[str]:
    return [text[i : i + size] for i in range(0, max(len(text), 1), size)]


# ------------------------------------------------------------------ chỉ mục


class Index:
    def __init__(self, db: Path):
        db.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(db))
        self.con.executescript(
            """
            CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, root TEXT, kind TEXT, size INT,
                mtime REAL, pages INT, status TEXT);
            CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(path UNINDEXED, page UNINDEXED, body,
                tokenize='unicode61 remove_diacritics 0');
            """
        )

    def close(self):
        self.con.close()

    def scan(self, roots: list[str]) -> dict:
        """Quét các thư mục; chỉ trích lại tệp mới hoặc đã đổi. Trả về thống kê."""
        stats = {"new": 0, "unchanged": 0, "removed": 0, "missing_roots": []}
        seen = set()
        for root in roots:
            r = Path(root).expanduser()
            if not r.is_dir():
                stats["missing_roots"].append(root)
                continue
            for f in sorted(r.rglob("*")):
                if not f.is_file() or f.name.startswith(("~$", ".")):
                    continue
                key = str(f)
                seen.add(key)
                st = f.stat()
                row = self.con.execute("SELECT size, mtime FROM files WHERE path=?", (key,)).fetchone()
                if row and row[0] == st.st_size and abs(row[1] - st.st_mtime) < 1:
                    stats["unchanged"] += 1
                    continue
                self._index_file(f, str(r), st)
                stats["new"] += 1
        for (path,) in self.con.execute("SELECT path FROM files").fetchall():
            if path not in seen:
                self.con.execute("DELETE FROM files WHERE path=?", (path,))
                self.con.execute("DELETE FROM pages WHERE path=?", (path,))
                stats["removed"] += 1
        self.con.commit()
        return stats

    def _index_file(self, f: Path, root: str, st) -> None:
        ext = f.suffix.lower()
        kind = "text" if ext in TEXT_EXT else "model" if ext in MODEL_EXT else "drawing" if ext in DRAWING_EXT else "other"
        key = str(f)
        self.con.execute("DELETE FROM pages WHERE path=?", (key,))
        pages, status = 0, ""
        if kind == "text":
            try:
                texts = extract(f)
                pages = len(texts)
                for i, t in enumerate(texts, 1):
                    if t.strip():
                        self.con.execute("INSERT INTO pages VALUES (?,?,?)", (key, i, t))
                if sum(len(t.strip()) for t in texts) < 20 * max(pages, 1):
                    status = "không đọc được chữ (có thể là bản scan)"
            except Exception as e:  # tệp hỏng/khóa: ghi nhận, không dừng quét
                status = f"lỗi: {e}"[:200]
        self.con.execute(
            "INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?)",
            (key, root, kind, st.st_size, st.st_mtime, pages, status),
        )

    def files(self) -> list[FileInfo]:
        rows = self.con.execute("SELECT path, kind, size, pages, status FROM files ORDER BY path").fetchall()
        return [FileInfo(*r) for r in rows]

    def search(self, query: str, limit: int = 30) -> list[Hit]:
        q = _fts_query(query)
        if not q:
            return []
        try:
            rows = self.con.execute(
                "SELECT path, page, snippet(pages, 2, '[[', ']]', ' … ', 40) FROM pages WHERE pages MATCH ? "
                "ORDER BY rank LIMIT ?",
                (q, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [Hit(p, int(pg), " ".join(s.split())) for p, pg, s in rows]


def _fts_query(q: str) -> str:
    """Chuỗi người dùng -> truy vấn FTS5: cụm trong nháy giữ nguyên, các từ còn lại là AND."""
    q = norm(q).strip()
    phrases = re.findall(r'"([^"]+)"', q)
    rest = re.sub(r'"[^"]*"', " ", q)
    words = [w for w in re.findall(r"[\w\-\.]+", rest) if w]
    if not phrases and len(words) > 1:  # mặc định coi cả chuỗi là một cụm
        phrases, words = [" ".join(words)], []
    parts = ['"' + p.replace('"', "") + '"' for p in phrases] + ['"' + w + '"' for w in words]
    return " AND ".join(parts)


def index_for(project_dir: Path) -> Index:
    return Index(project_dir / ".index" / "sources.db")


def inventory(idx: Index) -> dict[str, list[FileInfo]]:
    """Danh sách mô hình, bản vẽ, văn bản đầu vào (theo tên tệp, không cần đọc nội dung)."""
    out: dict[str, list[FileInfo]] = {"model": [], "drawing": [], "text": [], "other": []}
    for f in idx.files():
        kind = f.kind
        if kind == "text" and Path(f.path).suffix.lower() == ".pdf" and re.search(r"ban[_ ]?ve|bản vẽ", f.path, re.I):
            kind = "drawing"
        out.setdefault(kind, []).append(f)
    return out
