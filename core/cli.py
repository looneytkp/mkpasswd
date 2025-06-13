import sys
import textwrap
import vault
import password_gen
import update
import subprocess
import os

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

def show_help(version=None):
    show_banner()
    print("""Usage: vaultpass [OPTIONS]
Options:
  -l, --long [ID ...]        Generate long password(s)
  -s, --short [ID ...]       Generate short password(s)
  -c, --custom [ID ...]      Save custom password(s)
  -L, --list                 List all saved passwords
  -S, --search [ID ...]      Search for passwords by ID
  -f, --find [ID ...]        Alias for search
  -d, --delete [ID ...]      Delete password(s) by ID
  -e, --edit [ID]            Edit username/email
  -b, --backup               Backup passwords
  -r, --restore [filename]   Restore from backup
  -u, --update               Check for updates
  -U, --uninstall            Uninstall Vaultpass
  -h, --help                 Show this help
""")

def run_cli():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        show_help()
        return

    elif args[0] in ("-l", "--long"):
        if len(args) > 1:
            for save_id in args[1:]:
                info = input(f"[*] Optional info/description for {save_id} (leave blank to skip): ").strip()
                pwd = password_gen.generate_password(16)
                vault.add_entry(save_id, pwd=pwd, info=info)
                print(f"[✓] Generated & saved long password for {save_id}: {pwd}")
        else:
            print("[!] Please provide an ID.")
        return

    elif args[0] in ("-s", "--short"):
        if len(args) > 1:
            for save_id in args[1:]:
                info = input(f"[*] Optional info/description for {save_id} (leave blank to skip): ").strip()
                pwd = password_gen.generate_password(8)
                vault.add_entry(save_id, pwd=pwd, info=info)
                print(f"[✓] Generated & saved short password for {save_id}: {pwd}")
        else:
            print("[!] Please provide an ID.")
        return

    elif args[0] in ("-c", "--custom"):
        if len(args) > 1:
            for save_id in args[1:]:
                user_pwd = input(f"[*] Enter custom password for {save_id}: ")
                info = input(f"[*] Optional info/description for {save_id} (leave blank to skip): ").strip()
                vault.add_entry(save_id, pwd=user_pwd, info=info)
                print(f"[✓] Custom password saved for {save_id}.")
        else:
            print("[!] Please provide an ID.")
        return

    elif args[0] in ("-L", "--list"):
        vault.list_entries()
        return

    elif args[0] in ("-S", "--search", "-f", "--find"):
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

    elif args[0] in ("-u", "--update"):
        update.manual_check()
        return

    elif args[0] in ("-U", "--uninstall"):
        uninstall_path = os.path.expanduser("~/.vaultpass/install/uninstall.py")
        if os.path.isfile(uninstall_path):
            subprocess.run(["python3", uninstall_path])
        else:
            print("[X] uninstall.py not found.")
        return

    else:
        show_help()
        return