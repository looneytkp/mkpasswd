import sys
from getpass import getpass
import gnupg

gpg = gnupg.GPG()

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: vault.py [encrypt|decrypt|verify|change_passphrase] input [output]")
        sys.exit(1)

    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    if command == "encrypt":
        encrypt(input_file, output_file)
    elif command == "decrypt":
        decrypt(input_file, output_file)
    elif command == "verify":
        verify(input_file)
    elif command == "change_passphrase":
        change_passphrase(input_file)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)