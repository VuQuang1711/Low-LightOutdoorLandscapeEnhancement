@echo off
chcp 65001 >nul
title So sanh 4 Thuat Toan Xu Ly Anh Thieu Sang - Standalone Runner
color 0B
cd /d "%~dp0"

echo ===============================================================================
echo   DO AN XU LY ANH SO: NANG CAO CHAT LUONG ANH PHONG CANH THIEU SANG
echo   CHUONG TRINH SO SANH DONG THOI 4 THUAT TOAN (HE, CLAHE, GAMMA, MSR)
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
echo   Vui long cai dat Python (tu https://www.python.org/) va tich chon "Add Python to PATH".
echo ===============================================================================
echo.
pause
exit /b 1

:PYTHON_FOUND
echo   * Dang thuc thi bang lenh: %PY_CMD% all_algorithms.py %*
echo.

%PY_CMD% all_algorithms.py %*
if %errorlevel% neq 0 goto :ALGO_ERROR

echo.
echo ===============================================================================
echo   Da hoan tat xu ly va tinh toan cac chi so chat luong anh.
echo   Bieu do so sanh 6 o truc quan da duoc luu tai:
echo   %~dp0output_demo\so_sanh_4_thuat_toan.png
echo ===============================================================================
echo.
pause
exit /b 0

:ALGO_ERROR
color 0C
echo.
echo ===============================================================================
echo   [LOI] Chuong trinh gap su co trong qua trinh xu ly.
echo   Vui long kiem tra lai du lieu anh trong thu muc "data" hoac cai dat thu vien.
echo ===============================================================================
echo.
pause
exit /b 1
