@echo off
chcp 65001 >nul
title Kiem thu tu dong - Unit Tests du an Xu Ly Anh So
color 0E
cd /d "%~dp0"

echo ===============================================================================
echo   DO AN XU LY ANH SO: NANG CAO CHAT LUONG ANH NGOAI CANH THIEU SANG
echo   CHUONG TRINH CHAY KIEM THU TU DONG (UNIT TESTS VA HE THONG)
echo ===============================================================================
echo.

set "PY_CMD="

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_CMD=%~dp0.venv\Scripts\python.exe"
    goto :RUN_TESTS
)
if exist "%~dp0..\.venv\Scripts\python.exe" (
    set "PY_CMD=%~dp0..\.venv\Scripts\python.exe"
    goto :RUN_TESTS
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :RUN_TESTS
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :RUN_TESTS
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python3"
    goto :RUN_TESTS
)

color 0C
echo [LOI] Khong tim thay Python trong he thong PATH.
pause
exit /b 1

:RUN_TESTS
echo   * Dang thuc thi kiem thu bang: %PY_CMD% -m unittest discover test -v
echo.

%PY_CMD% -m unittest discover test -v
if %errorlevel% neq 0 goto :TESTS_FAILED

color 0A
echo.
echo ===============================================================================
echo   [THANH CONG] TOAN BO CAC BAI KIEM THU DA VUOT QUA (ALL TESTS PASSED).
echo   He thong san sang cho bao cao va thuyet trinh truoc Hoi dong.
echo ===============================================================================
echo.
pause
exit /b 0

:TESTS_FAILED
color 0C
echo.
echo ===============================================================================
echo   [CANH BAO] Co bai kiem thu that bai. Vui long kiem tra lai log chi tiet o tren.
echo ===============================================================================
echo.
pause
exit /b 1
