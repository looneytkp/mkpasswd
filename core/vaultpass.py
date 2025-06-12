#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil
import time

VERSION = "v1.6"
HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")
CHANGELOG_FILE = os.path.join(INSTALL_DIR, "changelog.txt")
VERSION_FILE = os.path.join(INSTALL_DIR, "version.txt")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
VAULT_PY = os.path.join(CORE_DIR, "vault.py")
PASSGEN_PY = os.path.join(CORE_DIR, "password_gen.py")
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"

def log_action(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def require_passphrase_setup():
    if not os.path.exists(HINT_FILE):
        print("[*] First run: You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        hint = input("[*] Enter a passphrase hint (for your eyes only, can be blank): ")
        os.makedirs(SYSTEM_DIR, exist_ok=True)
        with open(HINT_FILE, "w") as f:
            f.write(hint)
        log_action("Set passphrase hint")
        print("[*] Passphrase hint saved.")
    if os.path.exists(HINT_FILE):
        with open(HINT_FILE) as f:
            print("💡 Hint:", f.read().strip())

def show_changelog():
    if not os.path.exists(CHANGELOG_FILE):
        print("[!] No changelog found.")
        return
    with open(CHANGELOG_FILE) as f:
        for line in f:
            print(line.rstrip())

def show_features():
    print("""
Vaultpass Functions:
- Generate secure passwords (short, long, or custom)
- Save username/email with each password
- Add optional 'info' field (e.g. what the password is for)
- View, search, delete, or edit saved passwords
- Backup and restore encrypted vaults
- more features coming soon
""")

def show_log():
    if not os.path.exists(LOG_FILE):
        print("[!] No log file found.")
        return
    with open(LOG_FILE) as f:
        print(f.read())

def backup_passwords():
    require_passphrase_setup()
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"passwords_{timestamp}.gpg")
    shutil.copy2(PASS_FILE, backup_file)
    shutil.copy2(HINT_FILE, os.path.join(BACKUP_DIR, "passphrase_hint.txt"))
    print(f"[✓] Backup saved to {BACKUP_DIR}")
    log_action("Vault backup")

def restore_passwords():
    require_passphrase_setup()
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".gpg")]
    if not backups:
        print("[!] No backups found.")
        return
    print("[*] Backups found:")
    for f in backups:
        print(f"     - {f}")
    chosen = input("[?] Enter backup filename to restore: ").strip()
    backup_path = os.path.join(BACKUP_DIR, chosen)
    if not os.path.exists(backup_path):
        print("[X] Backup not found.")
        return
    shutil.copy2(backup_path, PASS_FILE)
    hint_path = os.path.join(BACKUP_DIR, "passphrase_hint.txt")
    if os.path.exists(hint_path):
        shutil.copy2(hint_path, HINT_FILE)
    print("[✓] Restored Vaultpass vault from backup.")
    log_action(f"Vault restored from {chosen}")

def edit_entry(entry_id):
    require_passphrase_setup()
    subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
    with open(f"{PASS_FILE}.tmp") as f:
        lines = f.readlines()
    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{entry_id}:"):
            old_user = line.split("|")[1]
            print(f"[?] Current username/email: {old_user}")
            new_user = input("[?] Enter new username/email: ")
            parts = line.split("|")
            parts[1] = new_user
            new_line = "|".join(parts)
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)
    if not found:
        print("[X] ID not found.")
        os.remove(f"{PASS_FILE}.tmp")
        return
    with open(f"{PASS_FILE}.tmp", "w") as f:
        f.writelines(new_lines)
    subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
    os.remove(f"{PASS_FILE}.tmp")
    print(f"[✓] Username/email updated for {entry_id}.")
    log_action(f"Edited entry for {entry_id}")

def change_passphrase():
    require_passphrase_setup()
    print("[?] To change passphrase, enter current passphrase: ")
    rc = subprocess.run(["python3", VAULT_PY, "verify", PASS_FILE])
    if rc.returncode == 0:
        print("[✓] Verified.")
        while True:
            new1 = input("[?] Set new passphrase: ")
            new2 = input("[?] Verify new passphrase: ")
            if new1 == new2:
                p = subprocess.run(["python3", VAULT_PY, "change_passphrase", PASS_FILE], input=new1, text=True)
                if p.returncode == 0:
                    print("[✓] New passphrase set.")
                    log_action("Passphrase changed")
                else:
                    print("[X] Failed to set new passphrase!")
                break
            else:
                print("[X] Passphrase does not match!")
    else:
        print("[X] Invalid passphrase. Try again.")

def uninstall():
    confirm = input("[?] Uninstall Vaultpass? (Y/n): ").strip().lower()
    if confirm in ("y", ""):
        shutil.rmtree(INSTALL_DIR, ignore_errors=True)
        bin_file = os.path.join(HOME, ".local", "bin", "vaultpass")
        if os.path.exists(bin_file):
            os.remove(bin_file)
        print("[✓] Vaultpass is uninstalled.")
    else:
        print("[!] Uninstall cancelled.")

def main():
    parser = argparse.ArgumentParser(
        description=f"Vaultpass - Secure Password Manager {VERSION}",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False
    )
    parser.add_argument("-l", "--long", nargs="+", help="Generate long password(s)")
    parser.add_argument("-s", "--short", nargs="+", help="Generate short password(s)")
    parser.add_argument("-c", "--custom", nargs="+", help="Save custom password(s)")
    parser.add_argument("-L", "--list", action="store_true", help="List all saved passwords")
    parser.add_argument("-S", "--search", nargs="+", help="Search for passwords by ID")
    parser.add_argument("-d", "--delete", nargs="+", help="Delete password(s) by ID")
    parser.add_argument("-e", "--edit", help="Edit username/email")
    parser.add_argument("--change-passphrase", action="store_true", help="Change master passphrase")
    parser.add_argument("-b", "--backup", action="store_true", help="Backup passwords")
    parser.add_argument("-r", "--restore", action="store_true", help="Restore from backup")
    parser.add_argument("--log", action="store_true", help="Show action log")
    parser.add_argument("-u", "--uninstall", action="store_true", help="Uninstall Vaultpass")
    parser.add_argument("--update", action="store_true", help="Check for updates now")
    parser.add_argument("-a", "--about", action="store_true", help="Show all features")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help")
    parser.add_argument("--changelog", action="store_true", help="Show latest changelog")

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        return
    if args.about:
        show_features()
        return
    if args.changelog:
        show_changelog()
        return
    if args.log:
        show_log()
        return
    if args.update:
        print("[*] Update logic not yet implemented in this sample.")
        return
    if args.backup:
        backup_passwords()
        return
    if args.restore:
        restore_passwords()
        return
    if args.edit:
        if args.edit:
            edit_entry(args.edit)
        else:
            print("Usage: vaultpass -e ID")
        return
    if args.change_passphrase:
        change_passphrase()
        return
    if args.list:
        require_passphrase_setup()
        subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp") as f:
            for line in f:
                print("[✓]", line.strip())
        os.remove(f"{PASS_FILE}.tmp")
        log_action("Listed all passwords")
        return
    if args.uninstall:
        uninstall()
        return

    # Add additional handling for add/search/delete/generate logic as you need

    parser.print_help()

if __name__ == "__main__":
    main()