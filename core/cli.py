import sys
import textwrap

# -------- Banner generator --------
def make_centered_banner(_=None):
    """Return ASCII banner string for Vaultpass (centered)."""
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
    """Print the Vaultpass banner."""
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
    """Show banner, changelog box, and link."""
    show_banner()
    if not lines:
        print("[!] No changelog found for this version.")
        return
    print_changelog_box(version, lines)
    print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass\n")

# ------- CLI dispatcher -------
def run_cli():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        show_help()
    elif args[0] in ("-a", "--about"):
        show_features()
    elif args[0] in ("--changelog",):
        show_banner()
        print("Changelog coming soon!\n")
    elif args[0] in ("--log",):
        show_banner()
        print("Log viewer coming soon!\n")
    elif args[0] in ("--update",):
        show_banner()
        print("Update checker coming soon!\n")
    elif args[0] in ("-b", "--backup"):
        show_banner()
        print("Backup feature coming soon!\n")
    elif args[0] in ("-r", "--restore"):
        show_banner()
        print("Restore feature coming soon!\n")
    elif args[0] in ("-L", "--list"):
        show_banner()
        print("Password listing coming soon!\n")
    elif args[0] in ("-S", "--search"):
        show_banner()
        print("Password search coming soon!\n")
    elif args[0] in ("-l", "--long"):
        show_banner()
        print("Long password generation coming soon!\n")
    elif args[0] in ("-s", "--short"):
        show_banner()
        print("Short password generation coming soon!\n")
    elif args[0] in ("-c", "--custom"):
        show_banner()
        print("Custom password saving coming soon!\n")
    elif args[0] in ("-d", "--delete"):
        show_banner()
        print("Password delete coming soon!\n")
    elif args[0] in ("-e", "--edit"):
        show_banner()
        print("Edit entry coming soon!\n")
    elif args[0] in ("--change-passphrase",):
        show_banner()
        print("Passphrase change coming soon!\n")
    elif args[0] in ("-u", "--uninstall"):
        show_banner()
        print("Uninstall feature coming soon!\n")
    else:
        show_banner()
        print(f"[X] Unknown option: {args[0]}\nRun 'vaultpass -h' for help.\n")