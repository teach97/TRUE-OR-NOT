@echo off
cd /d %~dp0
start "TRUE-OR-NOT backend" cmd /k "cd backend && .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8010"
start "TRUE-OR-NOT frontend" cmd /k "npm run dev"
echo Servers starting...
timeout /t 8 >nul
start http://127.0.0.1:3000
