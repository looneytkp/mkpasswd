#!/usr/bin/env python3

import os
import sys
import argparse
import shutil
import subprocess
import datetime
import requests

# ===============================
#           VAULTPASS
# ===============================

INSTALL_DIR = os.path.expanduser("~/.vaultpass")
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PASS_FILE = os.path.join(INSTALL_DIR, "system", "passwords.gpg")
HINT_FILE = os.path.join(INSTALL_DIR, "system", "passphrase_hint.txt")
LOG_FILE = os.path.join(INSTALL_DIR, "system", "vaultpass.log")
CHANGELOG_FILE = os.path.abspath(os.path.join(CORE_DIR, "..", "changelog.txt"))
VERSION_FILE = os.path.abspath(os.path.join(CORE_DIR, "..", "version.txt"))
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"
LAST_UPDATE_FILE = os.path.join(INSTALL_DIR, "system", ".last_update_check")
VAULT_PY = os.path.join(CORE_DIR, "vault.py")
PASSGEN_PY = os.path.join(CORE_DIR, "password_gen.py")

[os.makedirs(os.path.join(INSTALL_DIR, "system"), exist_ok=True) for _ in range(1)]
if not os.path.exists(VERSION_FILE):
    with open(VERSION_FILE, "w") as f:
        f.write("v1.6\n")

def get_version():
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except Exception:
        return "v1.6"

VERSION = get_version()

def log_action(msg):
    with open(LOG_FILE, "a") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{now} {msg}\n")

def require_passphrase_setup():
    if not os.path.isfile(HINT_FILE):
        print("[*] First run: You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        hint = input("[*] Enter a passphrase hint (for your eyes only, can be blank): ")
        os.makedirs(os.path.dirname(HINT_FILE), exist_ok=True)
        with open(HINT_FILE, "w") as f:
            f.write(hint)
        log_action("Set passphrase hint")
        print("[*] Passphrase hint saved.")
    if os.path.isfile(HINT_FILE):
        with open(HINT_FILE) as f:
            hint = f.read().strip()
        print(f"💡 Hint: {hint}")

def show_changelog(ver=None):
    ver = (ver or VERSION).lstrip("v")
    print(f"[*] Version {ver}")
    found = False
    with open(CHANGELOG_FILE) as f:
        for line in f:
            if line.strip().startswith(f"Version {ver}"):
                found = True
                continue
            if found:
                if line.strip().startswith("Version "):
                    break
                print(line.rstrip())
    print("[*] Full changelog: https://github.com/looneytkp/vaultpass")

def check_for_updates(force=False):
    need_update = False
    # check timestamp
    if force:
        need_update = True
    elif os.path.exists(LAST_UPDATE_FILE):
        last = os.path.getmtime(LAST_UPDATE_FILE)
        now = datetime.datetime.now().timestamp()
        diff = int((now - last) / 86400)
        if diff >= 3:
            need_update = True
    else:
        need_update = True

    if need_update:
        print("[*] Checking for Vaultpass updates...")
        try:
            with open(VERSION_FILE) as f:
                local_version = f.read().strip()
        except Exception:
            local_version = "v1.6"
        try:
            remote_version = requests.get(REMOTE_VERSION_URL, timeout=5).text.strip()
        except Exception:
            remote_version = local_version

        if local_version != remote_version:
            print("[!] New version available!")
            print(f"[!] Currently installed: {local_version}")
            print(f"[!] Latest: {remote_version}")
            print("[*] Changelog for latest version:")
            show_changelog(remote_version)
            u = input("[?] Do you want to update now? (Y/n): ")
            if u.strip().lower() in ("y", ""):
                print("[*] Updating Vaultpass…")
                try:
                    subprocess.run(["git", "pull", "origin", "main"], cwd=os.path.join(CORE_DIR, ".."),
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    with open(VERSION_FILE, "w") as f:
                        f.write(remote_version)
                    print(f"[✓] Vaultpass updated to {remote_version}.")
                    log_action(f"Vaultpass updated to {remote_version}")
                except Exception:
                    print("[X] Update failed.")
        else:
            # Minor updates (same version, new commit)
            try:
                local_commit = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=os.path.join(CORE_DIR, "..")).decode().strip()
                subprocess.run(["git", "fetch", "origin", "main"],
                               cwd=os.path.join(CORE_DIR, ".."),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                remote_commit = subprocess.check_output(
                    ["git", "rev-parse", "origin/main"], cwd=os.path.join(CORE_DIR, "..")).decode().strip()
            except Exception:
                local_commit, remote_commit = "", ""
            if local_commit and remote_commit and local_commit != remote_commit:
                try:
                    msg = subprocess.check_output(
                        ["git", "log", "-1", "--pretty=%B", "origin/main"],
                        cwd=os.path.join(CORE_DIR, "..")).decode().splitlines()[0]
                except Exception:
                    msg = "No commit message"
                print(f"[!] Minor updates available: {msg}")
                u = input("[?] Update? (Y/n): ")
                if u.strip().lower() in ("y", ""):
                    print("[*] Updating Vaultpass…")
                    try:
                        subprocess.run(["git", "pull", "origin", "main"], cwd=os.path.join(CORE_DIR, ".."),
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print("[✓] Vaultpass updated to latest code (version unchanged).")
                        log_action("Vaultpass minor update")
                    except Exception:
                        print("[X] Update failed.")
            else:
                print("[✓] Vaultpass is up to date.")
        with open(LAST_UPDATE_FILE, "a"):
            os.utime(LAST_UPDATE_FILE, None)
    else:
        print("[✓] Vaultpass is up to date.")

def show_help():
    print(f"Vaultpass - Secure Password Manager {VERSION}")
    print("""
Usage: vaultpass [OPTIONS]
Options:
  -l, --long [ID ...]        Generate long password(s)
  -s, --short [ID ...]       Generate short password(s)
  -c, --custom [ID ...]      Save custom password(s)
  -L, --list                 List all saved passwords
  -S, --search [ID ...]      Search for passwords by ID
  -d, --delete [ID ...]      Delete password(s) by ID
  -e, --edit [ID]            Edit username/email
  --change-passphrase        Change master passphrase
  -b, --backup               Backup passwords
  -r, --restore              Restore from backup
  --log                      Show action log
  -u, --uninstall            Uninstall Vaultpass
  --update                   Check for updates now
  -a, --about                Show all features
  -h, --help                 Show this help
  --changelog                Show latest changelog
""")

def show_features():
    print("""Vaultpass Functions:
- Generate secure passwords (short, long, or custom)
- Save username/email with each password
- Add optional 'info' field (e.g. what the password is for)
- View, search, delete, or edit saved passwords
- Backup and restore encrypted vaults
- more features coming soon
""")

def show_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            print(f.read())
    else:
        print("[!] No log found.")

def backup_passwords():
    require_passphrase_setup()
    backup_dir = os.path.join(INSTALL_DIR, "backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"passwords_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.gpg")
    shutil.copy(PASS_FILE, backup_file)
    shutil.copy(HINT_FILE, os.path.join(backup_dir, "passphrase_hint.txt"))
    print(f"[✓] Backup saved to {backup_dir}")
    log_action("Vault backup")

def restore_passwords():
    require_passphrase_setup()
    backup_dir = os.path.join(INSTALL_DIR, "backup")
    print("[*] Backups found:")
    try:
        backups = [f for f in os.listdir(backup_dir) if f.endswith(".gpg")]
    except Exception:
        backups = []
    if not backups:
        print("[!] No backups found.")
        return
    for f in backups:
        print(f"     - {f}")
    f = input("[?] Enter backup filename to restore: ")
    shutil.copy(os.path.join(backup_dir, f), PASS_FILE)
    hint_path = os.path.join(backup_dir, "passphrase_hint.txt")
    if os.path.exists(hint_path):
        shutil.copy(hint_path, HINT_FILE)
    print("[✓] Restored Vaultpass vault from backup.")
    log_action(f"Vault restored from {f}")

def edit_entry(entry_id):
    require_passphrase_setup()
    # Decrypt passwords
    subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
    lines = []
    found = False
    with open(f"{PASS_FILE}.tmp") as f:
        for line in f:
            if line.startswith(f"{entry_id}:"):
                found = True
                old_user = line.strip().split('|')[1]
                print(f"[?] Current username/email: {old_user}")
                new_user = input("[?] Enter new username/email: ")
                lines.append(line.replace(f":|{old_user}|", f":|{new_user}|"))
            else:
                lines.append(line)
    if found:
        with open(f"{PASS_FILE}.tmp", "w") as f:
            f.writelines(lines)
        subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        print(f"[✓] Username/email updated for {entry_id}.")
        log_action(f"Edited entry for {entry_id}")
    else:
        print("[X] ID not found")
        os.remove(f"{PASS_FILE}.tmp")

def change_passphrase():
    require_passphrase_setup()
    print("[?] To change passphrase, enter current passphrase: ")
    r = subprocess.run(["python3", VAULT_PY, "verify", PASS_FILE])
    if r.returncode == 0:
        print("[✓] Verified.")
        while True:
            new1 = input("[?] Set new passphrase: ")
            new2 = input("[?] Verify new passphrase: ")
            if new1 == new2:
                # Pipe new passphrase to change_passphrase
                p = subprocess.Popen(
                    ["python3", VAULT_PY, "change_passphrase", PASS_FILE],
                    stdin=subprocess.PIPE)
                p.communicate(input=new1.encode())
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
    conf = input("[?] Uninstall Vaultpass? (Y/n): ")
    if conf.strip().lower() in ("y", ""):
        try:
            shutil.rmtree(INSTALL_DIR)
            print("[✓] Vaultpass uninstalled.")
        except Exception:
            print("[X] Failed to remove install directory.")
    else:
        print("[!] Uninstall cancelled.")

def list_passwords():
    require_passphrase_setup()
    subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
    with open(f"{PASS_FILE}.tmp") as f:
        for line in f:
            print(f"[✓] {line.strip()}")
    os.remove(f"{PASS_FILE}.tmp")
    log_action("Listed all passwords")

def search_passwords(ids):
    require_passphrase_setup()
    for entry_id in ids:
        subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        found = False
        with open(f"{PASS_FILE}.tmp") as f:
            for line in f:
                if line.startswith(f"{entry_id}:"):
                    print(f"[✓] {line.strip()}")
                    found = True
        if not found:
            print(f"[X] ID {entry_id} not found")
        os.remove(f"{PASS_FILE}.tmp")
        log_action(f"Searched for {entry_id}")

def delete_passwords(ids):
    require_passphrase_setup()
    for entry_id in ids:
        subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp") as f:
            lines = [line for line in f if not line.startswith(f"{entry_id}:")]
        with open(f"{PASS_FILE}.tmp2", "w") as f:
            f.writelines(lines)
        subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp2", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        os.remove(f"{PASS_FILE}.tmp2")
        print(f"[✓] Deleted {entry_id}.")
        log_action(f"Deleted {entry_id}")

def generate_passwords(ids, mode):
    require_passphrase_setup()
    for entry_id in ids:
        pwd = subprocess.check_output(["python3", PASSGEN_PY, mode]).decode().strip()
        print(f"[?] Password for {entry_id}: {pwd}")
        user = input(f"[?] Enter username/email for {entry_id} (optional): ")
        info = input(f"[?] Add info/description for {entry_id} (optional): ")
        subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp", "a") as f:
            f.write(f"{entry_id}:|{user}|{pwd}|{info}\n")
        subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        print(f"[✓] Saved password for {entry_id}.")
        log_action(f"Saved password for {entry_id}")

def save_custom_passwords(ids):
    require_passphrase_setup()
    for entry_id in ids:
        pwd = input(f"[?] Enter password for {entry_id}: ")
        user = input(f"[?] Enter username/email for {entry_id} (optional): ")
        info = input(f"[?] Add info/description for {entry_id} (optional): ")
        subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp", "a") as f:
            f.write(f"{entry_id}:|{user}|{pwd}|{info}\n")
        subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        print(f"[✓] Saved custom password for {entry_id}.")
        log_action(f"Saved custom password for {entry_id}")

def main():
    parser = argparse.ArgumentParser(
        description=f"Vaultpass - Secure Password Manager {VERSION}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-l", "--long", nargs="*", metavar="ID", help="Generate long password(s)")
    parser.add_argument("-s", "--short", nargs="*", metavar="ID", help="Generate short password(s)")
    parser.add_argument("-c", "--custom", nargs="*", metavar="ID", help="Save custom password(s)")
    parser.add_argument("-L", "--list", action="store_true", help="List all saved passwords")
    parser.add_argument("-S", "--search", nargs="*", metavar="ID", help="Search for passwords by ID")
    parser.add_argument("-d", "--delete", nargs="*", metavar="ID", help="Delete password(s) by ID")
    parser.add_argument("-e", "--edit", metavar="ID", help="Edit username/email")
    parser.add_argument("--change-passphrase", action="store_true", help="Change master passphrase")
    parser.add_argument("-b", "--backup", action="store_true", help="Backup passwords")
    parser.add_argument("-r", "--restore", action="store_true", help="Restore from backup")
    parser.add_argument("--log", action="store_true", help="Show action log")
    parser.add_argument("-u", "--uninstall", action="store_true", help="Uninstall Vaultpass")
    parser.add_argument("--update", action="store_true", help="Check for updates now")
    parser.add_argument("-a", "--about", action="store_true", help="Show all features")
    parser.add_argument("--changelog", action="store_true", help="Show latest changelog")
    args = parser.parse_args()

    # Auto check for updates every run (except when uninstalling)
    if not args.uninstall:
        check_for_updates(force=args.update)

    if args.long:
        generate_passwords(args.long, "long")
    elif args.short:
        generate_passwords(args.short, "short")
    elif args.custom:
        save_custom_passwords(args.custom)
    elif args.list:
        list_passwords()
    elif args.search:
        search_passwords(args.search)
    elif args.delete:
        delete_passwords(args.delete)
    elif args.edit:
        edit_entry(args.edit)
    elif args.change_passphrase:
        change_passphrase()
    elif args.backup:
        backup_passwords()
    elif args.restore:
        restore_passwords()
    elif args.log:
        show_log()
    elif args.uninstall:
        uninstall()
    elif args.about:
        show_features()
    elif args.changelog:
        show_changelog()
    else:
        show_help()

if __name__ == "__main__":
    main()