#!/usr/bin/env python3
import os
import sys
import subprocess

# ----------- Constants for Folder Structure -----------
HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
INSTALL_DIR_INSTALL = os.path.join(INSTALL_DIR, "install")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")
CHANGELOG_FILE = os.path.join(SYSTEM_DIR, "changelog.txt")
VERSION_FILE = os.path.join(SYSTEM_DIR, "version.txt")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
BIN_PATH = os.path.join(HOME, ".local", "bin", "vaultpass")
LAST_UPDATE_FILE = os.path.join(SYSTEM_DIR, ".last_update_check")
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"

def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE) as f:
            return f.read().strip()
    return "0.0.0"

# ----------- Ensure __init__.py Exists -----------
def ensure_init_py():
    """Create __init__.py in core/ if missing, for reliable imports."""
    init_path = os.path.join(CORE_DIR, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "a").close()
        print("[!] Fixed missing __init__.py in core/ (required for imports)")

ensure_init_py()  # Always run this at startup

# ----------- Check Required Files Exist -----------
REQUIRED_CORE_FILES = [
    "cli.py",
    "update.py",
    "changelog.py",
    "password_gen.py",
    "config.py",
    "vault.py",
]
REQUIRED_SYSTEM_FILES = [
    "changelog.txt",
    "version.txt"
]
REQUIRED_INSTALL_FILES = [
    "setup.py",
    "uninstall.py"
]

missing_core = [f for f in REQUIRED_CORE_FILES if not os.path.isfile(os.path.join(CORE_DIR, f))]
missing_system = [f for f in REQUIRED_SYSTEM_FILES if not os.path.isfile(os.path.join(SYSTEM_DIR, f))]
missing_install = [f for f in REQUIRED_INSTALL_FILES if not os.path.isfile(os.path.join(INSTALL_DIR, "install", f))]

if missing_core or missing_system or missing_install:
    # Always show all missing, but handle setup.py special
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
        print("[X] setup.py is missing. Please reinstall Vaultpass from GitHub:\n    https://github.com/looneytkp/vaultpass")
    sys.exit(1)

# ----------- Import Modular Code -----------
sys.path.insert(0, CORE_DIR)
import cli
import update
import changelog
import password_gen
import config
import vault

# ----------- Main Entry Point -----------
def main():
    # 3-day auto update check on startup
    update.check_for_updates(
        current_version=get_current_version(),
        version_file=VERSION_FILE,
        changelog_file=CHANGELOG_FILE,
        install_dir=INSTALL_DIR,
        core_dir=CORE_DIR,
        bin_path=BIN_PATH,
        last_update_file=LAST_UPDATE_FILE,
        remote_version_url=REMOTE_VERSION_URL
    )
    cli.run_cli()

if __name__ == "__main__":
    main()