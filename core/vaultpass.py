#!/usr/bin/env python3
import os
import sys

# ----------- Constants for Folder Structure -----------
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

# ----------- Check Required Modules Exist -----------
REQUIRED_MODULES = [
    "cli.py",
    "update.py",
    "changelog.py",
    "password_gen.py",
    "config.py",
    "uninstall.py"
]
REQUIRED_SYSTEM_FILES = [
    "changelog.txt",
    "version.txt"
]

missing_core = [f for f in REQUIRED_MODULES if not os.path.isfile(os.path.join(CORE_DIR, f))]
missing_system = [f for f in REQUIRED_SYSTEM_FILES if not os.path.isfile(os.path.join(SYSTEM_DIR, f))]

if missing_core or missing_system:
    if missing_core:
        print(f"[X] Missing required core files: {', '.join(missing_core)}")
    if missing_system:
        print(f"[X] Missing required system files: {', '.join(missing_system)}")
    sys.exit(1)

# ----------- Import Modular Code -----------
sys.path.insert(0, CORE_DIR)
import cli
import update
import changelog
import password_gen
import config
import uninstall

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