@echo off
VT SCANNER


:MULAI
cls
color 0A
echo ==================================================
echo   CHIMERA / VIRUSTOTAL ANALYZER
echo ==================================================
echo.
echo Langkah-langkah:
echo 1. Copy domain dari Excel kamu.
echo 2. Paste di bawah sini.
echo 3. Tekan ENTER 2x (dua kali) agar script jalan.
echo.

:: Menjalankan Python
python analisa_domain_vtpy.py

echo.
echo ==================================================
echo   PROSES SELESAI.
echo ==================================================
echo.

:: Loop otomatis (Re-run)
set /p pilihan="Mau scan lagi? (y/n): "
if /i "%pilihan%"=="y" goto MULAI
if /i "%pilihan%"=="Y" goto MULAI

echo.
Ciao
pause
exit