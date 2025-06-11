import sys
import random
import string

def generate(length):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def main():
    if len(sys.argv) != 2:
        print("Usage: password_gen.py [short|long]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "short":
        print(generate(12))
    elif mode == "long":
        print(generate(24))
    else:
        print("[X] Unknown mode. Use 'short' or 'long'.")
        sys.exit(1)

if __name__ == "__main__":
    main()