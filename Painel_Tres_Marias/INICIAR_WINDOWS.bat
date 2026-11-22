@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto instalar
if exist "C:\Program Files\Python314\python.exe" (
  "C:\Program Files\Python314\python.exe" -m venv .venv
) else (
  py -3 -m venv .venv
)
if errorlevel 1 goto erro
:instalar
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro
".venv\Scripts\python.exe" -m streamlit run app_publica.py
if errorlevel 1 goto erro
exit /b 0
:erro
echo.
echo Nao foi possivel iniciar. Copie a mensagem de erro exibida acima.
pause
exit /b 1
