#!/bin/bash
# uninstall.sh - mkpasswd uninstaller for Linux

set -e

INSTALL_DIR="$HOME/.mkpasswd"
BIN_PATH="$HOME/.local/bin/mkpasswd"
BACKUP_DIR="$HOME/.mkpasswd/backup"
PASS_FILE="$INSTALL_DIR/system/passwords.gpg"

echo "[*] Uninstalling mkpasswd..."

# Ask about backup (to backup/ with timestamp)
if [ -f "$PASS_FILE" ]; then
  echo -n "Do you want to backup your password vault before uninstalling? (Y/n): "
  read answer
  if [[ "$answer" =~ ^[Yy]$ || -z "$answer" ]]; then
    mkdir -p "$BACKUP_DIR"
    BACKUP_PATH="$BACKUP_DIR/passwords_uninstall_$(date +%Y%m%d%H%M%S).gpg"
    cp "$PASS_FILE" "$BACKUP_PATH"
    echo "[✔] Passwords backed up to $BACKUP_PATH"
  fi
fi

rm -rf "$INSTALL_DIR"

if [ -L "$BIN_PATH" ]; then
  rm "$BIN_PATH"
  echo "[*] Removed command from ~/.local/bin/"
fi

if grep -q '.local/bin' "$HOME/.bashrc"; then
  sed -i '/.local\\/bin/d' "$HOME/.bashrc"
fi

echo "[✔] mkpasswd and all related files removed."
echo "[!] If you backed up your vault, it is in: $BACKUP_DIR"
exit 0