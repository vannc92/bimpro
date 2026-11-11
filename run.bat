@echo off
rem Chay giao dien bimpro tai http://127.0.0.1:8765
cd /d "%~dp0"
if not exist .venv (
  py -3 -m venv .venv
  .venv\Scripts\python -m pip install -e .
)
start "" http://127.0.0.1:8765
.venv\Scripts\python -m bimpro.cli serve
