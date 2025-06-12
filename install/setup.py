#!/usr/bin/env python3
"""
setup.py -- Vaultpass installer/updater

- Installs Vaultpass to ~/.vaultpass/
- Adds ~/.local/bin/vaultpass to PATH (if not present)
- Installs required Python packages
- Friendly output, idempotent (safe to re-run)
"""

import os
import sys
import shutil
import subprocess

REPO_URL = "https://github.com/looneytkp/vaultpass.git"

def have_python():
    return sys.version_info >= (3, 6)

def ensure_requests():
    try:
        import requests
        return True
    except ImportError:
        print("[!] Installing requests package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "requests"])
        return True

def clone_or_update_repo(install_dir):
    if os.path.exists(install_dir):
        print("[*] Updating existing Vaultpass...")
        rc = subprocess.run(["git", "pull"], cwd=install_dir,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc.returncode != 0:
            print("[X] Failed to update. Check your repo or connection.")
            sys.exit(1)
    else:
        print("[*] Cloning Vaultpass repository...")
        rc = subprocess.run(["git", "clone", REPO_URL, install_dir],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc.returncode != 0:
            print("[X] Failed to clone repo. Check your connection.")
            sys.exit(1)

def ensure_dirs(home):
    os.makedirs(os.path.join(home, ".vaultpass", "core"), exist_ok=True)
    os.makedirs(os.path.join(home, ".vaultpass", "system"), exist_ok=True)
    os.makedirs(os.path.join(home, ".vaultpass", "backup"), exist_ok=True)
    os.makedirs(os.path.join(home, ".vaultpass", "install"), exist_ok=True)

def add_to_path(bin_dir):
    shell = os.environ.get("SHELL", "")
    home = os.path.expanduser("~")
    rc_files = [os.path.join(home, ".bashrc"), os.path.join(home, ".zshrc")]
    export_line = f'export PATH="{bin_dir}:$PATH"'
    updated = False
    for rc in rc_files:
        if os.path.exists(rc):
            with open(rc, "r") as f:
                if export_line in f.read():
                    continue
            with open(rc, "a") as f:
                f.write("\n# Added by Vaultpass installer\n" + export_line + "\n")
            updated = True
    if updated:
        print(f"[✓] Added {bin_dir} to your PATH.")
    else:
        print(f"[✓] PATH already includes {bin_dir}.")

def main():
    if not have_python():
        print("[X] Python 3.6+ required. Install Python and try again.")
        sys.exit(1)
    ensure_requests()
    HOME = os.path.expanduser("~")
    INSTALL_DIR = os.path.join(HOME, ".vaultpass")
    BIN_DIR = os.path.join(HOME, ".local", "bin")
    CLI_SRC = os.path.join(INSTALL_DIR, "core", "vaultpass.py")
    CLI_BIN = os.path.join(BIN_DIR, "vaultpass")
    ensure_dirs(HOME)
    clone_or_update_repo(INSTALL_DIR)
    if os.path.isfile(CLI_SRC):
        os.makedirs(BIN_DIR, exist_ok=True)
        shutil.copy2(CLI_SRC, CLI_BIN)
        os.chmod(CLI_BIN, 0o755)
        print(f"[✓] vaultpass installed at {CLI_BIN}")
    add_to_path(BIN_DIR)
    print("[✓] Vaultpass installation complete.")
    print("[!] Run 'vaultpass -h' to get started.")

if __name__ == "__main__":
    main()