import os
import sys
import subprocess
import time
import shutil
import requests

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

import cli

def parse_ver(verstr):
    return tuple(map(int, verstr.strip().lstrip("vV").split(".")))

def get_local_commit(repo_path):
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_path, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""

def get_remote_commit(repo_path):
    try:
        subprocess.run(
            ["git", "fetch", "origin", "main"], cwd=repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return subprocess.check_output(
            ["git", "rev-parse", "origin/main"], cwd=repo_path, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""

def get_remote_msg(repo_path):
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--pretty=%B", "origin/main"],
            cwd=repo_path, text=True, stderr=subprocess.DEVNULL
        ).splitlines()[0]
    except Exception:
        return "(minor update)"

def check_for_updates(current_version, version_file, changelog_file, install_dir, core_dir, bin_path, last_update_file, remote_version_url):
    now = int(time.time())
    need_update = False

    if os.path.exists(last_update_file):
        last = int(os.path.getmtime(last_update_file))
        diff_days = (now - last) // 86400
        if diff_days >= 3:
            need_update = True
    else:
        need_update = True

    if not need_update:
        return

    print("[*] Checking for Vaultpass updates...")

    local_version = current_version

    try:
        r = requests.get(remote_version_url, timeout=5)
        r.raise_for_status()
        remote_version = r.text.strip()
    except Exception:
        print("[X] Could not fetch remote version info.")
        open(last_update_file, "a").close()
        return

    local_commit = get_local_commit(install_dir)
    remote_commit = get_remote_commit(install_dir)

    version_update = parse_ver(local_version) < parse_ver(remote_version)
    commit_update = (local_commit and remote_commit and local_commit != remote_commit)

    if version_update:
        print(f"[!] New version: v{remote_version}")
        lines = []
        try:
            with open(changelog_file, "r") as f:
                content = f.read()
            start = content.find(f"Version {remote_version}")
            if start != -1:
                end = content.find("Version ", start+1)
                lines = content[start:end].strip().splitlines()[1:] if end != -1 else content[start:].strip().splitlines()[1:]
        except Exception:
            pass
        cli.show_banner(remote_version)
        if lines:
            cli.print_changelog_box(remote_version, lines)
        print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass\n")
        update = input("[?] Update? (Y/n): ").strip().lower()
        if update in ("y", ""):
            print("[*] Updating Vaultpass…")
            rc = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=install_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if rc.returncode == 0:
                with open(version_file, "w") as f:
                    f.write(remote_version)
                shutil.copy2(os.path.join(core_dir, "vaultpass.py"), bin_path)
                os.chmod(bin_path, 0o755)
                print(f"[✓] Vaultpass updated to v{remote_version}.")
            else:
                print("[X] Failed to update Vaultpass.")
        open(last_update_file, "a").close()
        return

    elif commit_update:
        remote_msg = get_remote_msg(install_dir)
        print(f"[!] New version: {remote_msg}")
        update = input("[?] Update? (Y/n): ").strip().lower()
        if update in ("y", ""):
            print("[*] Updating Vaultpass…")
            rc = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=install_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if rc.returncode == 0:
                shutil.copy2(os.path.join(core_dir, "vaultpass.py"), bin_path)
                os.chmod(bin_path, 0o755)
                print("[✓] Vaultpass minor update applied.")
            else:
                print("[X] Failed to update Vaultpass.")
        open(last_update_file, "a").close()
        return

    else:
        #print("[✓] Vaultpass is up to date.")
        open(last_update_file, "a").close()
        return