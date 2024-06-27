@echo off
set root=%cd%
cd %root%
call .\sysexpetvenv\Scripts\Activate.bat
streamlit run .\Home.py 