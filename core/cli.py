import os
import sys
import vault
import password_gen
from banner_utils import show_banner

def show_help(version=None):
    show_banner()
    print("""Usage: vaultpass [OPTIONS]
Options:
  -l, --long [ID ...]        Generate long password(s)
  -s, --short [ID ...]       Generate short password(s)
  -c, --custom [ID ...]      Save custom password(s)
  -L, --list                 List all saved passwords
  -f, --find [ID ...]        Search for passwords by ID
  -d, --delete [ID ...]      Delete password(s) by ID
  -e, --edit [ID]            Edit username/email
  -b, --backup               Backup passwords
  -r, --restore [filename]   Restore from backup
  -U, --uninstall            Uninstall Vaultpass
  -u, --update               Check for updates
  -h, --help                 Show this help
""")

def run_cli():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        show_help()
        return

    # Password Generation & Save
    elif args[0] in ("-l", "--long"):
        if len(args) > 1:
            for save_id in args[1:]:
                new_id = vault.handle_duplicate_id(save_id) or save_id
                info = input(f"[*] Optional info/description for {new_id} (leave blank to skip): ").strip()
                pwd = password_gen.generate_password(16)
                vault.add_entry(new_id, pwd=pwd, info=info)
                print(f"[✓] Generated & saved long password for {new_id}: {pwd}")
        else:
            print("[!] Please provide an ID.")
        return

    elif args[0] in ("-s", "--short"):
        if len(args) > 1:
            for save_id in args[1:]:
                new_id = vault.handle_duplicate_id(save_id) or save_id
                info = input(f"[*] Optional info/description for {new_id} (leave blank to skip): ").strip()
                pwd = password_gen.generate_password(8)
                vault.add_entry(new_id, pwd=pwd, info=info)
                print(f"[✓] Generated & saved short password for {new_id}: {pwd}")
        else:
            print("[!] Please provide an ID.")
        return

    elif args[0] in ("-c", "--custom"):
        if len(args) > 1:
            for save_id in args[1:]:
                new_id = vault.handle_duplicate_id(save_id) or save_id
                user_pwd = input(f"[*] Enter custom password for {new_id}: ")
                info = input(f"[*] Optional info/description for {new_id} (leave blank to skip): ").strip()
                vault.add_entry(new_id, pwd=user_pwd, info=info)
                print(f"[✓] Custom password saved for {new_id}.")
        else:
            print("[!] Please provide an ID.")
        return

    elif args[0] in ("-L", "--list"):
        vault.list_entries()
        return

    elif args[0] in ("-f", "--find"):
        if len(args) > 1:
            for search_id in args[1:]:
                vault.search_entry(search_id)
        else:
            print("[!] Please provide an ID to search.")
        return

    elif args[0] in ("-d", "--delete"):
        if len(args) > 1:
            for del_id in args[1:]:
                vault.delete_entry(del_id)
        else:
            print("[!] Please provide an ID to delete.")
        return

    elif args[0] in ("-e", "--edit"):
        if len(args) > 1:
            new_user = input(f"[*] Enter new username/email for {args[1]}: ")
            vault.edit_entry(args[1], new_user)
        else:
            print("[!] Please provide an ID to edit.")
        return

    elif args[0] in ("-b", "--backup"):
        vault.backup_vault()
        return

    elif args[0] in ("-r", "--restore"):
        if len(args) > 1:
            vault.restore_vault(args[1])
        else:
            print("[!] Please provide backup filename to restore.")
        return

    elif args[0] in ("-U", "--uninstall"):
        uninstall_path = os.path.expanduser("~/.vaultpass/install/uninstall.py")
        if os.path.exists(uninstall_path):
            import subprocess
            subprocess.run(["python3", uninstall_path])
        else:
            print("[!] Uninstall script not found.")
        return

    elif args[0] in ("-u", "--update"):
        from update import check_for_updates
        HOME = os.path.expanduser("~")
        INSTALL_DIR = os.path.join(HOME, ".vaultpass")
        SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
        VERSION_FILE = os.path.join(SYSTEM_DIR, "version.txt")
        CHANGELOG_FILE = os.path.join(SYSTEM_DIR, "changelog.txt")
        CORE_DIR = os.path.join(INSTALL_DIR, "core")
        BIN_PATH = os.path.join(HOME, ".local", "bin", "vaultpass")
        LAST_UPDATE_FILE = os.path.join(SYSTEM_DIR, ".last_update_check")
        REMOTE_VERSION_URL = "https://raw.githubusercontent.com/looneytkp/vaultpass/main/version.txt"
        check_for_updates(
            current_version=open(VERSION_FILE).read().strip() if os.path.exists(VERSION_FILE) else "0.0.0",
            version_file=VERSION_FILE,
            changelog_file=CHANGELOG_FILE,
            install_dir=INSTALL_DIR,
            core_dir=CORE_DIR,
            bin_path=BIN_PATH,
            last_update_file=LAST_UPDATE_FILE,
            remote_version_url=REMOTE_VERSION_URL
        )
        return

    else:
        show_help()
        return