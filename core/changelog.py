# core/changelog.py

import os
from core.cli import print_changelog_box, show_banner

def get_latest_changelog(changelog_file, version):
    """
    Returns a list of changelog lines for the given version.
    If not found, returns an empty list.
    """
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
    """
    Prints the changelog for a given version (box style).
    Truncates if longer than `truncate` lines.
    """
    show_banner(version)
    lines = get_latest_changelog(changelog_file, version)
    if not lines:
        print("[!] No changelog found for this version.")
        return
    display_lines = lines[:truncate]
    if len(lines) > truncate:
        display_lines.append("[...truncated. See full changelog online.]")
    print_changelog_box(version, display_lines)
    print("\n[*] Full changelog: https://github.com/looneytkp/vaultpass\n")