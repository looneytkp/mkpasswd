#!/usr/bin/env python3
# core/password_gen.py
"""
Password generation module for Vaultpass.
Generates secure passwords (long or short) with complexity requirements.
"""

import sys
import random
import string

def generate_password(length):
    """
    Generates a secure password of given length.
    Ensures at least one lowercase, one uppercase, one digit, and one special character.
    """
    chars = string.ascii_letters + string.digits + '!@#$%^&*_+-='
    while True:
        password = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        # Check for complexity: at least one of each type
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*_+-=' for c in password)):
            return password

def usage():
    print("Usage: password_gen.py [short|long]")
    print("  short: generates 8-character password (default)")
    print("  long:  generates 16-character password")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else "short"
    if mode == "long":
        print(generate_password(16))
    elif mode == "short":
        print(generate_password(8))
    elif mode in ("-h", "--help", "help"):
        usage()
    else:
        print("[X] Invalid mode.")
        usage()
        sys.exit(1)