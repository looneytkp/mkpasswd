#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

REPO_URL = "https://github.com/looneytkp/vaultpass.git"

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
CORE_DIR = os.path.join(INSTALL_DIR, "core")
SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
BIN_DIR = os.path.join(HOME, ".local", "bin")
LAUNCHER = "vaultpass"
LOCAL_BIN = os.path.join(BIN_DIR, LAUNCHER)

def ensure_python3():
    if not shutil.which("python3"):
        print("[X] Python 3 is required. Please install it and re-run this script.")
        sys.exit(1)

def ensure_init_py(folder):
    path = os.path.join(folder, "__init__.py")
    if not os.path.exists(path):
        open(path, "a").close()

def setup_folders():
    for d in [INSTALL_DIR, CORE_DIR, SYSTEM_DIR, BACKUP_DIR, BIN_DIR]:
        os.makedirs(d, exist_ok=True)

def ensure_core_inits():
    for fname in os.listdir(CORE_DIR):
        fpath = os.path.join(CORE_DIR, fname)
        if os.path.isdir(fpath):
            ensure_init_py(fpath)
    ensure_init_py(CORE_DIR)

def clone_or_update_repo():
    if os.path.exists(INSTALL_DIR):
        if not os.path.exists(os.path.join(INSTALL_DIR, ".git")):
            print("[✓] Removed previous Vaultpass installation.")
            resp = input("[?] Delete and reinstall? (Y/n): ").strip().lower()
            if resp in ("y", ""):
                shutil.rmtree(INSTALL_DIR)
            else:
                print("[X] Install aborted.")
                sys.exit(1)
        else:
            print("[*] Updating Vaultpass repo...")
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=INSTALL_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return
    print("[*] Installing Vaultpass...")
    rc = subprocess.run(
        ["git", "clone", REPO_URL, INSTALL_DIR],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    if rc.returncode != 0:
        print("[X] Git clone failed.")
        sys.exit(1)

def install_bin():
    main_script = os.path.join(CORE_DIR, "vaultpass.py")
    shutil.copy2(main_script, LOCAL_BIN)
    os.chmod(LOCAL_BIN, 0o755)

def update_path():
    bashrc = os.path.join(HOME, ".bashrc")
    zshrc = os.path.join(HOME, ".zshrc")
    added = False
    for rc in [bashrc, zshrc]:
        if os.path.exists(rc):
            with open(rc, "r") as f:
                if BIN_DIR in f.read():
                    added = True
    if not added:
        with open(bashrc, "a") as f:
            f.write(f'\n# Vaultpass: Add user bin to PATH\nexport PATH="{BIN_DIR}:$PATH"\n')
        print(f"[✓] Vaultpass PATH is set.")
    else:
        print(f"[✓] Vaultpass PATH is set.")

def main():
    ensure_python3()
    setup_folders()
    clone_or_update_repo()
    ensure_core_inits()
    install_bin()
    update_path()
    print("[✓] Vaultpass installed successfully.")
    print("[!] Run 'vaultpass -h' to begin.")

if __name__ == "__main__":
    main()