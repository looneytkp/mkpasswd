import os
import sys
import time
import shutil
import getpass
import hashlib

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CONFIG_FILE = os.path.join(INSTALL_DIR, ".config")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
HASH_FILE = os.path.join(SYSTEM_DIR, "passphrase_hash.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")

DEFAULT_CONFIG = "encryption=on\npassphrase_set=no\ntheme=light\n"

def ensure_config_and_heal():
    """Heal .config if missing or out of sync with passphrase_hash.txt."""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            f.write(DEFAULT_CONFIG)
    config = {}
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                config[k] = v
    # Healing: If hash exists but config disagrees, fix config
    if os.path.exists(HASH_FILE):
        changed = False
        if config.get('encryption') != 'on':
            config['encryption'] = 'on'
            changed = True
        if config.get('passphrase_set') != 'yes':
            config['passphrase_set'] = 'yes'
            changed = True
        if changed:
            with open(CONFIG_FILE, "w") as f:
                for k, v in config.items():
                    f.write(f"{k}={v}\n")

def load_config():
    ensure_config_and_heal()
    config = {}
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                config[k] = v
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

def log_action(msg):
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def hash_passphrase(passphrase):
    return hashlib.sha256(passphrase.encode()).hexdigest()

def require_passphrase_setup():
    from cli import show_banner  # local import to avoid circular

    show_banner()
    config = load_config()
    enc_state = config.get('encryption', 'off')
    passphrase_state = config.get('passphrase_set', 'no')

    # 1. No encryption requested (by config)
    if enc_state == "off" or passphrase_state == "no":
        print("[!] No encryption enabled. Proceeding without passphrase.")
        return False

    # 2. Passphrase not set yet, prompt for setup
    if not os.path.isfile(HASH_FILE):
        print("[!] You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        passphrase = getpass.getpass("[*] Enter a passphrase [Leave blank for NO Encryption]: ")
        if passphrase == "":
            print("Passphrase not set, passwords won't be encrypted")
            # Update config file
            config['encryption'] = "off"
            config['passphrase_set'] = "no"
            save_config(config)
            if os.path.exists(HINT_FILE): os.remove(HINT_FILE)
            if os.path.exists(HASH_FILE): os.remove(HASH_FILE)
            return False  # Proceed unencrypted
        confirm = getpass.getpass("[*] Confirm passphrase: ")
        if passphrase != confirm:
            print("[X] Passphrases do not match.")
            sys.exit(1)
        # Save passphrase hash and update config
        with open(HASH_FILE, "w") as f:
            f.write(hash_passphrase(passphrase))
        hint = input("[*] Enter a passphrase hint (optional): ").strip()
        with open(HINT_FILE, "w") as f:
            f.write(hint)
        log_action("Set master passphrase and hint")
        config['encryption'] = "on"
        config['passphrase_set'] = "yes"
        save_config(config)
        print("[*] Passphrase and hint saved.")
        return True

    # 3. Passphrase is set, show hint, prompt for passphrase
    hint = ""
    if os.path.isfile(HINT_FILE):
        with open(HINT_FILE) as f:
            hint = f.read().strip()
        if hint:
            print("💡 Hint:", hint)
    with open(HASH_FILE) as f:
        saved_hash = f.read().strip()
    passphrase = getpass.getpass("[*] Enter your master passphrase: ")
    if hash_passphrase(passphrase) == saved_hash:
        return True
    else:
        print("[X] Incorrect passphrase.")
        sys.exit(1)

def list_entries():
    if require_passphrase_setup() is False:
        pass  # Proceed unencrypted
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        for line in f:
            print("[✓]", line.strip())
    log_action("Listed all passwords")

def add_entry(id, user="", pwd="", info=""):
    if require_passphrase_setup() is False:
        pass
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    line = f"{id}:|{user}|{pwd}|{info}\n"
    with open(PASS_FILE, "a") as f:
        f.write(line)
    print(f"[✓] Saved password for {id}.")
    log_action(f"Saved password for {id}")

def edit_entry(id, new_user):
    if require_passphrase_setup() is False:
        pass
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
    if require_passphrase_setup() is False:
        pass
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
    if require_passphrase_setup() is False:
        pass
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
    if require_passphrase_setup() is False:
        pass
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
    if require_passphrase_setup() is False:
        pass
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