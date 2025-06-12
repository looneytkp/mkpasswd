#!/usr/bin/env python3
# core/vault.py
"""
Vault logic module for Vaultpass.
Handles GPG encryption, decryption, verification, and passphrase change.
"""

import sys
from getpass import getpass

try:
    import gnupg
except ImportError:
    print("[X] Missing 'python-gnupg' library. Please install with 'pip install python-gnupg'.")
    sys.exit(1)

gpg = gnupg.GPG()  # Initialize the GPG interface

def encrypt(input_file, output_file):
    """
    Encrypts a file using a symmetric passphrase.
    """
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
    """
    Decrypts a file using a passphrase.
    """
    passphrase = getpass("Enter your passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase=passphrase, output=output_file)
    if not status.ok:
        print("[X] Decryption failed:", status.status)
        sys.exit(1)

def verify(input_file):
    """
    Verifies if the given passphrase can decrypt the file.
    """
    passphrase = getpass("Enter your current passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase=passphrase)
    if not status.ok:
        print("[X] Verification failed:", status.status)
        sys.exit(1)
    print("[✓] Passphrase is correct.")

def change_passphrase(input_file):
    """
    Changes the passphrase for the encrypted file.
    """
    old_pass = getpass("Enter current passphrase: ")
    # Decrypt the file with the old passphrase
    decrypted = gpg.decrypt_file(open(input_file, "rb"), passphrase=old_pass)
    if not decrypted.ok:
        print("[X] Decryption failed with current passphrase.")
        sys.exit(1)
    new_pass = getpass("Enter new passphrase: ")
    confirm_pass = getpass("Confirm new passphrase: ")
    if new_pass != confirm_pass:
        print("[X] Passphrases do not match.")
        sys.exit(1)
    # Re-encrypt the data with the new passphrase
    result = gpg.encrypt(
        str(decrypted), recipients=None, symmetric=True,
        passphrase=new_pass, output=input_file
    )
    if not result.ok:
        print("[X] Re-encryption failed:", result.status)
        sys.exit(1)
    print("[✓] Passphrase changed successfully.")

if __name__ == "__main__":
    # Basic CLI for vault actions
    if len(sys.argv) < 3:
        print("Usage: vault.py [encrypt|decrypt|verify|change_passphrase] input [output]")
        sys.exit(1)

    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    if command == "encrypt":
        if not output_file:
            print("[X] Output file required for encryption.")
            sys.exit(1)
        encrypt(input_file, output_file)
    elif command == "decrypt":
        if not output_file:
            print("[X] Output file required for decryption.")
            sys.exit(1)
        decrypt(input_file, output_file)
    elif command == "verify":
        verify(input_file)
    elif command == "change_passphrase":
        change_passphrase(input_file)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)