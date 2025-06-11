#!/bin/bash
set -e

INSTALL_DIR="$HOME/.mkpasswd"
BIN_PATH="$HOME/.local/bin/mkpasswd"
BACKUP_DIR="$INSTALL_DIR/backup"
PASS_FILE="$INSTALL_DIR/system/passwords.gpg"

echo "[*] Uninstalling mkpasswd..."

# Ask about backup
if [ -f "$PASS_FILE" ]; then
  read -p "Do you want to backup your password vault before uninstalling? (Y/n): " answer
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
  echo "[*] Removed mkpasswd command from ~/.local/bin/"
fi

# Uninstall git
if command -v git >/dev/null; then
  read -p "Do you want to uninstall git as well? (y/N): " un_git
  if [[ "$un_git" =~ ^[Yy]$ ]]; then
    if command -v apt-get >/dev/null; then
      sudo apt-get remove -y git
    elif command -v yum >/dev/null; then
      sudo yum remove -y git
    elif command -v brew >/dev/null; then
      brew uninstall git
    else
      echo "[!] Cannot uninstall git automatically. Please uninstall it manually."
    fi
  fi
fi

# Uninstall python3
if command -v python3 >/dev/null; then
  read -p "Do you want to uninstall python3 as well? (y/N): " un_py
  if [[ "$un_py" =~ ^[Yy]$ ]]; then
    if command -v apt-get >/dev/null; then
      sudo apt-get remove -y python3 python3-pip
    elif command -v yum >/dev/null; then
      sudo yum remove -y python3 python3-pip
    elif command -v brew >/dev/null; then
      brew uninstall python
    else
      echo "[!] Cannot uninstall python3 automatically. Please uninstall it manually."
    fi
  fi
fi

echo "[✔] mkpasswd and all related files removed."
echo "[!] If you backed up your vault, it is in: $BACKUP_DIR"
exit 0