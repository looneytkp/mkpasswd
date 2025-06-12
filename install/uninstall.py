#!/usr/bin/env python3

import os
import shutil
import platform

def is_windows():
    return os.name == "nt"

HOME = os.environ.get("USERPROFILE", os.path.expanduser("~")) if is_windows() else os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
BIN_DIR = os.path.join(HOME, ".local", "bin")
LAUNCHER = "vaultpass.py" if is_windows() else "vaultpass"
LOCAL_BIN = os.path.join(BIN_DIR, LAUNCHER)

# Print locations for clarity
print(f"[i] Vaultpass directory: {INSTALL_DIR}")
print(f"[i] Launcher: {LOCAL_BIN}")

print("[?] Uninstall Vaultpass? (Y/n): ", end="")
answer = input().strip()

if answer.lower() in ["y", ""]:
    # Remove ~/.vaultpass
    if os.path.isdir(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR, ignore_errors=True)
        print(f"[✓] Removed directory: {INSTALL_DIR}")
    # Remove ~/.local/bin/vaultpass(.py)
    if os.path.isfile(LOCAL_BIN):
        os.remove(LOCAL_BIN)
        print(f"[✓] Removed launcher: {LOCAL_BIN}")

    # Clean PATH from shell config files (not on Windows)
    if not is_windows():
        rc_files = [os.path.expanduser("~/.bashrc"), os.path.expanduser("~/.zshrc"), os.path.expanduser("~/.bash_profile")]
        for rc_file in rc_files:
            if os.path.isfile(rc_file):
                with open(rc_file, "r") as f:
                    lines = f.readlines()
                filtered = [line for line in lines if ".local/bin" not in line or "export PATH" not in line]
                if len(filtered) != len(lines):
                    with open(rc_file, "w") as f:
                        f.writelines(filtered)
                    print(f"[✓] Cleaned PATH entry from {rc_file}")

    # Friendly Windows guidance
    if is_windows():
        print(f"[i] Please remove '{BIN_DIR}' from your system PATH if you added it, for a full cleanup.")
        print("    (Search 'Edit environment variables' in Start Menu → Edit your PATH variable)")

    print("[✓] Vaultpass is uninstalled.")
else:
    print("[!] Uninstall cancelled.")