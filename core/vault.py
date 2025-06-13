# core/vault.py

import os
import sys
import time
import shutil
import getpass
import hashlib

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
HASH_FILE = os.path.join(SYSTEM_DIR, "passphrase_hash.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")

def log_action(msg):
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def hash_passphrase(passphrase):
    # Simple hash for illustration; use stronger hash+salt for production!
    return hashlib.sha256(passphrase.encode()).hexdigest()

def require_passphrase_setup(show_hint_only_on_prompt=False):
    from cli import show_banner  # local import to avoid circular

    # First run: Passphrase setup
    if not os.path.isfile(HASH_FILE):
        show_banner()
        print("First run: You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        for attempt in range(3):
            passphrase = getpass.getpass("[*] Enter a passphrase [Leave blank for NO Encryption]: ")
            if passphrase == "":
                print("[!] Warning: Passwords will NOT be encrypted!")
                # Save empty hash file to indicate "no encryption"
                with open(HASH_FILE, "w") as f:
                    f.write("")
                if os.path.exists(HINT_FILE):
                    os.remove(HINT_FILE)
                break
            confirm = getpass.getpass("[*] Confirm passphrase: ")
            if passphrase == confirm:
                with open(HASH_FILE, "w") as f:
                    f.write(hash_passphrase(passphrase))
                hint = input("[*] Enter a passphrase hint (optional): ").strip()
                with open(HINT_FILE, "w") as f:
                    f.write(hint)
                log_action("Set master passphrase and hint")
                print("[*] Passphrase and hint saved.")
                if hint:
                    print("💡 Hint:", hint)
                break
            else:
                print(f"[X] Passphrases do not match. {2 - attempt} tries left.")
        else:
            print("Passphrase not set, passwords won't be encrypted")
            with open(HASH_FILE, "w") as f:
                f.write("")
            if os.path.exists(HINT_FILE):
                os.remove(HINT_FILE)

    # All subsequent runs:
    elif os.path.isfile(HASH_FILE):
        with open(HASH_FILE) as f:
            saved_hash = f.read().strip()
        if saved_hash == "":
            print("[!] No encryption enabled. Proceeding without passphrase.")
            return
        for _ in range(3):
            passphrase = getpass.getpass("[*] Enter your master passphrase: ")
            if hash_passphrase(passphrase) == saved_hash:
                if show_hint_only_on_prompt and os.path.isfile(HINT_FILE):
                    with open(HINT_FILE) as hf:
                        hint = hf.read().strip()
                        if hint:
                            print("💡 Hint:", hint)
                return
            else:
                print("[X] Incorrect passphrase.")
        print("[X] Too many incorrect attempts. Exiting.")
        sys.exit(1)
    else:
        print("[!] No encryption enabled. Proceeding without passphrase.")

def list_entries():
    require_passphrase_setup(show_hint_only_on_prompt=True)
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        for line in f:
            print("[✓]", line.strip())
    log_action("Listed all passwords")

def add_entry(id, user="", pwd="", info=""):
    require_passphrase_setup(show_hint_only_on_prompt=True)
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    line = f"{id}:|{user}|{pwd}|{info}\n"
    with open(PASS_FILE, "a") as f:
        f.write(line)
    print(f"[✓] Saved password for {id}.")
    log_action(f"Saved password for {id}")

def edit_entry(id, new_user):
    require_passphrase_setup(show_hint_only_on_prompt=True)
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        lines = f.readlines()
    new_lines, found = [], False
    for line in lines:
        if line.startswith(f"{id}:"):
            parts = line.strip().split("|")
            parts[1] = new_user
            new_line = "|".join(parts) + "\n"
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)
    if found:
        with open(PASS_FILE, "w") as f:
            f.writelines(new_lines)
        print(f"[✓] Username/email updated for {id}.")
        log_action(f"Edited entry for {id}")
    else:
        print("[X] ID not found.")

def delete_entry(id):
    require_passphrase_setup(show_hint_only_on_prompt=True)
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        lines = f.readlines()
    new_lines, found = [], False
    for line in lines:
        if line.startswith(f"{id}:"):
            found = True
            continue
        new_lines.append(line)
    if found:
        with open(PASS_FILE, "w") as f:
            f.writelines(new_lines)
        print(f"[✓] Deleted {id}.")
        log_action(f"Deleted {id}")
    else:
        print("[X] ID not found.")

def search_entry(id):
    require_passphrase_setup(show_hint_only_on_prompt=True)
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        found = False
        for line in f:
            if line.startswith(f"{id}:"):
                print("[✓]", line.strip())
                found = True
                log_action(f"Searched for {id}")
    if not found:
        print(f"[X] ID {id} not found.")

def backup_vault():
    require_passphrase_setup(show_hint_only_on_prompt=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault to backup.")
        return
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"passwords_{timestamp}.gpg")
    shutil.copy2(PASS_FILE, backup_file)
    if os.path.isfile(HINT_FILE):
        shutil.copy2(HINT_FILE, os.path.join(BACKUP_DIR, "passphrase_hint.txt"))
    print(f"[✓] Backup saved to {BACKUP_DIR}")
    log_action("Vault backup")

def restore_vault(backup_name):
    require_passphrase_setup(show_hint_only_on_prompt=True)
    backup_file = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.isfile(backup_file):
        print("[X] Backup not found.")
        return
    shutil.copy2(backup_file, PASS_FILE)
    hint_file = os.path.join(BACKUP_DIR, "passphrase_hint.txt")
    if os.path.isfile(hint_file):
        shutil.copy2(hint_file, HINT_FILE)
    print("[✓] Restored Vaultpass vault from backup.")
    log_action(f"Vault restored from {backup_name}")

# Example of usage for direct script run
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "list":
        list_entries()
    elif cmd == "add":
        add_entry(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "edit":
        edit_entry(sys.argv[2], sys.argv[3])
    elif cmd == "delete":
        delete_entry(sys.argv[2])
    elif cmd == "search":
        search_entry(sys.argv[2])
    elif cmd == "backup":
        backup_vault()
    elif cmd == "restore":
        restore_vault(sys.argv[2])
    else:
        print("Usage: vault.py [list|add|edit|delete|search|backup|restore]")