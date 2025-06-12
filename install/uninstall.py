#!/usr/bin/env python3
"""
uninstall.py -- Vaultpass uninstaller

- Confirms user intent
- Deletes all Vaultpass data and binaries
- Cleans up PATH entries from rc files
- Confirms removal of backups
- Warns if files/folders aren't found
"""

import os
import shutil

def clean_path(bin_dir):
    """
    Removes export PATH lines from bash/zsh rc files that include Vaultpass's bin_dir.
    """
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
    backup_dir = os.path.join(install_dir, "backup")

    confirm = input("[?] Uninstall Vaultpass? (Y/n): ").strip().lower()
    if confirm not in ("y", ""):
        print("[!] Uninstall cancelled.")
        return

    # Remove install dir (except backup)
    if os.path.exists(install_dir):
        # Remove everything except backup for now
        for item in os.listdir(install_dir):
            path = os.path.join(install_dir, item)
            if os.path.abspath(path) == os.path.abspath(backup_dir):
                continue
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        print(f"[✓] Removed {install_dir} (except backups)")
    else:
        print(f"[!] Vaultpass directory not found: {install_dir}")

    # Remove binaries
    removed_bin = False
    for f in [bin_file, bin_file_py]:
        if os.path.exists(f):
            os.remove(f)
            print(f"[✓] Removed {f}")
            removed_bin = True
        else:
            print(f"[!] Binary not found: {f}")
    if not removed_bin:
        print("[!] No Vaultpass CLI binaries found in .local/bin.")

    # Confirm removal of backups
    if os.path.exists(backup_dir):
        confirm_backup = input("[?] Remove all Vaultpass backups as well? (Y/n): ").strip().lower()
        if confirm_backup in ("y", ""):
            shutil.rmtree(backup_dir, ignore_errors=True)
            print("[✓] Backups removed.")
        else:
            print("[!] Backups retained in:", backup_dir)
    else:
        print("[!] No Vaultpass backups found.")

    # Clean PATH from rc files
    clean_path(bin_dir)
    print("[✓] Vaultpass uninstalled. All data and binaries removed.")

if __name__ == "__main__":
    main()