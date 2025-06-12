#!/usr/bin/env python3
import sys
from getpass import getpass
import gnupg
import os
import tempfile

gpg = gnupg.GPG()

def encrypt(input_file, output_file):
    passphrase = getpass("Enter your passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.encrypt_file(
            f, recipients=None, symmetric=True, passphrase=passphrase,
            output=output_file
        )
    if not status.ok:
        print("[X] Encryption failed:", status.status)
        sys.exit(1)
    print("[✓] Encrypted successfully.")

def decrypt(input_file, output_file):
    passphrase = getpass("Enter your passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase=passphrase, output=output_file)
    if not status.ok:
        print("[X] Decryption failed:", status.status)
        sys.exit(1)
    print("[✓] Decrypted successfully.")

def verify(input_file):
    passphrase = getpass("Enter your current passphrase: ")
    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase=passphrase)
    if not status.ok:
        print("[X] Verification failed:", status.status)
        sys.exit(1)
    print("[✓] Passphrase verified.")

def change_passphrase(input_file):
    # First, prompt for new passphrase to avoid having to re-enter current on failure
    new_pass = getpass("Enter new passphrase: ")
    confirm_pass = getpass("Confirm new passphrase: ")
    if new_pass != confirm_pass:
        print("[X] Passphrases do not match.")
        sys.exit(1)
    old_pass = getpass("Enter current passphrase: ")
    # Decrypt current file
    with open(input_file, "rb") as f:
        decrypted = gpg.decrypt_file(f, passphrase=old_pass)
    if not decrypted.ok:
        print("[X] Decryption failed with current passphrase.")
        sys.exit(1)
    # Write decrypted data to temp file
    with tempfile.NamedTemporaryFile("wb", delete=False) as tf:
        tf.write(decrypted.data)
        temp_file = tf.name
    # Encrypt again with new passphrase
    with open(temp_file, "rb") as f:
        status = gpg.encrypt_file(
            f, recipients=None, symmetric=True, passphrase=new_pass,
            output=input_file
        )
    os.remove(temp_file)
    if not status.ok:
        print("[X] Re-encryption failed:", status.status)
        sys.exit(1)
    print("[✓] Passphrase changed.")

if __name__ == "__main__":
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