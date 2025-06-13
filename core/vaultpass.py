#!/usr/bin/env python3
import os
import sys
import subprocess

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")
CHANGELOG_FILE = os.path.join(SYSTEM_DIR, "changelog.txt")
VERSION_FILE = os.path.join(SYSTEM_DIR, "version.txt")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
BIN_PATH = os.path.join(HOME, ".local", "bin", "vaultpass")
LAST_UPDATE_FILE = os.path.join(SYSTEM_DIR, ".last_update_check")
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"

# Ensure .config exists in ~/.vaultpass
CONFIG_FILE = os.path.join(INSTALL_DIR, ".config")
DEFAULT_CONFIG = "encryption=on\npassphrase_set=no\ntheme=light\n"
if not os.path.exists(CONFIG_FILE):
    os.makedirs(INSTALL_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(DEFAULT_CONFIG)

def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE) as f:
            return f.read().strip()
    return "0.0.0"

def ensure_init_py():
    init_path = os.path.join(CORE_DIR, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "a").close()

ensure_init_py()

REQUIRED_CORE_FILES = [
    "cli.py", "update.py", "changelog.py", "password_gen.py", "config.py", "vault.py"
]
REQUIRED_SYSTEM_FILES = ["changelog.txt", "version.txt"]
REQUIRED_INSTALL_FILES = ["setup.py", "uninstall.py"]

missing_core = [f for f in REQUIRED_CORE_FILES if not os.path.isfile(os.path.join(CORE_DIR, f))]
missing_system = [f for f in REQUIRED_SYSTEM_FILES if not os.path.isfile(os.path.join(SYSTEM_DIR, f))]
missing_install = [f for f in REQUIRED_INSTALL_FILES if not os.path.isfile(os.path.join(INSTALL_DIR, "install", f))]

if missing_core or missing_system or missing_install:
    missing_msgs = []
    if missing_core:
        missing_msgs.append(f"core files: {', '.join(missing_core)}")
    if missing_system:
        missing_msgs.append(f"system files: {', '.join(missing_system)}")
    if missing_install:
        missing_msgs.append(f"install files: {', '.join(missing_install)}")
    print(f"[X] Missing required Vaultpass files: {', '.join(missing_msgs)}")
    setup_path = os.path.join(INSTALL_DIR, "install", "setup.py")
    if os.path.isfile(setup_path):
        resp = input("[?] Vaultpass is broken or incomplete. Reinstall now? (Y/n): ").strip().lower()
        if resp in ("y", ""):
            print("[*] Reinstalling Vaultpass...")
            subprocess.run(["python3", setup_path])
        else:
            print("[X] Aborted. Vaultpass may not work correctly until you reinstall.")
    else:
        print("[X] setup.py is missing. Please reinstall Vaultpass from GitHub.")
    sys.exit(1)

sys.path.insert(0, CORE_DIR)
import cli
import update
import changelog
import password_gen
import config
import vault

def main():
    # For brevity, skipping update checks here. Add if you use updates.
    cli.run_cli()

if __name__ == "__main__":
    main()