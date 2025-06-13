import os
import sys
import time
import shutil
import getpass
import hashlib
from banner_utils import show_banner

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CONFIG_FILE = os.path.join(INSTALL_DIR, ".config")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
HASH_FILE = os.path.join(SYSTEM_DIR, "passphrase_hash.txt")

DEFAULT_CONFIG = "encryption=on\npassphrase_set=no\ntheme=light\n"

def load_config():
    config = {}
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            f.write(DEFAULT_CONFIG)
    with open(CONFIG_FILE) as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                config[k] = v
    # Heal missing keys
    for line in DEFAULT_CONFIG.strip().splitlines():
        key = line.split("=")[0]
        if key not in config:
            config[key] = line.split("=")[1]
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

def hash_passphrase(passphrase):
    return hashlib.sha256(passphrase.encode()).hexdigest()

def sanitize(s):
    return s.replace("|", "_").replace("\n", " ").strip()

def require_passphrase_setup():
    from cli import show_banner  # local import to avoid circular

    config = load_config()
    enc_state = config.get('encryption', 'off')
    passphrase_state = config.get('passphrase_set', 'no')

    if enc_state == "off":
        print("[!] No encryption enabled. Proceeding without passphrase.")
        return False

    # If encryption is ON, but passphrase isn't set, prompt!
    if passphrase_state == "no" or not os.path.isfile(HASH_FILE):
        show_banner()
        print("[!] You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        passphrase = getpass.getpass("[*] Enter a passphrase [Leave blank for NO Encryption]: ")
        if passphrase == "":
            print("Passphrase not set, passwords won't be encrypted")
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
        config['encryption'] = "on"
        config['passphrase_set'] = "yes"
        save_config(config)
        print("[*] Passphrase and hint saved.")
        return True

    # Existing passphrase
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

def _read_pass_lines():
    if not os.path.isfile(PASS_FILE):
        return []
    with open(PASS_FILE) as f:
        return f.readlines()

def _write_pass_lines(lines):
    with open(PASS_FILE, "w") as f:
        f.writelines(lines)

def handle_duplicate_id(save_id):
    # Check if ID exists and prompt for action
    lines = _read_pass_lines()
    id_found = any(line.startswith(f"{save_id}:") for line in lines)
    if not id_found:
        return None
    while True:
        resp = input(f"[!] ID '{save_id}' already exists. [O]verwrite, [A]ppend, [C]ancel? (o/a/c): ").strip().lower()
        if resp == "o":
            # Overwrite: remove old entry
            _write_pass_lines([line for line in lines if not line.startswith(f"{save_id}:")])
            return save_id
        elif resp == "a":
            # Append: find next available suffix
            count = 2
            existing_ids = [line.split(":")[0] for line in lines]
            new_id = f"{save_id}_{count}"
            while new_id in existing_ids:
                count += 1
                new_id = f"{save_id}_{count}"
            print(f"[*] Saving as {new_id}")
            return new_id
        elif resp == "c":
            print("[!] Cancelled.")
            sys.exit(0)
        else:
            print("[!] Invalid option.")

def list_entries():
    require_passphrase_setup()
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    with open(PASS_FILE) as f:
        for line in f:
            print("[✓]", line.strip())

def add_entry(id, user="", pwd="", info=""):
    require_passphrase_setup()
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    id = sanitize(id)
    user = sanitize(user)
    info = sanitize(info)
    if info:
        line = f"{id}:|{user}|{pwd}|{info}\n"
    else:
        line = f"{id}:|{user}|{pwd}\n"
    with open(PASS_FILE, "a") as f:
        f.write(line)
    print(f"[✓] Saved password for {id}.")

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
        _write_pass_lines(new_lines)
        print(f"[✓] Username/email updated for {id}.")
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
        _write_pass_lines(new_lines)
        print(f"[✓] Deleted {id}.")
    else:
        print("[X] ID not found.")

def search_entry(id):
    require_passphrase_setup()
    if not os.path.isfile(PASS_FILE):
        print("[!] No vault found.")
        return
    found = False
    with open(PASS_FILE) as f:
        for line in f:
            if line.startswith(f"{id}:"):
                print("[✓]", line.strip())
                found = True
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