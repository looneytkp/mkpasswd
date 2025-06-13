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

# ------- CLI dispatcher stub (add your logic here!) -------
def run_cli():
    # Placeholder for CLI logic (parsing, action dispatch)
    # You’ll expand this as you modularize.
    pass