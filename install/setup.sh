#!/bin/bash
# vaultpass - Setup Script (Installer/Uninstaller)
set -e

INSTALL_DIR="$HOME/.vaultpass"
BIN_PATH="$HOME/.local/bin/vaultpass"

# Function to install dependencies (distro-aware)
install_dependencies() {
    echo "[*] Checking required packages..."
    PKG_MANAGER=""
    if [ -x "$(command -v apt-get)" ]; then
        PKG_MANAGER="sudo apt-get install -y"
    elif [ -x "$(command -v dnf)" ]; then
        PKG_MANAGER="sudo dnf install -y"
    elif [ -x "$(command -v pacman)" ]; then
        PKG_MANAGER="sudo pacman -Syu --noconfirm"
    elif [ -x "$(command -v pkg)" ]; then
        PKG_MANAGER="pkg install -y"
    else
        echo "[X] Unsupported package manager. Install git and python3 manually."
        return
    fi

    if ! command -v git >/dev/null 2>&1; then
        echo "[*] Installing git..."
        $PKG_MANAGER git
    fi
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[*] Installing python3..."
        $PKG_MANAGER python3
    fi
}

# Function to install vaultpass
install_vaultpass() {
    echo "[*] Installing vaultpass..."
    rm -rf "$INSTALL_DIR"
    git clone https://github.com/looneytkp/vaultpass "$INSTALL_DIR"
    mkdir -p "$HOME/.local/bin"
    cp "$INSTALL_DIR/core/vaultpass" "$BIN_PATH"
    chmod +x "$BIN_PATH"
    echo "[✔] Installed. Run with: vaultpass"
}

# Function to uninstall vaultpass
uninstall_vaultpass() {
    echo "[*] Uninstalling vaultpass..."
    read -p "Do you want to delete all vaultpass files? (Y/n): " conf
    if [[ "$conf" =~ ^[Yy]$ || -z "$conf" ]]; then
        rm -rf "$INSTALL_DIR"
        rm -f "$BIN_PATH"
        echo "[✔] vaultpass uninstalled."
    else
        echo "Uninstall cancelled."
    fi
    exit 0
}

# --- Main Logic ---

# Check if vaultpass is already installed (folder or command exists)
if [ -d "$INSTALL_DIR" ] || command -v vaultpass >/dev/null 2>&1; then
    echo "vaultpass is already installed."
    echo "What would you like to do?"
    echo "1) Reinstall vaultpass"
    echo "2) Uninstall vaultpass"
    echo "3) Cancel"
    read -p "[?] Choose an option (1/2/3): " opt
    case $opt in
        1) install_dependencies && install_vaultpass ;;
        2) uninstall_vaultpass ;;
        *) echo "Cancelled."; exit 0 ;;
    esac
else
    install_dependencies
    install_vaultpass
fi