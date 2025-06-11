#!/bin/bash

INSTALL_DIR="$HOME/.vaultpass"
REPO_URL="https://github.com/looneytkp/vaultpass.git"

echo "[*] Installing vaultpass..."

# Remove old install if it exists
if [ -d "$INSTALL_DIR" ]; then
    echo "[*] Removing old installation..."
    rm -rf "$INSTALL_DIR"
fi

# Check if git is installed
if ! command -v git &>/dev/null; then
    echo "[!] git not found. Installing git..."
    if [ -x "$(command -v pkg)" ]; then
        pkg install -y git
    elif [ -x "$(command -v apt-get)" ]; then
        sudo apt-get update && sudo apt-get install -y git
    elif [ -x "$(command -v dnf)" ]; then
        sudo dnf install -y git
    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -Sy --noconfirm git
    else
        echo "[!] Package manager not supported. Please install git manually."
        exit 1
    fi
fi

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "[!] Python 3 not found. Installing..."
    if [ -x "$(command -v pkg)" ]; then
        pkg install -y python
    elif [ -x "$(command -v apt-get)" ]; then
        sudo apt-get update && sudo apt-get install -y python3
    elif [ -x "$(command -v dnf)" ]; then
        sudo dnf install -y python3
    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -Sy --noconfirm python
    else
        echo "[!] Package manager not supported. Please install Python manually."
        exit 1
    fi
fi

# Install python-gnupg
pip3 install --user python-gnupg &>/dev/null

# Clone the repo
git clone "$REPO_URL" "$INSTALL_DIR"

# Make the script executable and link it
chmod +x "$INSTALL_DIR/core/vaultpass"
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/core/vaultpass" "$HOME/.local/bin/vaultpass"

# Termux / Linux PATH fix
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "[*] PATH updated in .bashrc"
fi

export PATH="$HOME/.local/bin:$PATH"

echo ""
echo "[✔] vaultpass installed successfully!"
echo "[*] If 'vaultpass' still doesn't work, try this:"
echo "    source ~/.bashrc"
echo ""
echo "[*] Or run directly:"
echo "    ~/.local/bin/vaultpass"