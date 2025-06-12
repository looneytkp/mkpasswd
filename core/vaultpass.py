#!/usr/bin/env python3
import os
import sys

# ----------- Constants for Folder Structure -----------
HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
# (add any others as needed)

# ----------- Ensure __init__.py Exists -----------
def ensure_init_py():
    """Create __init__.py in core/ if missing, for reliable imports."""
    init_path = os.path.join(CORE_DIR, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "a").close()
        print("[!] Fixed missing __init__.py in core/ (required for imports)")

ensure_init_py()  # Always run this at startup

# ----------- Import Modular Code -----------
# Now you can import your modules (assuming you’ve split up code):
sys.path.insert(0, CORE_DIR)
import cli
import update
import changelog
import config
# ... add imports as you modularize

# ----------- Main Entry Point -----------
def main():
    # Parse CLI and dispatch actions
    cli.run_cli()

if __name__ == "__main__":
    main()