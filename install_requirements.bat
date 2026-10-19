@echo off
chcp 65001 >nul
title Cai dat thu vien Python - Toan bo du an Image Processing
color 0A
cd /d "%~dp0"

echo ===============================================================================
echo   DO AN XU LY ANH SO: NANG CAO CHAT LUONG ANH NGOAI CANH THIEU SANG
echo   TU DONG KIEM TRA VA CAI DAT THU VIEN DU AN (CORE + ALGORITHM + WEB GUI)
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
echo   [LOI] Khong tim thay Python tren may tinh cua ban.
echo   Vui long cai dat Python (3.9 tro len) va tich chon "Add Python to PATH".
echo ===============================================================================
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [1/3] Da tim thay moi truong Python: %PY_CMD%
%PY_CMD% --version
echo.

echo [2/3] Kiem tra cac thu vien da duoc cai dat san...
%PY_CMD% -c "import cv2, numpy, skimage, scipy, matplotlib, fastapi, uvicorn, pydantic, yaml; print('OK')" >nul 2>&1
if %errorlevel% equ 0 goto :ALL_ALREADY_INSTALLED

:DO_INSTALL
echo.
echo [3/3] Dang tien hanh cai dat tu requirements.txt qua pip...
echo       - opencv-python, numpy, scikit-image, scipy, matplotlib (Thuat toan)
echo       - fastapi, uvicorn, pydantic, pyyaml (Web App va API Server)
echo.

%PY_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 goto :INSTALL_ERROR

echo.
echo ===============================================================================
echo   [THANH CONG] TAT CA CAC THU VIEN DA DUOC CAI DAT HOAN TAT.
echo.
echo   - De chay Web App truc quan:       Chay file "run_web.bat"
echo   - De chay so sanh 4 thuat toan:    Chay "py AlgorithmCode/all_algorithms.py"
echo   - De chay kiem thu tu dong:        Chay file "run_tests.bat"
echo ===============================================================================
goto :FINISH

:INSTALL_ERROR
color 0C
echo.
echo ===============================================================================
echo   [CANH BAO] Co loi xay ra trong qua trinh cai dat qua pip.
echo   Vui long kiem tra lai ket noi Internet hoac quyen Administrator.
echo ===============================================================================
goto :FINISH

:ALL_ALREADY_INSTALLED
echo.
echo ===============================================================================
echo   [THANH CONG] Tat ca thu vien can thiet da co san trong moi truong Python.
echo   Khong can phai tai lai tu Internet.
echo.
echo   * De chay Web Dashboard truc quan:  Chay file "run_web.bat"
echo   * De chay so sanh 4 thuat toan:     Chay "py AlgorithmCode/all_algorithms.py"
echo   * De chay kiem thu tu dong:         Chay file "run_tests.bat"
echo ===============================================================================
echo.
set "REINSTALL=N"
set /p "REINSTALL=Ban co muon cap nhat lai toan bo qua pip khong? (Y/N, mac dinh N): "
if /i "%REINSTALL%"=="Y" goto :DO_INSTALL

:FINISH
echo.
pause
