# core/cli.py
import sys
import textwrap

# -------- Banner generator --------
def make_centered_banner(_=None):
    width = 37
    line1 = "VAULTPASS"
    line2 = "Secure Password Manager"
    def pad(s):
        total = width - 2 - len(s)
        left = total // 2
        right = total - left
        return " " * left + s + " " * right
    top = "╔" + "═" * (width - 2) + "╗"
    mid1 = "║" + pad(line1) + "║"
    mid2 = "║" + pad(line2) + "║"
    bot = "╚" + "═" * (width - 2) + "╝"
    return "\n" + "\n".join([top, mid1, mid2, bot]) + "\n"

def show_banner(version=None):
    print(make_centered_banner())

# -------- Help/usage --------
def show_help(version=None):
    show_banner()
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

# -------- About/features --------
def show_features(version=None):
    show_banner()
    print("""
Vaultpass Functions:
- Generate secure passwords (short, long, or custom)
- Save username/email with each password
- Add optional 'info' field (e.g. what the password is for)
- View, search, delete, or edit saved passwords
- Backup and restore encrypted vaults
- More features coming soon

""")

# -------- Changelog box printer --------
def print_changelog_box(version, lines, width=55):
    print("   ┌" + "─" * width + "┐")
    title = f"Vaultpass v{version}:"
    print(f"   │ {title.ljust(width)}│")
    for idx, line in enumerate(lines):
        if idx >= 20:
            print(f"   │ {'[...truncated. See full changelog.]'.ljust(width)}│")
            break
        msg = line.lstrip("- ").capitalize()
        wrapped = textwrap.wrap(msg, width=width-2)
        if wrapped:
            print(f"   │ - {wrapped[0].ljust(width-2)}│")
            for cont in wrapped[1:]:
                print(f"   │   {cont.ljust(width-2)}│")
    print("   └" + "─" * width + "┘")

def show_changelog(version, lines):
    show_banner()
    if not lines:
        print("[!] No changelog found for this version.")
        return
    print_changelog_box(version, lines)
    print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass\n")

# ------- CLI dispatcher (all logic hooked up) -------
def run_cli():
    import vault
    import password_gen
    import changelog
    import update
    import os

    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        show_help()
        return
    elif args[0] in ("-a", "--about"):
        show_features()
        return
    elif args[0] == "--changelog":
        # Get current version
        version = ""
        version_file = os.path.expanduser("~/.vaultpass/system/version.txt")
        if os.path.exists(version_file):
            with open(version_file) as f:
                version = f.read().strip()
        lines = []
        changelog_file = os.path.expanduser("~/.vaultpass/system/changelog.txt")
        if os.path.exists(changelog_file):
            lines = changelog.get_latest_changelog(changelog_file, version)
        show_changelog(version, lines)
        return
    elif args[0] == "--log":
        log_file = os.path.expanduser("~/.vaultpass/system/vaultpass.log")
        if os.path.exists(log_file):
            with open(log_file) as f:
                print(f.read())
        else:
            print("[!] Log file not found.")
        return
    elif args[0] in ("--update",):
        # Manual update check
        version_file = os.path.expanduser("~/.vaultpass/system/version.txt")
        changelog_file = os.path.expanduser("~/.vaultpass/system/changelog.txt")
        install_dir = os.path.expanduser("~/.vaultpass")
        core_dir = os.path.expanduser("~/.vaultpass/core")
        bin_path = os.path.expanduser("~/.local/bin/vaultpass")
        last_update_file = os.path.expanduser("~/.vaultpass/system/.last_update_check")
        remote_version_url = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"
        update.check_for_updates(
            current_version=open(version_file).read().strip() if os.path.exists(version_file) else "0.0.0",
            version_file=version_file,
            changelog_file=changelog_file,
            install_dir=install_dir,
            core_dir=core_dir,
            bin_path=bin_path,
            last_update_file=last_update_file,
            remote_version_url=remote_version_url
        )
        return
    elif args[0] in ("-b", "--backup"):
        vault.backup_passwords()
        return
    elif args[0] in ("-r", "--restore"):
        vault.restore_passwords()
        return
    elif args[0] in ("-L", "--list"):
        vault.list_passwords()
        return
    elif args[0] in ("-S", "--search"):
        if len(args) > 1:
            for search_id in args[1:]:
                vault.search_password(search_id)
        else:
            print("[!] Please provide an ID to search.")
        return
    elif args[0] in ("-d", "--delete"):
        if len(args) > 1:
            for del_id in args[1:]:
                vault.delete_password(del_id)
        else:
            print("[!] Please provide an ID to delete.")
        return
    elif args[0] in ("-e", "--edit"):
        if len(args) > 1:
            vault.edit_entry(args[1])
        else:
            print("[!] Please provide an ID to edit.")
        return
    elif args[0] == "--change-passphrase":
        vault.change_passphrase()
        return
    elif args[0] in ("-l", "--long"):
        if len(args) > 1:
            for save_id in args[1:]:
                vault.generate_and_save_password(save_id, length="long")
        else:
            print("[!] Please provide an ID.")
        return
    elif args[0] in ("-s", "--short"):
        if len(args) > 1:
            for save_id in args[1:]:
                vault.generate_and_save_password(save_id, length="short")
        else:
            print("[!] Please provide an ID.")
        return
    elif args[0] in ("-c", "--custom"):
        if len(args) > 1:
            for save_id in args[1:]:
                vault.save_custom_password(save_id)
        else:
            print("[!] Please provide an ID.")
        return
    elif args[0] in ("-u", "--uninstall"):
        uninstall_path = os.path.expanduser("~/.vaultpass/install/uninstall.py")
        if os.path.exists(uninstall_path):
            import subprocess
            subprocess.run(["python3", uninstall_path])
        else:
            print("[!] Uninstall script not found.")
        return
    else:
        show_help()
        return