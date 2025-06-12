#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil

REPO_URL = "https://github.com/looneytkp/vaultpass.git"
INSTALL_DIR = os.path.expanduser("~/.vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
BIN_DIR = os.path.expanduser("~/.local/bin")
LAUNCHER = "vaultpass"
LOCAL_BIN = os.path.join(BIN_DIR, LAUNCHER)
INSTALL_SCRIPTS_DIR = os.path.join(INSTALL_DIR, "install")

def run_quiet(cmd, cwd=None):
    subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("[*] Installing Vaultpass...")

    # Clone or update repo
    if os.path.isdir(os.path.join(INSTALL_DIR, ".git")):
        print("[*] Updating Vaultpass...")
        run_quiet(f"git pull origin main", cwd=INSTALL_DIR)
    else:
        print("[*] Installing Vaultpass...")
        run_quiet(f"git clone {REPO_URL} {INSTALL_DIR}")

    # Create necessary folders
    for d in [CORE_DIR, SYSTEM_DIR, BACKUP_DIR, BIN_DIR, INSTALL_SCRIPTS_DIR]:
        os.makedirs(d, exist_ok=True)

    # Ensure core scripts are in place
    if not (os.path.isfile(os.path.join(CORE_DIR, "vault.py")) and
            os.path.isfile(os.path.join(CORE_DIR, "password_gen.py")) and
            os.path.isfile(os.path.join(CORE_DIR, "vaultpass.py"))):
        print("[X] Missing core scripts. Please check the repository.")
        sys.exit(1)

    # Ensure uninstall.sh is always present
    src_uninstall = None
    if os.path.isfile(os.path.join(INSTALL_DIR, "install", "uninstall.sh")):
        src_uninstall = os.path.join(INSTALL_DIR, "install", "uninstall.sh")
    elif os.path.isfile("install/uninstall.sh"):
        src_uninstall = "install/uninstall.sh"
    if src_uninstall:
        shutil.copy2(src_uninstall, os.path.join(INSTALL_SCRIPTS_DIR, "uninstall.sh"))

    # Copy launcher to bin and make executable
    shutil.copy2(os.path.join(CORE_DIR, "vaultpass.py"), LOCAL_BIN)
    with open(LOCAL_BIN, "r") as f:
        lines = f.readlines()
    if not lines[0].startswith("#!"):
        lines.insert(0, "#!/usr/bin/env python3\n")
        with open(LOCAL_BIN, "w") as f:
            f.writelines(lines)
    os.chmod(LOCAL_BIN, 0o755)

    # Ensure bin path is in PATH
    shell_rc = os.path.expanduser("~/.bashrc")
    with open(shell_rc, "a+") as f:
        f.seek(0)
        content = f.read()
        if BIN_DIR not in os.environ.get("PATH", "") and f'export PATH="{BIN_DIR}:$PATH"' not in content:
            f.write(f'\nexport PATH="{BIN_DIR}:$PATH"\n')
            os.environ["PATH"] = f"{BIN_DIR}:{os.environ.get('PATH', '')}"

    # Touch metadata files
    for meta in ["passphrase_hint.txt", "vaultpass.log", ".last_update_check"]:
        open(os.path.join(SYSTEM_DIR, meta), "a").close()

    # Check python3 and requests
    if not shutil.which("python3"):
        print("[X] Python3 is not installed. Please install python3 and rerun setup.")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print("[!] Python 'requests' package not found. Installing (may prompt for password)...")
        run_quiet(f"python3 -m pip install --user requests")

    print("[✓] Vaultpass installed successfully.")
    print("[!] Run 'vaultpass -h' to begin.")

if __name__ == "__main__":
    main()