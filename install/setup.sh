#!/bin/bash

INSTALL_DIR="$HOME/.vaultpass"
BIN_PATH="$HOME/.local/bin/vaultpass"
REPO_URL="https://github.com/looneytkp/vaultpass.git"
SHELL_RC="$HOME/.bashrc"

# Detect shell config
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.profile" ]; then
    SHELL_RC="$HOME/.profile"
fi

function install_git() {
    echo "[*] Git not found. Installing..."
    if command -v pkg &>/dev/null; then pkg install -y git
    elif command -v apt-get &>/dev/null; then sudo apt-get install -y git
    elif command -v dnf &>/dev/null; then sudo dnf install -y git
    elif command -v pacman &>/dev/null; then sudo pacman -Sy --noconfirm git
    else echo "[!] No supported package manager for Git."; exit 1
    fi
}

function install_python() {
    echo "[*] Python not found. Installing..."
    if command -v pkg &>/dev/null; then pkg install -y python
    elif command -v apt-get &>/dev/null; then sudo apt-get install -y python3
    elif command -v dnf &>/dev/null; then sudo dnf install -y python3
    elif command -v pacman &>/dev/null; then sudo pacman -Sy --noconfirm python
    else echo "[!] No supported package manager for Python."; exit 1
    fi
}

function update_git_python() {
    echo "[*] Updating Git and Python..."
    if command -v pkg &>/dev/null; then pkg upgrade -y git python
    elif command -v apt-get &>/dev/null; then sudo apt-get install --only-upgrade -y git python3
    elif command -v dnf &>/dev/null; then sudo dnf upgrade -y git python3
    elif command -v pacman &>/dev/null; then sudo pacman -Syu --noconfirm git python
    fi
}

function install_vaultpass() {
    echo "[*] Installing vaultpass..."

    command -v git &>/dev/null || install_git
    command -v python3 &>/dev/null || install_python

    pip3 install --user python-gnupg &>/dev/null

    git clone "$REPO_URL" "$INSTALL_DIR"

    chmod +x "$INSTALL_DIR/core/vaultpass"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$INSTALL_DIR/core/vaultpass" "$BIN_PATH"

    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "[*] PATH updated in $SHELL_RC"
    fi
    export PATH="$HOME/.local/bin:$PATH"

    echo ""
    echo "[✔] vaultpass installed!"
    echo "[*] Run with: vaultpass"
    echo "[*] Restart terminal if it doesn't work immediately."
}

function uninstall_vaultpass() {
    echo "[*] Uninstalling vaultpass..."

    rm -f "$BIN_PATH"
    rm -rf "$INSTALL_DIR"

    sed -i '/.local\/bin/d' "$SHELL_RC"

    read -p "[?] Also uninstall Git and Python? (y/N): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        if command -v pkg &>/dev/null; then pkg uninstall -y git python
        elif command -v apt-get &>/dev/null; then sudo apt-get remove -y git python3
        elif command -v dnf &>/dev/null; then sudo dnf remove -y git python3
        elif command -v pacman &>/dev/null; then sudo pacman -Rns --noconfirm git python
        else echo "[!] Package manager not supported."
        fi
    fi

    echo "[✔] vaultpass fully uninstalled."
}

function main_menu() {
    if [ -d "$INSTALL_DIR" ]; then
        echo "vaultpass is already installed."
        echo "What would you like to do?"
        echo "1) Reinstall vaultpass"
        echo "2) Uninstall vaultpass"
        echo "3) Cancel"
        read -p "[?] Choose an option (1/2/3): " option

        case "$option" in
            1)
                update_git_python
                rm -f "$BIN_PATH"
                rm -rf "$INSTALL_DIR"
                install_vaultpass
                ;;
            2)
                uninstall_vaultpass
                ;;
            3|*)
                echo "[*] Action cancelled."
                ;;
        esac
    else
        install_vaultpass
    fi
}

main_menu