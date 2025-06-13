import sys
import textwrap

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
  [ID USER PASS INFO]              Add a new entry
  -L, --list                       List all saved entries
  -S, --search [ID]                Search for entry by ID
  -d, --delete [ID]                Delete entry by ID
  -e, --edit [ID USER]             Edit username/email
  -b, --backup                     Backup vault
  -r, --restore [FILENAME]         Restore vault from backup
  -h, --help                       Show this help

Examples:
  vaultpass gmail me@mail.com password123 "my gmail"
  vaultpass -L
""")

def run_cli():
    import vault
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        show_help()
        return

    # Add entry: only if called with exactly 4 args, and first arg does not look like a flag
    if len(args) == 4 and not args[0].startswith("-"):
        id, user, pwd, info = args
        vault.add_entry(id, user, pwd, info)
        return

    cmd = args[0]

    if cmd in ("-L", "--list"):
        vault.list_entries()
        return

    elif cmd in ("-S", "--search"):
        if len(args) >= 2:
            vault.search_entry(args[1])
        else:
            print("[!] Usage: vaultpass -S ID")
        return

    elif cmd in ("-d", "--delete"):
        if len(args) >= 2:
            vault.delete_entry(args[1])
        else:
            print("[!] Usage: vaultpass -d ID")
        return

    elif cmd in ("-e", "--edit"):
        if len(args) >= 3:
            vault.edit_entry(args[1], args[2])
        else:
            print("[!] Usage: vaultpass -e ID NEWUSER")
        return

    elif cmd in ("-b", "--backup"):
        vault.backup_vault()
        return

    elif cmd in ("-r", "--restore"):
        if len(args) >= 2:
            vault.restore_vault(args[1])
        else:
            print("[!] Usage: vaultpass -r BACKUP_FILENAME")
        return

    else:
        show_help()
        return