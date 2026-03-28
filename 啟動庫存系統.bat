@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在啟動庫存系統...
start "" streamlit run app.py
timeout /t 5 /nobreak >nul
start http://localhost:8501
echo 已開啟瀏覽器，請稍候載入。
timeout /t 2 /nobreak >nul
exit
