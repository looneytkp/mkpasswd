#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import time
import textwrap

try:
    import requests
except ImportError:
    print("[X] Missing 'requests' library. Please install it with 'pip install requests'.")
    sys.exit(1)

VERSION = "v1.7"
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
LAST_UPDATE_FILE = os.path.join(SYSTEM_DIR, ".last_update_check")
BIN_PATH = os.path.join(HOME, ".local", "bin", "vaultpass")

def make_centered_banner(version=VERSION):
    width = 37
    line1 = "🔑  VAULTPASS  🔒"
    line2 = f"Secure Password Manager {version}"
    def pad(s):
        total = width - 2 - len(s)
        left = total // 2
        right = total - left
        return " " * left + s + " " * right
    top = "╔" + "═" * (width - 2) + "╗"
    mid1 = "║" + pad(line1) + "║"
    mid2 = "║" + pad(line2) + "║"
    bot = "╚" + "═" * (width - 2) + "╝"
    return "\n".join([top, mid1, mid2, bot])

banner = make_centered_banner()

def log_action(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def require_passphrase_setup():
    if not os.path.exists(HINT_FILE):
        print("[*] First run: You must set a master passphrase.")
        print("  - This passphrase protects all your saved passwords.")
        print("  - If you forget it, your passwords cannot be recovered.")
        hint = read_input_with_abort("[*] Enter a passphrase hint (for your eyes only, can be blank): ")
        os.makedirs(SYSTEM_DIR, exist_ok=True)
        with open(HINT_FILE, "w") as f:
            f.write(hint)
        log_action("Set passphrase hint")
        print("[*] Passphrase hint saved.")
    if os.path.exists(HINT_FILE):
        with open(HINT_FILE) as f:
            print("💡 Hint:", f.read().strip())

# --------- ESC-ABORT INPUT HANDLER ---------
def read_input_with_abort(prompt):
    print(prompt, end="", flush=True)
    try:
        # Unix
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            chars = []
            while True:
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    print("\n[✓] Vaultpass aborted")
                    sys.exit(0)
                elif ch in ["\r", "\n"]:
                    print()
                    return "".join(chars)
                else:
                    print(ch, end="", flush=True)
                    chars.append(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except ImportError:
        # Windows
        import msvcrt
        chars = []
        while True:
            ch = msvcrt.getch()
            if ch == b"\x1b":
                print("\n[✓] Vaultpass aborted")
                sys.exit(0)
            elif ch in [b"\r", b"\n"]:
                print()
                return b"".join(chars).decode()
            else:
                print(ch.decode(), end="", flush=True)
                chars.append(ch)

# --------- USERNAME/EMAIL REQUIRED ---------
def prompt_username_email(ID):
    tries = 0
    while tries < 3:
        user = read_input_with_abort(f"[?] Username/email for {ID}: ")
        if user.strip():
            return user
        tries += 1
        if tries < 3:
            print("[!] Can't save a password without an ID.")
        else:
            print("[X] Abort")
            sys.exit(1)

def get_latest_changelog(changelog_file, version):
    try:
        with open(changelog_file, "r") as f:
            lines = f.readlines()
    except Exception:
        return []
    target = f"Version {version.lstrip('v')}"
    start, out = False, []
    for line in lines:
        if line.strip().startswith("Version "):
            if start: break
            start = line.strip().startswith(target)
            continue
        if start:
            if line.strip():
                out.append(line.strip(" \n"))
    return out

def print_changelog_box(version, lines, width=41):
    print("   ┌" + "─" * width + "┐")
    title = f"Vaultpass {version}:"
    print(f"   │ {title.ljust(width)}│")
    for line in lines:
        msg = line.lstrip("- ").capitalize()
        wrapped = textwrap.wrap(msg, width=width-2)
        if wrapped:
            print(f"   │ - {wrapped[0].ljust(width-2)}│")
            for cont in wrapped[1:]:
                print(f"   │   {cont.ljust(width-2)}│")
    print("   └" + "─" * width + "┘")

def show_changelog(version=VERSION):
    print("\n" + banner + "\n")
    lines = get_latest_changelog(CHANGELOG_FILE, version)
    if not lines:
        print("[!] No changelog found.")
        return
    print_changelog_box(version, lines)
    print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass")

def show_features():
    print("\n" + banner + "\n")
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
    print("\n" + banner + "\n")
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
    chosen = read_input_with_abort("[?] Enter backup filename to restore: ").strip()
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
            new_user = prompt_username_email(entry_id)
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
            new1 = read_input_with_abort("[?] Set new passphrase: ")
            new2 = read_input_with_abort("[?] Verify new passphrase: ")
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
    print("\n" + banner + "\n")
    confirm = read_input_with_abort("[?] Uninstall Vaultpass? (Y/n): ").strip().lower()
    if confirm in ("y", ""):
        shutil.rmtree(INSTALL_DIR, ignore_errors=True)
        bin_file = os.path.join(HOME, ".local", "bin", "vaultpass")
        if os.path.exists(bin_file):
            os.remove(bin_file)
        print("[✓] Vaultpass is uninstalled.")
    else:
        print("[!] Uninstall cancelled.")

def check_for_updates(force=False):
    now = int(time.time())
    need_update = False
    if force:
        need_update = True
    elif os.path.exists(LAST_UPDATE_FILE):
        last = int(os.path.getmtime(LAST_UPDATE_FILE))
        diff_days = (now - last) // 86400
        if diff_days >= 3:
            need_update = True
    else:
        need_update = True

    if not need_update:
        return

    print("[*] Checking for Vaultpass updates...")

    # Read local version
    try:
        with open(VERSION_FILE) as f:
            local_version = f.read().strip()
    except FileNotFoundError:
        local_version = "unknown"

    # Get remote version
    try:
        r = requests.get(REMOTE_VERSION_URL, timeout=5)
        r.raise_for_status()
        remote_version = r.text.strip()
    except Exception:
        print("[X] Could not fetch remote version info.")
        open(LAST_UPDATE_FILE, "a").close()
        return

    # Major update (version change)
    if local_version != remote_version:
        print(f"[!] Latest: {remote_version}")
        print("[*] Changelog for latest version:\n")
        lines = get_latest_changelog(CHANGELOG_FILE, remote_version)
        print_changelog_box(remote_version, lines)
        print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass")
        update = read_input_with_abort("[?] Do you want to update now? (Y/n): ").strip().lower()
        if update in ("y", ""):
            print("[*] Updating Vaultpass…")
            rc = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=INSTALL_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if rc.returncode == 0:
                with open(VERSION_FILE, "w") as f:
                    f.write(remote_version)
                shutil.copy2(os.path.join(CORE_DIR, "vaultpass.py"), BIN_PATH)
                os.chmod(BIN_PATH, 0o755)
                print(f"[✓] Vaultpass updated to {remote_version}.")
            else:
                print("[X] Failed to update Vaultpass.")
        open(LAST_UPDATE_FILE, "a").close()
        return
    else:
        # Minor updates: compare git commit hashes
        try:
            local_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=INSTALL_DIR, text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            subprocess.run(
                ["git", "fetch", "origin", "main"],
                cwd=INSTALL_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            remote_commit = subprocess.check_output(
                ["git", "rev-parse", "origin/main"], cwd=INSTALL_DIR, text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            print("[✓] Vaultpass is up to date.")
            open(LAST_UPDATE_FILE, "a").close()
            return

        if local_commit != remote_commit:
            try:
                remote_msg = subprocess.check_output(
                    ["git", "log", "-1", "--pretty=%B", "origin/main"],
                    cwd=INSTALL_DIR, text=True,
                    stderr=subprocess.DEVNULL
                ).splitlines()[0]
            except Exception:
                remote_msg = "(minor update)"
            print(f"[!] Minor updates available: {remote_msg}")
            update = read_input_with_abort("[?] Update? (Y/n): ").strip().lower()
            if update in ("y", ""):
                print("[*] Updating Vaultpass…")
                rc = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=INSTALL_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if rc.returncode == 0:
                    shutil.copy2(os.path.join(CORE_DIR, "vaultpass.py"), BIN_PATH)
                    os.chmod(BIN_PATH, 0o755)
                    print("[✓] Vaultpass updated with small changes.")
                else:
                    print("[X] Failed to update Vaultpass.")
        else:
            print("[✓] Vaultpass is up to date.")
    open(LAST_UPDATE_FILE, "a").close()

def show_help():
    print("\n" + banner + "\n")
    print("""Usage: vaultpass [OPTIONS]
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

def generate_password(length):
    import random
    import string
    chars = string.ascii_letters + string.digits + '!@#$%^&*_+-='
    while True:
        password = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*_+-=' for c in password)):
            return password

def save_password(ID, password, user, info):
    require_passphrase_setup()
    subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
    with open(f"{PASS_FILE}.tmp", "a") as f:
        f.write(f"{ID}:|{user}|{password}|{info}\n")
    subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
    os.remove(f"{PASS_FILE}.tmp")
    print(f"[✓] Saved password for {ID}.")
    log_action(f"Saved password for {ID}")

def main():
    # 3-day auto update check, unless --update
    if "--update" not in sys.argv:
        check_for_updates()

    # Simple manual flag parsing to keep old style behavior
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        show_help()
        return
    if argv[0] in ("-a", "--about"):
    show_features()
        return
    if argv[0] == "--changelog":
        show_changelog()
        return
    if argv[0] == "--log":
        show_log()
        return
    if argv[0] == "--update":
        check_for_updates(force=True)
        return
    if argv[0] in ("-b", "--backup"):
        backup_passwords()
        return
    if argv[0] in ("-r", "--restore"):
        restore_passwords()
        return
    if argv[0] in ("-u", "--uninstall"):
        uninstall()
        return
    if argv[0] in ("--change-passphrase",):
        change_passphrase()
        return
    if argv[0] in ("-e", "--edit"):
        if len(argv) < 2:
            print("[X] Usage: vaultpass -e ID")
            return
        edit_entry(argv[1])
        return
    if argv[0] in ("-L", "--list"):
        require_passphrase_setup()
        subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
        with open(f"{PASS_FILE}.tmp") as f:
            for line in f:
                print("[✓]", line.strip())
        os.remove(f"{PASS_FILE}.tmp")
        log_action("Listed all passwords")
        return
    if argv[0] in ("-S", "--search"):
        require_passphrase_setup()
        if len(argv) < 2:
            print("[X] Usage: vaultpass -S ID [ID2 ...]")
            return
        for ID in argv[1:]:
            subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
            found = False
            with open(f"{PASS_FILE}.tmp") as f:
                for line in f:
                    if line.startswith(f"{ID}:"):
                        print("[✓]", line.strip())
                        found = True
                        break
            os.remove(f"{PASS_FILE}.tmp")
            if not found:
                print(f"[X] ID {ID} not found")
            log_action(f"Searched for {ID}")
        return
    if argv[0] in ("-d", "--delete"):
        require_passphrase_setup()
        if len(argv) < 2:
            print("[X] Usage: vaultpass -d ID [ID2 ...]")
            return
        for ID in argv[1:]:
            subprocess.run(["python3", VAULT_PY, "decrypt", PASS_FILE, f"{PASS_FILE}.tmp"])
            lines = []
            deleted = False
            with open(f"{PASS_FILE}.tmp") as f:
                for line in f:
                    if line.startswith(f"{ID}:"):
                        deleted = True
                    else:
                        lines.append(line)
            with open(f"{PASS_FILE}.tmp", "w") as f:
                f.writelines(lines)
            subprocess.run(["python3", VAULT_PY, "encrypt", f"{PASS_FILE}.tmp", PASS_FILE])
            os.remove(f"{PASS_FILE}.tmp")
            if deleted:
                print(f"[✓] Deleted {ID}.")
                log_action(f"Deleted {ID}")
            else:
                print(f"[X] ID {ID} not found")
        return

    # Password generation logic (long/short/custom)
    if argv[0] in ("-l", "--long", "-s", "--short", "-c", "--custom"):
        mode = argv[0]
        IDs = argv[1:]
        if not IDs:
            print(f"[X] Usage: vaultpass {mode} ID [ID2 ...]")
            return
        for ID in IDs:
            if mode in ("-l", "--long"):
                password = generate_password(16)
            elif mode in ("-s", "--short"):
                password = generate_password(8)
            else:
                # Custom mode: ask user to enter password
                password = read_input_with_abort(f"[?] Password for {ID}: ")
            if mode != "-c" and mode != "--custom":
                print(f"[?] Password for {ID}: {password}")

            # Username/email (required, up to 3 tries, esc-abort possible)
            user = None
            tries = 0
            while tries < 3:
                user = read_input_with_abort(f"[?] Username/email for {ID}: ")
                if user.strip():
                    break
                tries += 1
                if tries < 3:
                    print("[!] Can't save a password without an ID.")
                else:
                    print("[X] Abort")
                    sys.exit(1)
            # Optional info
            info = read_input_with_abort(f"[?] Info [Optional]: ")
            save_password(ID, password, user, info)
        return

    # If nothing matches, show help
    show_help()

if __name__ == "__main__":
    main()