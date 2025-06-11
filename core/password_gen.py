#!/usr/bin/env python3
"""
password_gen.py - Password generator for mkpasswd
Usage: password_gen.py [short|long]
"""

import sys
import secrets
import string

def gen_password(length):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("short", "long"):
        print("Usage: password_gen.py [short|long]")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "short":
        print(gen_password(8))
    elif mode == "long":
        print(gen_password(20))