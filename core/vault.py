#!/usr/bin/env python3
"""
vault.py - Encryption/Decryption helper for vaultpass
Uses GPG (python-gnupg) to encrypt/decrypt vault files.
"""

import sys
import gnupg
import getpass
import os

def get_passphrase():
    if 'VAULTPASS_PASSPHRASE' in os.environ:
        return os.environ['VAULTPASS_PASSPHRASE']
    else:
        return getpass.getpass("Enter vault passphrase: ")

def encrypt(infile, outfile):
    gpg = gnupg.GPG()
    passphrase = get_passphrase()
    with open(infile, 'rb') as f:
        status = gpg.encrypt_file(
            f, recipients=None, symmetric=True,
            passphrase=passphrase,
            output=outfile
        )
    if not status.ok:
        print("[X] Encryption failed:", status.status)
        sys.exit(1)

def decrypt(infile, outfile):
    gpg = gnupg.GPG()
    passphrase = get_passphrase()
    with open(infile, 'rb') as f:
        status = gpg.decrypt_file(
            f, passphrase=passphrase, output=outfile
        )
    if not status.ok:
        print("[X] Decryption failed:", status.status)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: vault.py [encrypt|decrypt] <input> <output>")
        sys.exit(1)
    action = sys.argv[1]
    infile = sys.argv[2]
    outfile = sys.argv[3]
    if action == "encrypt":
        encrypt(infile, outfile)
    elif action == "decrypt":
        decrypt(infile, outfile)
    else:
        print("Unknown action:", action)
        sys.exit(1)
