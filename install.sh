#!/bin/bash
set -e
echo "[*] Installing mkpasswd..."
mkdir -p "$HOME/.mkpasswd"
cp mkpasswd vault.py password_gen.py "$HOME/.mkpasswd/"
chmod +x "$HOME/.mkpasswd/mkpasswd"
BIN_PATH="$PREFIX/bin/mkpasswd"
if [ ! -e "$BIN_PATH" ]; then
  ln -s "$HOME/.mkpasswd/mkpasswd" "$BIN_PATH"
  echo "[+] mkpasswd linked to $BIN_PATH"
fi
python3 -c "import gnupg" 2>/dev/null || {
  echo "[!] python-gnupg not found. Installing..."
  (command -v pip3 && pip3 install python-gnupg) || (command -v pip && pip install python-gnupg) || {
    echo "[x] pip not found. Please install it manually."
    exit 1
  }
}
echo "[✔] Installation complete. Run 'mkpasswd' to start."
