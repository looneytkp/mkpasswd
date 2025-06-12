#!/usr/bin/env python3
import os
import sys

# ----------- Constants for Folder Structure -----------
HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")

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

missing = [f for f in REQUIRED_MODULES if not os.path.isfile(os.path.join(CORE_DIR, f))]
if missing:
    print(f"[X] Missing required core files: {', '.join(missing)}")
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
    cli.run_cli()

if __name__ == "__main__":
    main()