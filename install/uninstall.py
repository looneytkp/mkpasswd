#!/usr/bin/env python3

import os
import shutil
import sys

def clean_path_from_shell_rc(bin_dir):
    home = os.path.expanduser("~")
    rc_files = [
        os.path.join(home, ".bashrc"),
        os.path.join(home, ".zshrc"),
        os.path.join(home, ".bash_profile")
    ]
    export_line = f'export PATH="{bin_dir}:$PATH"'
    found = False
    for rc_file in rc_files:
        if os.path.exists(rc_file):
            with open(rc_file, "r") as f:
                lines = f.readlines()
            with open(rc_file, "w") as f:
                for line in lines:
                    if export_line not in line:
                        f.write(line)
                    else:
                        found = True
    if found:
        print(f"[✓] Removed PATH entry from shell configuration ({', '.join([f for f in rc_files if os.path.exists(f)])})")
    else:
        print("[✓] No PATH entry found to remove.")

def main():
    home = os.path.expanduser("~")
    install_dir = os.path.join(home, ".vaultpass")
    bin_dir = os.path.join(home, ".local", "bin")
    bin_file = os.path.join(bin_dir, "vaultpass")
    bin_file_win = os.path.join(bin_dir, "vaultpass.py")

    print("[?] Uninstall Vaultpass? (Y/n): ", end="")
    answer = input().strip().lower()

    if answer not in ["y", ""]:
        print("[!] Uninstall cancelled.")
        return

    if os.path.exists(install_dir):
        shutil.rmtree(install_dir, ignore_errors=True)
        print(f"[✓] Removed {install_dir}")
    else:
        print(f"[✓] No {install_dir} directory found.")

    if os.path.exists(bin_file):
        os.remove(bin_file)
        print(f"[✓] Removed binary: {bin_file}")

    if os.path.exists(bin_file_win):
        os.remove(bin_file_win)
        print(f"[✓] Removed binary: {bin_file_win}")

    clean_path_from_shell_rc(bin_dir)

    print("[✓] Vaultpass is uninstalled.")

if __name__ == "__main__":
    main()