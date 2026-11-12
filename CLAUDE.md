# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

bimpro is a local web app (Vietnamese UI and output) that composes BIM Execution Plans (BEP, "Kế hoạch thực hiện BIM") and their appendices as Word files, from a template library plus per-project data. No AI in the generation path. Design doc: `docs/specs/2026-11-11-bep-app-design.md`.

## Commands

```bash
pip install -e ".[dev]"          # install (Python 3.11+)
pytest                           # all tests
pytest tests/test_core.py::test_validate_catches_errors   # single test
bimpro build projects/dh3mr_bvtc            # write .docx files to projects/<id>/output/
bimpro build projects/dh3mr_bvtc --doc bep  # one document
bimpro check projects/dh3mr_bvtc            # consistency check; exit 1 on errors
bimpro serve                                # web UI at http://127.0.0.1:8765
```

`BIMPRO_PROJECTS` overrides the projects directory (default `./projects`); tests use it to work on a temp copy. To eyeball layout, convert output with `soffice --headless --convert-to pdf *.docx` (the container lacks Times New Roman, so Vietnamese glyphs may look italic in that preview only).

## Architecture

Single pipeline shared by preview and export:

`projects/<id>/project.yaml` → `store.load` → `models.Project` → `compose.compose(project, doc)` → `Doc` (block tree: Heading/Para/Bullet/Table/Figure) → `render_docx.render` (Word) or `render_html.render` (web preview).

- **Word formatting lives in `src/bimpro/library/base.docx`**, copied from the user's hand-edited BEP; `render_docx` opens it, clears the body and only picks styles from it (Heading 1–4 auto-numbered, `Body Text 1..4` by current heading level, `Body Text 21/22` bullets, `BANG`/`HINH VE` auto-numbered captions, `toc 1..3`). Do not type heading/caption numbers into text. Cover is its own section (no header/footer); the rest restarts page numbering at 1. To change fonts, spacing, margins or header/footer look, edit the styles in `base.docx` (open in Word) rather than the renderer. Header/footer text is rebuilt in code (`_header_footer`) from `general.owner_short/author_short/name_short/header_title` and `doc.issue_text`.

- **Templates** are `src/bimpro/library/documents/<doc>.md`: YAML front matter (`title`, `short`, `summary`, `kind: bep|appendix`, `orientation`) then sections `# sid | TITLE`, `## sid | Title {when: <jinja expr>}`. Section bodies are Jinja2 rendered with context from `compose.context()` (`p` project, `A` author role, `stage`, `f` = `p.bim.features`, `pl('pl_x')` → appendix label, `code('bep')` → document code, `tbl(headers, rows)`, `rows()`, `grows()`, `split()`). Body mini-markup (`- `, `  + `, `[Bảng#ref|widths] caption`, `[Hình#ref]`, `> syntax`, `### minor`, `@[ref]`, `@sec[sid]`) is documented at the top of `compose.py`.
- `@sec[...]` and `@[...]` resolve only within the same document; cross-document references must be plain text or `pl()`/`code()`.
- `{when: ...}` hides a section (and its children) per stage/features; disabled-by-override sections still show in the section tree. Numbering and Bảng/Hình counters are assigned after filtering.
- Appendix numbers (PL-01…) come from the order of enabled entries in `p.doc.documents`; never hard-code them in templates.
- Empty values render as `«…»` (`PLACEHOLDER`). In `rows()/grows()` a column name ending in `?` may stay blank.
- `stages.yaml` holds per-stage wording (`phrase`, `short`, `next`, `design_docs`); stage-specific behavior otherwise comes from `p.bim.features` flags (clash, sim4d, qto, existing, asbuilt, supervisor, drawings).
- **Per-project overrides**: `p.overrides[doc][sid]` replaces a section body (same mini-markup + Jinja) or disables it; edited via the web UI.
- **Data model** (`models.py`): each `Group` subclass is one web form page, registered in `GROUPS`. The web form is generated from field types (`str`, `bool`, `list[str]`, `list[Model]` grid, nested model of bools); field `title` is the Vietnamese label, `long=True` gives a textarea. Adding a field to a group automatically adds it to the UI. Multi-column values inside one string use `;` (RACI values, permission rows, MIDP dates).
- `validate.py` cross-checks project data and the composed documents (appendix codes, revision vs footer text, round/MIDP/TIDP date order, models in MIDP/TIDP vs model list, naming regex, exactly one A per RACI row, permission column counts, unresolved references, remaining `«…»`).
- `sources.py` indexes the user's input folders (PDF via pdfplumber, docx, xlsx) into SQLite FTS5 at `projects/<id>/.index/sources.db`; read-only on source files. The web search panel copies snippets into the focused field and stores the citation in `p.citations`.
- `web/app.py` is FastAPI + Jinja2 templates + vanilla JS (`static/app.js`); no build step.

## Projects

- `projects/_mau_tkcs`: template project for the basic-design stage (TKCS); used as the clone source and by tests.
- `projects/dh3mr_bvtc`: real project, construction-drawing stage (BVTC), 7 appendices. Its YAML was generated with Python + `store.save`; when editing YAML by hand, quote flow-mapping values that contain commas, and avoid the bare key `no` (YAML reads it as `false`).

Generated `output/` and `.index/` folders are git-ignored.
