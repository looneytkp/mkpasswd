import os
import sys

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

import cli

def get_latest_changelog(changelog_file, version):
    try:
        with open(changelog_file, "r") as f:
            lines = f.readlines()
    except Exception:
        return []
    target = f"Version {version.lstrip('vV')}"
    start, out = False, []
    for line in lines:
        if line.strip().startswith("Version "):
            if start:
                break
            start = line.strip().startswith(target)
            continue
        if start and line.strip():
            out.append(line.strip(" \n"))
    return out

def show_changelog(changelog_file, version, truncate=20):
    cli.show_banner(version)
    lines = get_latest_changelog(changelog_file, version)
    if not lines:
        print("[!] No changelog found for this version.")
        return
    display_lines = lines[:truncate]
    if len(lines) > truncate:
        display_lines.append("[...truncated. See full changelog online.]")
    cli.print_changelog_box(version, display_lines)
    print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass\n")