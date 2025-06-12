#!/usr/bin/env python3

import os
import shutil
import sys
import platform

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

    print("\n[?] Uninstall Vaultpass? (Y/n): ", end="")
    answer = input().strip().lower()

    if answer not in ["y", ""]:
        print("[!] Uninstall cancelled.")
        return

    removed_any = False

    if os.path.exists(install_dir):
        shutil.rmtree(install_dir, ignore_errors=True)
        print(f"[✓] Removed {install_dir}")
        removed_any = True
    else:
        print(f"[✓] No {install_dir} directory found.")

    if os.path.exists(bin_file):
        os.remove(bin_file)
        print(f"[✓] Removed binary: {bin_file}")
        removed_any = True

    if os.path.exists(bin_file_win):
        os.remove(bin_file_win)
        print(f"[✓] Removed binary: {bin_file_win}")
        removed_any = True

    # PATH cleanup
    if platform.system() == "Windows":
        print("[!] Please remove .vaultpass from your PATH manually if needed (Windows).")
    else:
        clean_path_from_shell_rc(bin_dir)

    if removed_any:
        print("[✓] Vaultpass is uninstalled.\n")
    else:
        print("[✓] Nothing to remove. Vaultpass was already uninstalled.\n")

if __name__ == "__main__":
    main()