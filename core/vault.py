# core/vault.py

import os
import shutil
import time

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

def backup_vault():
    require_passphrase_setup()
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"passwords_{timestamp}.gpg")
    shutil.copy2(PASS_FILE, backup_file)
    shutil.copy2(HINT_FILE, os.path.join(BACKUP_DIR, "passphrase_hint.txt"))
    print(f"[✓] Backup saved to {BACKUP_DIR}")
    log_action("Vault backup")

def restore_vault():
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

def list_entries():
    require_passphrase_setup()
    if not os.path.exists(PASS_FILE):
        print("[!] No passwords found.")
        return
    # For now, show as plain text (replace with decrypt logic as needed)
    with open(PASS_FILE) as f:
        for line in f:
            print("[✓]", line.strip())
    log_action("Listed all passwords")

# Add more vault logic (add/edit/delete) here as needed

# The functions above can be imported and used directly from cli.py or vaultpass.py.