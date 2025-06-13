# core/vault.py

import os
import sys
import time
import shutil

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")

def log_action(msg):
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def require_passphrase_setup():
    if not os.path.isfile(HINT_FILE):
        print("[*] First run: You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        hint = input("[*] Enter a passphrase hint (for your eyes only, can be blank): ")
        os.makedirs(SYSTEM_DIR, exist_ok=True)
        with open(HINT_FILE, "w") as f:
            f.write(hint)
        log_action("Set passphrase hint")
        print("[*] Passphrase hint saved.")
    if os.path.isfile(HINT_FILE):
        with open(HINT_FILE) as f:
            print("💡 Hint:", f.read().strip())

def list_entries():
    require_passphrase_setup()
    # Simulate decrypt (replace with actual decryption in production)
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        for line in f:
            print("[✓]", line.strip())
    log_action("Listed all passwords")

def add_entry(id, user="", pwd="", info=""):
    require_passphrase_setup()
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    line = f"{id}:|{user}|{pwd}|{info}\n"
    with open(PASS_FILE, "a") as f:
        f.write(line)
    print(f"[✓] Saved password for {id}.")
    log_action(f"Saved password for {id}")

def edit_entry(id, new_user):
    require_passphrase_setup()
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
    require_passphrase_setup()
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
    require_passphrase_setup()
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
    require_passphrase_setup()
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
    require_passphrase_setup()
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
    # Minimal CLI for direct test (replace with argparse if needed)
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