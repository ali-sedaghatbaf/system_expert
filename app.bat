@echo off
set root=%cd%
cd %root%
call .\env\Scripts\Activate.bat
streamlit run .\Home.py 