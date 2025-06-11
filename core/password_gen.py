#!/usr/bin/env python3
"""
password_gen.py - mkpasswd secure password generator
Author: looneytkp
"""

import sys
import string
import secrets

def generate_password(length=16, symbols=True):
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>/?"
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    # Usage: password_gen.py [length] [nosymbols]
    length = 16
    symbols = True

    if len(sys.argv) > 1:
        try:
            length = int(sys.argv[1])
        except ValueError:
            print("Invalid length. Using default (16).")
    if len(sys.argv) > 2:
        if sys.argv[2].lower() == "nosymbols":
            symbols = False

    print(generate_password(length, symbols))
