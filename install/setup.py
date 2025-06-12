#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import platform

REPO_URL = "https://github.com/looneytkp/vaultpass.git"

def is_windows():
    return os.name == "nt"

def detect_python3():
    py_exec = shutil.which("python3")
    if not py_exec and is_windows():
        py_exec = shutil.which("python")
    return py_exec

def ensure_python3():
    py_exec = detect_python3()
    if not py_exec:
        print("[X] Python 3 is required to run Vaultpass. Please install Python 3 and re-run this script.")
        sys.exit(1)
    return py_exec

def run_quiet(cmd, cwd=None):
    kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if cwd:
        kwargs["cwd"] = cwd
    result = subprocess.run(cmd, **kwargs)
    return result.returncode == 0

def detect_shell_rc():
    shell = os.environ.get("SHELL", "")
    home = os.path.expanduser("~")
    rc_files = []
    if platform.system() == "Darwin":
        zshrc = os.path.join(home, ".zshrc")
        bash_profile = os.path.join(home, ".bash_profile")
        if os.path.exists(zshrc):
            rc_files.append(zshrc)
        elif os.path.exists(bash_profile):
            rc_files.append(bash_profile)
        else:
            rc_files.append(zshrc)
    else:
        bashrc = os.path.join(home, ".bashrc")
        zshrc = os.path.join(home, ".zshrc")
        if os.path.exists(bashrc):
            rc_files.append(bashrc)
        elif os.path.exists(zshrc):
            rc_files.append(zshrc)
        else:
            rc_files.append(bashrc)
    return rc_files

def add_bin_to_path(bin_dir):
    if is_windows():
        print(f"[!] Please add '{bin_dir}' to your system PATH environment variable for global use.")
        return
    rc_files = detect_shell_rc()
    export_line = f'export PATH="{bin_dir}:$PATH"\n'
    updated = False
    for rc_file in rc_files:
        already = False
        if os.path.exists(rc_file):
            with open(rc_file, "r") as f:
                if bin_dir in f.read():
                    already = True
        if not already:
            with open(rc_file, "a") as f:
                f.write(f'\n# Added by Vaultpass installer\n{export_line}')
            updated = True
    if updated:
        print(f"[✓] PATH updated: {bin_dir}")
    else:
        print(f"[✓] PATH already set.")

def install_python_packages(packages):
    try:
        import pip
    except ImportError:
        print("[X] pip not found. Please install pip for your Python environment.")
        sys.exit(1)
    actually_installed = False
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            if not actually_installed:
                print("[*] Installing required packages for Vaultpass:")
                actually_installed = True
            print(f"[!] Installing '{pkg}' package...")
            rc = run_quiet([sys.executable, "-m", "pip", "install", "--user", pkg])
            if not rc:
                print(f"[X] Failed to install '{pkg}'. Please install it manually.")
                sys.exit(1)
    return actually_installed

def main():
    py_exec = ensure_python3()
    HOME = os.path.expanduser("~") if not is_windows() else os.environ.get("USERPROFILE", os.path.expanduser("~"))
    INSTALL_DIR = os.path.join(HOME, ".vaultpass")
    CORE_DIR = os.path.join(INSTALL_DIR, "core")
    SYSTEM_DIR = os.path.join(INSTALL_DIR, "system")
    BACKUP_DIR = os.path.join(INSTALL_DIR, "backup")
    BIN_DIR = os.path.join(HOME, ".local", "bin")
    LAUNCHER = "vaultpass.py" if is_windows() else "vaultpass"
    LOCAL_BIN = os.path.join(BIN_DIR, LAUNCHER)

    fresh_install = False

    # 1. Fresh install
    if not os.path.exists(INSTALL_DIR):
        print("[*] Installing Vaultpass...")
        rc = run_quiet(["git", "clone", REPO_URL, INSTALL_DIR])
        if not rc:
            print("[X] Failed to install Vaultpass. Please check your internet connection or repo.")
            sys.exit(1)
        fresh_install = True

    # 2. Detected previous (non-git) install
    elif not os.path.isdir(os.path.join(INSTALL_DIR, ".git")):
        print("[*] Previous Vaultpass installation detected.")
        print("[*] Cleaning up previous Vaultpass installation...")
        shutil.rmtree(INSTALL_DIR, ignore_errors=True)
        print("[*] Installing Vaultpass...")
        rc = run_quiet(["git", "clone", REPO_URL, INSTALL_DIR])
        if not rc:
            print("[X] Failed to install Vaultpass. Please check your internet connection or repo.")
            sys.exit(1)
        fresh_install = True

    # 3. Update existing install
    else:
        print("[*] Updating Vaultpass...")
        rc = run_quiet(["git", "pull", "origin", "main"], cwd=INSTALL_DIR)
        if rc:
            print("[✓] Vaultpass updated successfully.")
        else:
            print("[X] Failed to update Vaultpass. Please check your internet connection or repo status.")
            sys.exit(1)

    for d in [CORE_DIR, SYSTEM_DIR, BACKUP_DIR, BIN_DIR]:
        os.makedirs(d, exist_ok=True)

    # Ensure core scripts are present
    if not (os.path.isfile(os.path.join(CORE_DIR, "vault.py")) and
            os.path.isfile(os.path.join(CORE_DIR, "password_gen.py")) and
            os.path.isfile(os.path.join(CORE_DIR, "vaultpass.py"))):
        print("[X] Missing core scripts. Please check the repository.")
        sys.exit(1)

    # Copy launcher (overwrites old one)
    shutil.copy2(os.path.join(CORE_DIR, "vaultpass.py"), LOCAL_BIN)
    try:
        os.chmod(LOCAL_BIN, 0o755)
    except Exception:
        pass

    # Shebang check/skip
    with open(LOCAL_BIN, "r") as f:
        lines = f.readlines()
    shebang = f"#!{py_exec}\n"
    if not lines[0].startswith("#!"):
        lines.insert(0, shebang)
        with open(LOCAL_BIN, "w") as f:
            f.writelines(lines)

    add_bin_to_path(BIN_DIR)

    # Touch metadata files
    for meta in ["passphrase_hint.txt", "vaultpass.log", ".last_update_check"]:
        open(os.path.join(SYSTEM_DIR, meta), "a").close()

    # Install required Python packages only if missing
    install_python_packages(['requests'])

    # Print installed version if available
    version_txt = os.path.join(INSTALL_DIR, "version.txt")
    version = None
    if os.path.exists(version_txt):
        with open(version_txt) as vf:
            version = vf.read().strip()
    if version:
        print(f"[✓] Vaultpass {version} installed successfully.")
    else:
        print("[✓] Vaultpass installed successfully.")

    print("[!] Run 'vaultpass -h' to begin.")

if __name__ == "__main__":
    main()