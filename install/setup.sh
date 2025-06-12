#!/bin/bash

REPO_URL="https://github.com/looneytkp/vaultpass.git"
INSTALL_DIR="$HOME/.vaultpass"
CORE_DIR="$INSTALL_DIR/core"
SYSTEM_DIR="$INSTALL_DIR/system"
BACKUP_DIR="$INSTALL_DIR/backup"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="vaultpass"
LOCAL_BIN="$BIN_DIR/$LAUNCHER"
INSTALL_SCRIPTS_DIR="$INSTALL_DIR/install"

# Install or update repo
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "[*] Updating Vaultpass..."
  git -C "$INSTALL_DIR" pull origin main > /dev/null 2>&1
else
  echo "[*] Installing Vaultpass..."
  git clone "$REPO_URL" "$INSTALL_DIR" > /dev/null 2>&1
fi

# Create necessary folders (after cloning to avoid git clone errors)
mkdir -p "$CORE_DIR" "$SYSTEM_DIR" "$BACKUP_DIR" "$BIN_DIR" "$INSTALL_SCRIPTS_DIR" > /dev/null 2>&1

# Ensure core scripts are in place
if [ ! -f "$CORE_DIR/vault.py" ] || [ ! -f "$CORE_DIR/password_gen.py" ] || [ ! -f "$CORE_DIR/vaultpass" ]; then
  echo "[X] Missing core scripts. Please check the repository."
  exit 1
fi

# Ensure uninstall.sh is always present in ~/.vaultpass/install/
if [ -f "$INSTALL_DIR/install/uninstall.sh" ]; then
    cp "$INSTALL_DIR/install/uninstall.sh" "$INSTALL_SCRIPTS_DIR/uninstall.sh" > /dev/null 2>&1
elif [ -f "install/uninstall.sh" ]; then
    cp "install/uninstall.sh" "$INSTALL_SCRIPTS_DIR/uninstall.sh" > /dev/null 2>&1
fi

# Copy launcher to bin and make executable
cp "$CORE_DIR/vaultpass" "$LOCAL_BIN" > /dev/null 2>&1
chmod +x "$LOCAL_BIN" > /dev/null 2>&1

# Ensure bin path is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
  export PATH="$BIN_DIR:$PATH"
fi

# Touch metadata files
touch "$SYSTEM_DIR/passphrase_hint.txt" "$SYSTEM_DIR/vaultpass.log" "$SYSTEM_DIR/.last_update_check" > /dev/null 2>&1

echo "[✓] Vaultpass installed successfully."
echo "[!] Run 'vaultpass -h' to begin."