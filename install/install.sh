#!/bin/bash
set -e

INSTALL_DIR="$HOME/.mkpasswd"
REPO_URL="https://github.com/looneytkp/mkpasswd.git"
TMP_DIR="$(mktemp -d)"

# Function to install git if missing
install_git() {
    echo "[*] 'git' not found. Attempting to install..."
    if command -v apt-get >/dev/null; then
        sudo apt-get update && sudo apt-get install -y git
    elif command -v yum >/dev/null; then
        sudo yum install -y git
    elif command -v brew >/dev/null; then
        brew install git
    else
        echo "[X] Cannot install git automatically. Please install git and rerun."
        exit 1
    fi
}

# Check for git
if ! command -v git >/dev/null; then
    install_git
else
    echo "[*] 'git' found. Checking for updates..."
    if command -v apt-get >/dev/null; then
        sudo apt-get update && sudo apt-get install --only-upgrade -y git
    elif command -v yum >/dev/null; then
        sudo yum update -y git
    elif command -v brew >/dev/null; then
        brew upgrade git
    fi
fi

echo "[*] Downloading mkpasswd files from GitHub..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR"

echo "[*] Installing mkpasswd..."
mkdir -p "$INSTALL_DIR"
cp -r "$TMP_DIR/core" "$INSTALL_DIR/"
cp -r "$TMP_DIR/install" "$INSTALL_DIR/"
cp -r "$TMP_DIR/system" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$TMP_DIR/backup" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$TMP_DIR/remote" "$INSTALL_DIR/" 2>/dev/null || true
cp "$TMP_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

# System files
touch "$INSTALL_DIR/system/passphrase_hint.txt"
touch "$INSTALL_DIR/system/passwords.gpg"
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

# Make the script executable and add to PATH
chmod +x "$INSTALL_DIR/core/mkpasswd"
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/core/mkpasswd" "$HOME/.local/bin/mkpasswd"
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  export PATH="$HOME/.local/bin:$PATH"
fi

rm -rf "$TMP_DIR"

echo "[✔] mkpasswd installed successfully!"
echo "Type 'mkpasswd -h' to get started."
exit 0