#!/usr/bin/env python3
import sys
import random
import string

# =========================
# Vaultpass Password Gen
# =========================

def generate_password(length):
    """Generate a strong password with at least 1 lowercase, 1 uppercase, 1 digit, and 1 special char."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*_+-='
    while True:
        password = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*_+-=' for c in password)):
            return password

if __name__ == '__main__':
    # CLI Usage: password_gen.py [long|short]
    mode = sys.argv[1] if len(sys.argv) > 1 else "short"
    if mode == "long":
        print(generate_password(16))
    else:
        print(generate_password(8))