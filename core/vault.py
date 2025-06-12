#!/usr/bin/env python3

import os
import sys
from getpass import getpass
import gnupg
import random
import string

# ====================
# Vaultpass Vault Logic
# ====================

HOME = os.path.expanduser("~")
SYSTEM_DIR = os.path.join(HOME, ".vaultpass", "system")
PASS_FILE = os.path.join(SYSTEM_DIR, "passwords.gpg")
HINT_FILE = os.path.join(SYSTEM_DIR, "passphrase_hint.txt")

gpg = gnupg.GPG()

# --------- Password Generation ----------
def generate_password(length=16):
    chars = string.ascii_letters + string.digits + '!@#$%^&*_+-='
    while True:
        password = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*_+-=' for c in password)):
            return password

# --------- Encryption & Decryption ----------
def encrypt(input_file, output_file):
    passphrase = getpass("Enter your passphrase: ")
    with open(input_file, "r") as f:
        status = gpg.encrypt_file(
            f, recipients=None, symmetric=True, passphrase=passphrase,
            output=output_file
        )
    if not status.ok:
        print("[X] Encryption failed:", status.status)
        sys.exit(1)

def decrypt(input_file, output_file):
    passphrase = getpass("Enter your passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase=passphrase, output=output_file)
    if not status.ok:
        print("[X] Decryption failed:", status.status)
        sys.exit(1)

def verify(input_file):
    passphrase = getpass("Enter your current passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase=passphrase)
    if not status.ok:
        print("[X] Verification failed:", status.status)
        sys.exit(1)

def change_passphrase(input_file):
    old_pass = getpass("Enter current passphrase: ")
    decrypted = gpg.decrypt_file(open(input_file, "rb"), passphrase=old_pass)
    if not decrypted.ok:
        print("[X] Decryption failed with current passphrase.")
        sys.exit(1)
    new_pass = getpass("Enter new passphrase: ")
    confirm_pass = getpass("Confirm new passphrase: ")
    if new_pass != confirm_pass:
        print("[X] Passphrases do not match.")
        sys.exit(1)
    result = gpg.encrypt(str(decrypted), recipients=None, symmetric=True,
                         passphrase=new_pass, output=input_file)
    if not result.ok:
        print("[X] Re-encryption failed:", result.status)
        sys.exit(1)

# --------- Vault Actions ----------
def list_passwords():
    tmp_file = PASS_FILE + ".tmp"
    decrypt(PASS_FILE, tmp_file)
    with open(tmp_file) as f:
        for line in f:
            print(line.strip())
    os.remove(tmp_file)

def add_password(entry_id, username_email, info=""):
    tmp_file = PASS_FILE + ".tmp"
    decrypt(PASS_FILE, tmp_file)
    with open(tmp_file, "a") as f:
        password = generate_password(16)
        f.write(f"{entry_id}|{username_email}|{password}|{info}\n")
    encrypt(tmp_file, PASS_FILE)
    os.remove(tmp_file)
    print(f"[✓] Saved password for {entry_id}.")

def search_password(entry_id):
    tmp_file = PASS_FILE + ".tmp"
    decrypt(PASS_FILE, tmp_file)
    found = False
    with open(tmp_file) as f:
        for line in f:
            if line.startswith(f"{entry_id}|"):
                print(line.strip())
                found = True
    if not found:
        print("[X] No entry found.")
    os.remove(tmp_file)

def delete_password(entry_id):
    tmp_file = PASS_FILE + ".tmp"
    decrypt(PASS_FILE, tmp_file)
    lines = []
    found = False
    with open(tmp_file) as f:
        for line in f:
            if not line.startswith(f"{entry_id}|"):
                lines.append(line)
            else:
                found = True
    with open(tmp_file, "w") as f:
        f.writelines(lines)
    encrypt(tmp_file, PASS_FILE)
    os.remove(tmp_file)
    if found:
        print(f"[✓] Deleted entry for {entry_id}.")
    else:
        print("[X] No entry found.")

# --------- Command-line Usage ----------
if __name__ == "__main__":
    # Simple CLI for demo purposes
    if len(sys.argv) < 2:
        print("Usage: vault.py [list|add|search|delete|encrypt|decrypt|verify|change_passphrase] [args...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_passwords()
    elif command == "add":
        if len(sys.argv) < 4:
            print("Usage: vault.py add <ID> <username/email> [info]")
            sys.exit(1)
        entry_id = sys.argv[2]
        username_email = sys.argv[3]
        info = sys.argv[4] if len(sys.argv) > 4 else ""
        add_password(entry_id, username_email, info)
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: vault.py search <ID>")
            sys.exit(1)
        entry_id = sys.argv[2]
        search_password(entry_id)
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: vault.py delete <ID>")
            sys.exit(1)
        entry_id = sys.argv[2]
        delete_password(entry_id)
    elif command == "encrypt":
        if len(sys.argv) < 4:
            print("Usage: vault.py encrypt <input> <output>")
            sys.exit(1)
        encrypt(sys.argv[2], sys.argv[3])
    elif command == "decrypt":
        if len(sys.argv) < 4:
            print("Usage: vault.py decrypt <input> <output>")
            sys.exit(1)
        decrypt(sys.argv[2], sys.argv[3])
    elif command == "verify":
        if len(sys.argv) < 3:
            print("Usage: vault.py verify <input>")
            sys.exit(1)
        verify(sys.argv[2])
    elif command == "change_passphrase":
        if len(sys.argv) < 3:
            print("Usage: vault.py change_passphrase <input>")
            sys.exit(1)
        change_passphrase(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)