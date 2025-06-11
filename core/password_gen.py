import secrets
import string
import sys

def generate_short():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

def generate_long():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(20))

def generate_custom():
    length = int(input("Length of custom password: "))
    use_symbols = input("Include symbols? (Y/n): ").strip().lower() != 'n'
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

mode = sys.argv[1] if len(sys.argv) > 1 else 'short'

if mode == "short":
    print(generate_short())
elif mode == "long":
    print(generate_long())
elif mode == "custom":
    print(generate_custom())
else:
    print("Invalid mode. Use: short | long | custom")