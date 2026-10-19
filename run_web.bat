@echo off
chcp 65001 >nul
title Khoi dong Web Dashboard - Xu Ly Anh So
color 0B
cd /d "%~dp0"

echo ===============================================================================
echo   DO AN XU LY ANH SO: NANG CAO CHAT LUONG ANH NGOAI CANH THIEU SANG
echo   KHOI DONG HE THONG WEB DASHBOARD SO SANH 4 THUAT TOAN (HE, CLAHE, GAMMA, MSR)
echo ===============================================================================
echo.

set "PY_CMD="

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_CMD=%~dp0.venv\Scripts\python.exe"
    goto :PYTHON_FOUND
)
if exist "%~dp0..\.venv\Scripts\python.exe" (
    set "PY_CMD=%~dp0..\.venv\Scripts\python.exe"
    goto :PYTHON_FOUND
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :PYTHON_FOUND
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :PYTHON_FOUND
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python3"
    goto :PYTHON_FOUND
)

color 0C
echo ===============================================================================
echo   [LOI] Khong tim thay Python trong he thong PATH.
echo   Vui long cai dat Python (3.9 tro len) va tich chon "Add Python to PATH".
echo   Hoac thiet lap moi truong ao .venv trong thu muc du an.
echo ===============================================================================
echo.
pause
exit /b 1

:PYTHON_FOUND
echo   * Moi truong Python duoc chon: %PY_CMD%
%PY_CMD% --version
echo.
echo   * Dang khoi dong may chu Web Server tai: http://127.0.0.1:8501
echo   * Trinh duyet web se tu dong mo sau vai giay.
echo   * Nhan [Ctrl + C] trong cua so nay de dung may chu.
echo ===============================================================================
echo.

%PY_CMD% run_web.py %*
if %errorlevel% neq 0 goto :WEB_ERROR

echo.
echo   * May chu Web da dung hoat dong.
pause
exit /b 0

:WEB_ERROR
color 0C
echo.
echo ===============================================================================
echo   [CANH BAO] Qua trinh thuc thi run_web.py bi ngat hoac gap su co.
echo   Neu thieu thu vien, hay chay file "install_requirements.bat" truoc.
echo ===============================================================================
echo.
pause
exit /b 1
