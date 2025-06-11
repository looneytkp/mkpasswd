import sys
import gnupg
import os

gpg = gnupg.GPG()
passfile = sys.argv[2]

def get_passphrase():
    return input("🔐 Enter master passphrase: ")

def decrypt():
    outfile = sys.argv[3]
    with open(passfile, 'rb') as f:
        decrypted = gpg.decrypt_file(f, passphrase=get_passphrase(), output=outfile)
        if not decrypted.ok:
            print("[X] Failed to decrypt. Wrong passphrase?")
            os.remove(outfile) if os.path.exists(outfile) else None
            sys.exit(1)

def encrypt():
    infile = sys.argv[3]
    with open(infile, 'rb') as f:
        encrypted = gpg.encrypt_file(
            f,
            None,
            passphrase=get_passphrase(),
            symmetric='AES256',
            output=passfile
        )
        if not encrypted.ok:
            print("[X] Encryption failed.")
            sys.exit(1)

def verify():
    with open(passfile, 'rb') as f:
        decrypted = gpg.decrypt_file(f, passphrase=get_passphrase())
        if not decrypted.ok:
            print("[X] Incorrect passphrase.")
            sys.exit(1)
        else:
            print("[✔] Passphrase verified.")

def change_passphrase():
    infile = passfile + ".tmp"
    with open(passfile, 'rb') as f:
        decrypted = gpg.decrypt_file(f, passphrase=get_passphrase(), output=infile)
        if not decrypted.ok:
            print("[X] Failed to verify current passphrase.")
            os.remove(infile) if os.path.exists(infile) else None
            sys.exit(1)
    new_pass = input("🔐 Enter new passphrase: ")
    with open(infile, 'rb') as f:
        encrypted = gpg.encrypt_file(
            f,
            None,
            passphrase=new_pass,
            symmetric='AES256',
            output=passfile
        )
    os.remove(infile)
    print("[✔] Passphrase changed successfully.")

cmd = sys.argv[1]

if cmd == "decrypt":
    decrypt()
elif cmd == "encrypt":
    encrypt()
elif cmd == "verify":
    verify()
elif cmd == "change_passphrase":
    change_passphrase()
else:
    print("[X] Unknown command.")