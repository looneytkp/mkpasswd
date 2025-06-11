#!/bin/bash
set -e
echo "[*] Installing mkpasswd..."

INSTALL_DIR="$HOME/.mkpasswd"
CURRENT_DIR="$(pwd)"

if [ "$CURRENT_DIR" != "$INSTALL_DIR" ]; then
  mkdir -p "$INSTALL_DIR"
  cp mkpasswd vault.py password_gen.py "$INSTALL_DIR/"
  echo "[-] Files copied to $INSTALL_DIR"
else
  echo "[!] Already inside install directory. Skipping copy."
fi

chmod +x "$INSTALL_DIR/mkpasswd"
BIN_PATH="$PREFIX/bin/mkpasswd"
if [ ! -e "$BIN_PATH" ]; then
  ln -s "$INSTALL_DIR/mkpasswd" "$BIN_PATH"
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