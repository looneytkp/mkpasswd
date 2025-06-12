#!/bin/bash

REPO_URL="https://github.com/looneytkp/vaultpass.git"
INSTALL_DIR="$HOME/.vaultpass"
CORE_DIR="$INSTALL_DIR/core"
SYSTEM_DIR="$INSTALL_DIR/system"
BACKUP_DIR="$INSTALL_DIR/backup"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="vaultpass"
LOCAL_BIN="$BIN_DIR/$LAUNCHER"

# Create necessary folders
mkdir -p "$CORE_DIR" "$SYSTEM_DIR" "$BACKUP_DIR" "$BIN_DIR"

# Clone or update repo
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "[*] Updating vaultpass..."
  git -C "$INSTALL_DIR" pull origin main
else
  echo "[*] Installing vaultpass..."
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Ensure core scripts are in place
if [ ! -f "$CORE_DIR/vault.py" ] || [ ! -f "$CORE_DIR/password_gen.py" ]; then
  echo "[X] Missing core scripts. Please check the repository."
  exit 1
fi

# Copy launcher to bin and make executable
cp "$INSTALL_DIR/vaultpass" "$LOCAL_BIN"
chmod +x "$LOCAL_BIN"

# Ensure bin path is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
  export PATH="$BIN_DIR:$PATH"
fi

# Touch metadata files
touch "$SYSTEM_DIR/passphrase_hint.txt" "$SYSTEM_DIR/vaultpass.log" "$SYSTEM_DIR/.last_update_check"

echo "[✔] vaultpass installed successfully."
echo "[!] Run 'vaultpass -h' to begin."