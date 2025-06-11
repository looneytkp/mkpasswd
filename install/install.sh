#!/bin/bash
# install.sh - mkpasswd installer (Linux/WSL)

set -e

INSTALL_DIR="$HOME/.mkpasswd"
BIN_PATH="$HOME/.local/bin"
MAIN_SCRIPT="core/mkpasswd"

echo "[*] Installing mkpasswd..."

mkdir -p "$INSTALL_DIR/core" "$INSTALL_DIR/system" "$INSTALL_DIR/install" "$INSTALL_DIR/backup" "$INSTALL_DIR/remote"
cp -r core/* "$INSTALL_DIR/core/"
cp -r install/* "$INSTALL_DIR/install/"
cp -r remote/* "$INSTALL_DIR/remote/"
cp README.md "$INSTALL_DIR/" 2>/dev/null || true

# System files
touch "$INSTALL_DIR/system/passphrase_hint.txt"
touch "$INSTALL_DIR/system/passwords.gpg"
touch "$INSTALL_DIR/system/version.txt"
touch "$INSTALL_DIR/system/mkpasswd.log"
echo "1.3" > "$INSTALL_DIR/system/version.txt"

# Python check
if ! command -v python3 >/dev/null; then
  echo "[!] Python 3 is required. Please install it and rerun this installer."
  exit 1
fi
# GPG check (optional)
if ! command -v gpg >/dev/null; then
  echo "[!] GPG not found. Backups will not be encrypted. (Install gpg if you want encryption)"
fi

chmod +x "$INSTALL_DIR/core/mkpasswd"
mkdir -p "$BIN_PATH"
ln -sf "$INSTALL_DIR/core/mkpasswd" "$BIN_PATH/mkpasswd"
if ! echo "$PATH" | grep -q "$BIN_PATH"; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "[✔] mkpasswd installed successfully!"
echo "Type 'mkpasswd -h' to get started."
exit 0
