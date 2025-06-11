#!/usr/bin/env python3
"""
vault.py - mkpasswd password vault helper v1.3
Author: looneytkp
"""

import os
import sys
from datetime import datetime

VAULT_PATH = os.path.expanduser("~/.mkpasswd/system/passwords.gpg")
LOG_PATH = os.path.expanduser("~/.mkpasswd/system/mkpasswd.log")

def log_action(action, detail):
    with open(LOG_PATH, "a") as lf:
        lf.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {action} | {detail}\n")

def save_entry(entry_id, password, username=None):
    """Save a password entry with optional username/email and multi-ID support."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Check for multi-ID: if ID exists, append _n for next count
    entry_lines = []
    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, "r") as f:
            entry_lines = f.readlines()
    similar = [l for l in entry_lines if l.startswith(entry_id)]
    if similar:
        next_num = len(similar) + 1
        entry_id = f"{entry_id}_{next_num}"
    with open(VAULT_PATH, "a") as f:
        username_part = f" | user: {username}" if username else ""
        f.write(f"{entry_id}{username_part} | pass: {password} | added: {now}\n")
    log_action("SAVE", f"Saved entry {entry_id}")

def list_entries():
    """List all entries in the vault."""
    if not os.path.isfile(VAULT_PATH):
        print("No entries found.")
        return
    with open(VAULT_PATH) as f:
        for idx, line in enumerate(f, 1):
            print(f"{idx}. {line.strip()}")

def search_entries(search_term):
    """Search for entries by ID or username/email."""
    if not os.path.isfile(VAULT_PATH):
        print("No entries found.")
        return
    found = False
    with open(VAULT_PATH) as f:
        for line in f:
            if search_term in line:
                print(line.strip())
                found = True
    if not found:
        print("No entries matched your search.")

def delete_entry(entry_id):
    """Delete an entry by its ID."""
    if not os.path.isfile(VAULT_PATH):
        print("Vault is empty.")
        return
    lines_kept = []
    deleted = False
    with open(VAULT_PATH) as f:
        for line in f:
            if entry_id not in line:
                lines_kept.append(line)
            else:
                deleted = True
    with open(VAULT_PATH, "w") as f:
        f.writelines(lines_kept)
    if deleted:
        print(f"Deleted entry '{entry_id}'.")
        log_action("DELETE", f"Deleted {entry_id}")
    else:
        print(f"No entry found for '{entry_id}'.")

def update_username(entry_id, new_user):
    """Update username/email for an entry by ID."""
    if not os.path.isfile(VAULT_PATH):
        print("Vault is empty.")
        return
    updated = False
    lines = []
    for line in open(VAULT_PATH):
        if line.startswith(entry_id):
            parts = line.split('|')
            password = ""
            for part in parts:
                if part.strip().startswith("pass:"):
                    password = part.strip().split("pass:")[1].strip()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_line = f"{entry_id} | user: {new_user} | pass: {password} | added: {now}\n"
            lines.append(new_line)
            updated = True
        else:
            lines.append(line)
    with open(VAULT_PATH, "w") as f:
        f.writelines(lines)
    if updated:
        print(f"[✔] Updated username/email for {entry_id}")
        log_action("UPDATE_USER", f"Updated user for {entry_id}")
    else:
        print(f"No entry found for {entry_id}")

if __name__ == "__main__":
    # Minimal CLI for testing
    if len(sys.argv) < 2:
        print("Usage: vault.py [save|list|search|delete|update_user] ...")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "save":
        eid, pwd = sys.argv[2], sys.argv[3]
        username = sys.argv[4] if len(sys.argv) > 4 else None
        save_entry(eid, pwd, username)
    elif cmd == "list":
        list_entries()
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Provide a search term.")
        else:
            search_entries(sys.argv[2])
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Provide an entry ID to delete.")
        else:
            delete_entry(sys.argv[2])
    elif cmd == "update_user":
        if len(sys.argv) < 4:
            print("Provide an entry ID and new user/email.")
        else:
            update_username(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
