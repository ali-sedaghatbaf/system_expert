@echo off
set root=%cd%
cd %root%
call .\expertvenv\Scripts\Activate.bat
streamlit run .\Home.py