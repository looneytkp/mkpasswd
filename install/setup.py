#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

REPO_URL = "https://github.com/looneytkp/vaultpass.git"

HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(HOME, ".vaultpass")
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

def ensure_bin_dir():
    os.makedirs(BIN_DIR, exist_ok=True)

def clone_or_update_repo():
    if os.path.exists(INSTALL_DIR):
        # Only if NOT a git repo (half-installed or leftover), ask to remove!
        if not os.path.exists(os.path.join(INSTALL_DIR, ".git")):
            print(f"[!] Existing non-git directory found at {INSTALL_DIR}.")
            resp = input("[?] Delete and reinstall? (Y/n): ").strip().lower()
            if resp in ("y", ""):
                shutil.rmtree(INSTALL_DIR)
                print("[*] Removed previous directory.")
            else:
                print("[X] Install aborted.")
                sys.exit(1)
        else:
            print("[*] Updating Vaultpass repo...")
            subprocess.run(["git", "pull", "origin", "main"], cwd=INSTALL_DIR)
            return
    print("[*] Cloning Vaultpass repo...")
    rc = subprocess.run(["git", "clone", REPO_URL, INSTALL_DIR])
    if rc.returncode != 0:
        print("[X] Git clone failed.")
        sys.exit(1)

def ensure_core_inits():
    core_dir = os.path.join(INSTALL_DIR, "core")
    if os.path.exists(core_dir):
        for fname in os.listdir(core_dir):
            fpath = os.path.join(core_dir, fname)
            if os.path.isdir(fpath):
                ensure_init_py(fpath)
        ensure_init_py(core_dir)

def install_bin():
    core_dir = os.path.join(INSTALL_DIR, "core")
    main_script = os.path.join(core_dir, "vaultpass.py")
    shutil.copy2(main_script, LOCAL_BIN)
    os.chmod(LOCAL_BIN, 0o755)
    print(f"[✓] Installed CLI: {LOCAL_BIN}")

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
        print(f"[✓] Added {BIN_DIR} to PATH in {bashrc}")
    else:
        print(f"[✓] PATH already includes: {BIN_DIR}")

def main():
    ensure_python3()
    ensure_bin_dir()
    clone_or_update_repo()
    ensure_core_inits()
    install_bin()
    update_path()
    print("[✓] Vaultpass installed successfully.")
    print("[!] Run 'vaultpass -h' to begin.")

if __name__ == "__main__":
    main()