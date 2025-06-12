#!/usr/bin/env python3

import os
import sys
import argparse
import shutil
import subprocess
import datetime
import platform

try:
    import requests
except ImportError:
    print("[X] Python 'requests' module is not installed. Please install with 'pip install requests' and re-run.")
    sys.exit(1)

# --- Detect OS and Set Directories ---
IS_WINDOWS = os.name == "nt"
HOME = os.environ.get("USERPROFILE", os.path.expanduser("~")) if IS_WINDOWS else os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")
LOG_FILE = os.path.join(SYSTEM_DIR, "vaultpass.log")
CHANGELOG_FILE = os.path.abspath(os.path.join(CORE_DIR, "..", "changelog.txt"))
VERSION_FILE = os.path.abspath(os.path.join(CORE_DIR, "..", "version.txt"))
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"
LAST_UPDATE_FILE = os.path.join(SYSTEM_DIR, ".last_update_check")
VAULT_PY = os.path.join(CORE_DIR, "vault.py")
PASSGEN_PY = os.path.join(CORE_DIR, "password_gen.py")

# Windows: Main launcher is 'vaultpass.py' in .local/bin
BIN_DIR = os.path.join(HOME, ".local", "bin")
LAUNCHER = "vaultpass.py" if IS_WINDOWS else "vaultpass"
LOCAL_BIN = os.path.join(BIN_DIR, LAUNCHER)

# --- Use system python for subprocesses ---
def get_python_exec():
    return sys.executable or "python3"

PYTHON_EXEC = get_python_exec()

# --- Version detection ---
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
    if not os.path.exists(CHANGELOG_FILE):
        print("[X] Changelog file not found.")
        return
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
                # Only run git if .git exists
                repo_dir = os.path.abspath(os.path.join(CORE_DIR, ".."))
                if os.path.isdir(os.path.join(repo_dir, ".git")):
                    subprocess.run(["git", "pull", "origin", "main"], cwd=repo_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with open(VERSION_FILE, "w") as f:
                    f.write(remote_version)
                print(f"[✓] Vaultpass updated to {remote_version}.")
                log_action(f"Vaultpass updated to {remote_version}")
        else:
            # Minor updates (same version, new commit)
            try:
                repo_dir = os.path.abspath(os.path.join(CORE_DIR, ".."))
                local_commit = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=repo_dir).decode().strip()
                subprocess.run(["git", "fetch", "origin", "main"], cwd=repo_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                remote_commit = subprocess.check_output(
                    ["git", "rev-parse", "origin/main"], cwd=repo_dir).decode().strip()
            except Exception:
                local_commit, remote_commit = "", ""
            if local_commit and remote_commit and local_commit != remote_commit:
                try:
                    msg = subprocess.check_output(
                        ["git", "log", "-1", "--pretty=%B", "origin/main"], cwd=repo_dir).decode().splitlines()[0]
                except Exception:
                    msg = "No commit message"
                print(f"[!] Minor updates available: {msg}")
                u = input("[?] Update? (Y/n): ")
                if u.strip().lower() in ("y", ""):
                    print("[*] Updating Vaultpass…")
                    subprocess.run(["git", "pull", "origin", "main"], cwd=repo_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("[✓] Vaultpass updated to latest code (version unchanged).")
                    log_action("Vaultpass minor update")
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
    if IS_WINDOWS:
        print(f"[i] On Windows, Vaultpass is installed at: {INSTALL_DIR}")
        print(f"[i] The CLI launcher is at: {LOCAL_BIN}")
        print(f"[i] If you want to add the CLI to your PATH, add '{BIN_DIR}' to your system PATH environment variable.")

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
    if os.path.exists(PASS_FILE):
        shutil.copy(PASS_FILE, backup_file)
    if os.path.exists(HINT_FILE):
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
    subprocess.run([PYTHON_EXEC, VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
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
        subprocess.run([PYTHON_EXEC, VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        print(f"[✓] Username/email updated for {entry_id}.")
        log_action(f"Edited entry for {entry_id}")
    else:
        print("[X] ID not found")
        os.remove(f"{PASS_FILE}.tmp")

def change_passphrase():
    require_passphrase_setup()
    print("[?] To change passphrase, enter current passphrase: ")
    r = subprocess.run([PYTHON_EXEC, VAULT_PY, "verify", PASS_FILE])
    if r.returncode == 0:
        print("[✓] Verified.")
        while True:
            new1 = input("[?] Set new passphrase: ")
            new2 = input("[?] Verify new passphrase: ")
            if new1 == new2:
                # Pipe new passphrase to change_passphrase
                p = subprocess.Popen(
                    [PYTHON_EXEC, VAULT_PY, "change_passphrase", PASS_FILE],
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
        # Remove all files and directories
        try:
            shutil.rmtree(INSTALL_DIR, ignore_errors=True)
            if os.path.exists(LOCAL_BIN):
                os.remove(LOCAL_BIN)
        except Exception as e:
            print(f"[X] Failed to remove install directory: {e}")
        # Clean PATH export (optional: print message for Windows)
        if not IS_WINDOWS:
            rc_files = [os.path.expanduser("~/.bashrc"), os.path.expanduser("~/.zshrc"), os.path.expanduser("~/.bash_profile")]
            for rc_file in rc_files:
                if os.path.isfile(rc_file):
                    with open(rc_file, "r") as f:
                        lines = f.readlines()
                    filtered = [line for line in lines if ".local/bin" not in line or "export PATH" not in line]
                    if len(filtered) != len(lines):
                        with open(rc_file, "w") as f:
                            f.writelines(filtered)
        print("[✓] Vaultpass uninstalled.")
        if IS_WINDOWS:
            print(f"[i] Please also remove '{BIN_DIR}' from your system PATH if you wish.")
    else:
        print("[!] Uninstall cancelled.")

def list_passwords():
    require_passphrase_setup()
    subprocess.run([PYTHON_EXEC, VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
    with open(f"{PASS_FILE}.tmp") as f:
        for line in f:
            print(f"[✓] {line.strip()}")
    os.remove(f"{PASS_FILE}.tmp")
    log_action("Listed all passwords")

def search_passwords(ids):
    require_passphrase_setup()
    for entry_id in ids:
        subprocess.run([PYTHON_EXEC, VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
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
        subprocess.run([PYTHON_EXEC, VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp") as f:
            lines = [line for line in f if not line.startswith(f"{entry_id}:")]
        with open(f"{PASS_FILE}.tmp2", "w") as f:
            f.writelines(lines)
        subprocess.run([PYTHON_EXEC, VAULT_PY, "encrypt", f"{PASS_FILE}.tmp2", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        os.remove(f"{PASS_FILE}.tmp2")
        print(f"[✓] Deleted {entry_id}.")
        log_action(f"Deleted {entry_id}")

def generate_passwords(ids, mode):
    require_passphrase_setup()
    for entry_id in ids:
        pwd = subprocess.check_output([PYTHON_EXEC, PASSGEN_PY, mode]).decode().strip()
        print(f"[?] Password for {entry_id}: {pwd}")
        user = input(f"[?] Enter username/email for {entry_id} (optional): ")
        info = input(f"[?] Add info/description for {entry_id} (optional): ")
        subprocess.run([PYTHON_EXEC, VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp", "a") as f:
            f.write(f"{entry_id}:|{user}|{pwd}|{info}\n")
        subprocess.run([PYTHON_EXEC, VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        print(f"[✓] Saved password for {entry_id}.")
        log_action(f"Saved password for {entry_id}")

def save_custom_passwords(ids):
    require_passphrase_setup()
    for entry_id in ids:
        pwd = input(f"[?] Enter password for {entry_id}: ")
        user = input(f"[?] Enter username/email for {entry_id} (optional): ")
        info = input(f"[?] Add info/description for {entry_id} (optional): ")
        subprocess.run([PYTHON_EXEC, VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp", "a") as f:
            f.write(f"{entry_id}:|{user}|{pwd}|{info}\n")
        subprocess.run([PYTHON_EXEC, VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
        os.remove(f"{PASS_FILE}.tmp")
        print(f"[✓] Saved custom password for {entry_id}.")
        log_action(f"Saved custom password for {entry_id}")

def main():
    parser = argparse.ArgumentParser(
        description=f"Vaultpass - Secure Password Manager {VERSION}",
        formatter_class=argparse.RawText