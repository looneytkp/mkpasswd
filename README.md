# vaultpass

**vaultpass** is a lightweight, offline-first password manager built with Bash and Python.  
It securely stores and manages your credentials using GPG encryption — fast, portable, and private.

---

## 🔐 Features

- Generate secure passwords (short, long, or custom)
- Save optional usernames/emails with each password
- Edit stored usernames/emails
- Search, list, and delete stored entries
- Backup and restore password vaults
- Change your master passphrase
- Auto logs actions with timestamps
- Weekly auto-update checker
- Works on Linux, Termux, and Windows (via PowerShell)

---

## 📦 Installation

### 🔧 Linux / Termux (bash):
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/looneytkp/vaultpass/main/install/setup.sh)
```

### 🪟 Windows (PowerShell):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
iwr -useb https://raw.githubusercontent.com/looneytkp/vaultpass/main/install/setup.ps1 | iex
```

---

## 🧭 Usage

```bash
vaultpass [OPTIONS]
```

### Options:
| Option                  | Description                                      |
|------------------------|--------------------------------------------------|
| `-l [ID]`              | Generate long password and save with ID          |
| `-s [ID]`              | Generate short password and save with ID         |
| `-c [ID]`              | Create custom password (you enter it yourself)   |
| `-L`                   | List all saved passwords                         |
| `-S [ID]`              | Search for saved password by ID                  |
| `-d [ID]`              | Delete saved password by ID                      |
| `-e [ID]`              | Edit username/email of a saved entry             |
| `-b`                   | Backup vault to a timestamped `.gpg` file        |
| `-r`                   | Restore vault from a previous backup             |
| `--change-passphrase`  | Change the master passphrase                     |
| `--update`             | Check for updates manually                       |
| `--log`                | View action log                                  |
| `-a`                   | Show all vaultpass functions                     |
| `-h`, `--help`         | Show usage help                                  |
| `--changelog`, `-c`    | View changelog                                   |
| `-u`                   | Uninstall vaultpass                              |

---

## 💾 Backup & Restore

- **Backup:**  
  `vaultpass -b` — creates a backup file in `.vaultpass/backup/`

- **Restore:**  
  `vaultpass -r` — prompts you to select a backup file

- **Passphrase hint** is also backed up and auto-restored after reinstall.

---

## 🧼 Uninstallation

You can uninstall safely with:
```bash
vaultpass -u
```
Backups will be offered before deletion.

---

## ❤️ Credit

Built by [looneytkp](https://github.com/looneytkp)  
Project: [vaultpass](https://github.com/looneytkp/vaultpass)

---

## 📜 License

MIT License — Free for personal or commercial use.