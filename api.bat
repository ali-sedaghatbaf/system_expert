@echo off
set root=%cd%
cd %root%
if not exist env\ (
    python -m venv .\env
    call .\env\Scripts\Activate.bat && pip install -r .\requirements.txt && uvicorn api:app --reload
) else (
    call .\env\Scripts\Activate.bat && uvicorn api:app --reload
)vite

