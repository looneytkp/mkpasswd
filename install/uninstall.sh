#!/bin/bash

INSTALL_DIR="$HOME/.vaultpass"
BIN_PATH="$HOME/.local/bin/vaultpass"

echo "[*] Uninstalling vaultpass..."

# Remove symlink
if [ -f "$BIN_PATH" ]; then
    rm -f "$BIN_PATH"
    echo "[*] Removed binary: $BIN_PATH"
fi

# Remove main directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "[*] Removed install directory: $INSTALL_DIR"
fi

# Remove PATH line from .bashrc if it was added
if grep -q 'export PATH="\$HOME/.local/bin:\$PATH"' "$HOME/.bashrc"; then
    sed -i '/export PATH="\$HOME\/.local\/bin:\$PATH"/d' "$HOME/.bashrc"
    echo "[*] Cleaned PATH entry from .bashrc"
fi

# Ask to remove Git and Python
read -p "[?] Do you also want to uninstall Git and Python? (y/N): " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    if [ -x "$(command -v pkg)" ]; then
        pkg uninstall -y git python
    elif [ -x "$(command -v apt-get)" ]; then
        sudo apt-get remove -y git python3
    elif [ -x "$(command -v dnf)" ]; then
        sudo dnf remove -y git python3
    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -Rns --noconfirm git python
    else
        echo "[!] Could not auto-remove Git/Python — unsupported package manager."
    fi
fi

echo ""
echo "[✔] vaultpass has been completely removed."