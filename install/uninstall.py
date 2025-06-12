#!/usr/bin/env python3
"""
uninstall.py -- Vaultpass uninstaller

- Confirms user intent
- Deletes all Vaultpass data
- Cleans up PATH and binaries
- Outputs status
"""

import os
import shutil

def clean_path(bin_dir):
    home = os.path.expanduser("~")
    rc_files = [
        os.path.join(home, ".bashrc"),
        os.path.join(home, ".zshrc"),
        os.path.join(home, ".bash_profile")
    ]
    export_line = f'export PATH="{bin_dir}:$PATH"'
    for rc in rc_files:
        if os.path.exists(rc):
            with open(rc, "r") as f:
                lines = f.readlines()
            with open(rc, "w") as f:
                for line in lines:
                    if export_line not in line:
                        f.write(line)

def main():
    home = os.path.expanduser("~")
    install_dir = os.path.join(home, ".vaultpass")
    bin_dir = os.path.join(home, ".local", "bin")
    bin_file = os.path.join(bin_dir, "vaultpass")
    bin_file_py = os.path.join(bin_dir, "vaultpass.py")
    confirm = input("[?] Uninstall Vaultpass? (Y/n): ").strip().lower()
    if confirm not in ("y", ""):
        print("[!] Uninstall cancelled.")
        return
    # Remove install dir
    if os.path.exists(install_dir):
        shutil.rmtree(install_dir, ignore_errors=True)
        print(f"[✓] Removed {install_dir}")
    # Remove binaries
    for f in [bin_file, bin_file_py]:
        if os.path.exists(f):
            os.remove(f)
            print(f"[✓] Removed {f}")
    # Clean PATH from rc files
    clean_path(bin_dir)
    print("[✓] Vaultpass uninstalled. All data and binaries removed.")

if __name__ == "__main__":
    main()