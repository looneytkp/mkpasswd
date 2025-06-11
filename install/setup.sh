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

function install_vaultpass() {
    echo "[*] Installing vaultpass..."

    # Ensure Git
    if ! command -v git &>/dev/null; then
        echo "[*] Installing git..."
        if command -v pkg &>/dev/null; then pkg install -y git
        elif command -v apt-get &>/dev/null; then sudo apt-get install -y git
        elif command -v dnf &>/dev/null; then sudo dnf install -y git
        elif command -v pacman &>/dev/null; then sudo pacman -Sy --noconfirm git
        else echo "[!] No supported package manager"; exit 1
        fi
    fi

    # Ensure Python
    if ! command -v python3 &>/dev/null; then
        echo "[*] Installing python3..."
        if command -v pkg &>/dev/null; then pkg install -y python
        elif command -v apt-get &>/dev/null; then sudo apt-get install -y python3
        elif command -v dnf &>/dev/null; then sudo dnf install -y python3
        elif command -v pacman &>/dev/null; then sudo pacman -Sy --noconfirm python
        else echo "[!] No supported package manager"; exit 1
        fi
    fi

    # Install Python dependency
    pip3 install --user python-gnupg &>/dev/null

    # Clone repo
    git clone "$REPO_URL" "$INSTALL_DIR"

    # Set permissions and link binary
    chmod +x "$INSTALL_DIR/core/vaultpass"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$INSTALL_DIR/core/vaultpass" "$BIN_PATH"

    # Ensure path
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
                uninstall_vaultpass
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