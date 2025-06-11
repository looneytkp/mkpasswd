# mkpasswd

**mkpasswd** is a simple, cross-platform password manager for the terminal.  
Built for Linux, macOS, and Windows with Bash & Python.  
It lets you securely generate, save, search, backup, and restore passwords—with optional username/email and encrypted backups.

---

## ✨ Features

- Interactive password generator (short, long, or custom)
- Secure vault saved with GPG encryption
- Save username/email with each password
- Multi-ID support (save multiple passwords for same ID)
- Auto-backup system (optional encryption, multiple backups)
- Action log for auditing your vault use
- Uninstall with backup prompt and automatic cleanup
- Weekly auto-update check (with changelog display)
- Cross-platform CLI: works on Linux, macOS, and Windows
- Easy one-liner install

---

## 📦 Folder Structure

mkpasswd/
├── core/                  # Main scripts  
│   ├── mkpasswd           # Main Bash script  
│   ├── vault.py
│   ├── password_gen.py
│   └── changelog.txt
│
├── install/               # Installation files  
│   ├── install.sh  
│   ├── uninstall.sh  
│   ├── install.ps1  
│   ├── uninstall.ps1  
│   ├── mkpasswd-launcher (universal launcher)
│
├── system/                # User data files (created on first use)
│   ├── version.txt  
│
├── backup/                # User backups (auto/manual, created at runtime)
│
├── remote/                # Remote install loader  
│   └── remote-install.sh  
│
└── README.md              # Project overview

---

## 🚀 Installation

**Linux/macOS:**

bash <(curl -fsSL https://raw.githubusercontent.com/looneytkp/mkpasswd/main/install/install.sh)

**Windows (PowerShell):**

irm https://raw.githubusercontent.com/looneytkp/mkpasswd/main/install/install.ps1 | iex

or use Git Bash/WSL with the Linux command.

**Universal one-liner:**

bash <(curl -fsSL https://raw.githubusercontent.com/looneytkp/mkpasswd/main/remote/remote-install.sh)

---

## 🛠 Usage

Type `mkpasswd -h` to see all options, including:

- `-l [ID] [USER]` — Generate a long password for an ID (and optional username/email)
- `-s [ID] [USER]` — Generate a short password
- `-c [ID] [USER] [PASS]` — Save a custom password
- `-L` — List all entries
- `-S [TERM]` — Search for ID, username, or email
- `-d [ID]` — Delete an entry
- `-U [ID] [USER]` — Update username/email for an entry
- `--backup` — Manual backup (with encryption option)
- `--restore` — Restore from backup
- `--log` — Show the audit log
- `-u` — Uninstall mkpasswd (with backup prompt)
- `-C` — Show changelog

---

## 🔒 Security Notes

- **Your passphrase is critical.** If forgotten, you can’t recover your passwords.
- You can add a passphrase hint (on first run).
- All files are local; only you can access them unless you share your backups.
- Backups can be encrypted for safety.

---

## 📝 Changelog

See `core/changelog.txt`.

---

## 🤝 Contributors

- Built by [looneytkp](https://github.com/looneytkp)
- Modernized and documented by the community

---

## 📄 License

MIT License (see `LICENSE` file).