def make_centered_banner(_=None):
    width = 37
    line1 = "VAULTPASS"
    line2 = "Secure Password Manager"
    def pad(s):
        total = width - 2 - len(s)
        left = total // 2
        right = total - left
        return " " * left + s + " " * right
    top = "╔" + "═" * (width - 2) + "╗"
    mid1 = "║" + pad(line1) + "║"
    mid2 = "║" + pad(line2) + "║"
    bot = "╚" + "═" * (width - 2) + "╝"
    return "\n" + "\n".join([top, mid1, mid2, bot]) + "\n"

def show_banner(version=None):
    print(make_centered_banner())