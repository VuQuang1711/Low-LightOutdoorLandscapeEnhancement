@echo off
chcp 65001 >nul
title Cai dat thu vien Python - AlgorithmCode (Xu Ly Anh So)
color 0A
cd /d "%~dp0"

echo ===============================================================================
echo   DO AN XU LY ANH SO: NANG CAO CHAT LUONG ANH THIEU SANG
echo   TU DONG KIEM TRA VA CAI DAT CAC THU VIEN PYTHON CAN THIET (ALGORITHM CODE)
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
echo   Vui long cai dat Python (phien ban 3.9 tro len) va tich chon "Add Python to PATH".
echo ===============================================================================
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [1/3] Da tim thay moi truong Python: %PY_CMD%
%PY_CMD% --version
echo.

echo [2/3] Kiem tra cac thu vien thuat toan da co san...
%PY_CMD% -c "import cv2, numpy, skimage, scipy, matplotlib; print('OK')" >nul 2>&1
if %errorlevel% equ 0 goto :ALGO_ALREADY_INSTALLED

:DO_ALGO_INSTALL
echo.
echo [3/3] Dang tien hanh cai dat tu requirements.txt...
echo       - opencv-python (Xu ly anh so va loc Bilateral)
echo       - numpy (Tinh toan ma tran va LUT)
echo       - scikit-image (Do chi so hoc thuat SSIM)
echo       - scipy (Khoa hoc tinh toan)
echo       - matplotlib (Ve bieu do va xuat anh so sanh truc quan)
echo.

%PY_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 goto :INSTALL_ERROR

echo.
echo ===============================================================================
echo   [THANH CONG] TAT CA CAC THU VIEN DA DUOC CAI DAT HOAN TAT.
echo   Ban co the chay thu ngay bang lenh:
echo     run_all.bat   hoac   %PY_CMD% all_algorithms.py
echo ===============================================================================
goto :FINISH_ALGO

:INSTALL_ERROR
color 0C
echo.
echo ===============================================================================
echo   [CANH BAO] Co loi xay ra trong qua trinh cai dat qua pip.
echo   Vui long kiem tra lai ket noi Internet hoac quyen Administrator.
echo ===============================================================================
goto :FINISH_ALGO

:ALGO_ALREADY_INSTALLED
echo.
echo ===============================================================================
echo   [THANH CONG] Tat ca thu vien thuat toan da co san trong moi truong Python.
echo   Khong can phai tai lai tu Internet.
echo.
echo   Ban co the chay thu nghiem ngay bang lenh:
echo     run_all.bat   hoac   %PY_CMD% all_algorithms.py
echo ===============================================================================
echo.
set "REINSTALL=N"
set /p "REINSTALL=Ban co muon tai lai qua pip khong? (Y/N, mac dinh N): "
if /i "%REINSTALL%"=="Y" goto :DO_ALGO_INSTALL

:FINISH_ALGO
echo.
pause
