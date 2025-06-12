#!/usr/bin/env python3

import os
import shutil

HOME = os.path.expanduser("~")
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULTPASS_DIR = os.path.join(HOME, ".vaultpass")
LOCAL_BIN = os.path.join(HOME, ".local", "bin", "vaultpass")
BASHRC = os.path.join(HOME, ".bashrc")

print("[?] Uninstall Vaultpass? (Y/n): ", end="")
answer = input().strip()

if answer.lower() in ["y", ""]:
    # Remove ~/.vaultpass
    if os.path.isdir(VAULTPASS_DIR):
        shutil.rmtree(VAULTPASS_DIR, ignore_errors=True)
    # Remove ~/.local/bin/vaultpass
    if os.path.isfile(LOCAL_BIN):
        os.remove(LOCAL_BIN)
    # Clean PATH from .bashrc if necessary
    if os.path.isfile(BASHRC):
        with open(BASHRC, "r") as f:
            lines = f.readlines()
        filtered = [line for line in lines if 'export PATH="$HOME/.local/bin:$PATH"' not in line]
        if len(filtered) != len(lines):
            with open(BASHRC, "w") as f:
                f.writelines(filtered)
    # Remove project directory (for direct use, not in ~/.vaultpass)
    if os.path.isdir(PROJECT_DIR):
        try:
            shutil.rmtree(PROJECT_DIR, ignore_errors=True)
        except Exception:
            pass
    print("[✓] Vaultpass is uninstalled.")
else:
    print("[!] Uninstall cancelled.")