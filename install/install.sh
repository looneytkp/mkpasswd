#!/bin/bash
set -e

INSTALL_DIR="$HOME/.vaultpass"
BIN_PATH="$HOME/.local/bin/vaultpass"
REPO_URL="https://github.com/looneytkp/vaultpass.git"

# --- Remove any old install ---
if [ -d "$INSTALL_DIR" ]; then
    echo "[*] Removing previous vaultpass install at $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
fi
if [ -L "$BIN_PATH" ]; then
    echo "[*] Removing old vaultpass symlink at $BIN_PATH..."
    rm -f "$BIN_PATH"
fi

install_deps() {
    # Termux (Android)
    if [ -n "$PREFIX" ] && grep -qi termux <<< "$PREFIX"; then
        echo "[*] Detected Termux (Android)."
        pkg install -y git python
        pip install --user python-gnupg
        return
    fi

    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "[*] Detected macOS."
        if ! command -v brew >/dev/null; then
            echo "[X] Homebrew not found. Please install Homebrew and rerun."
            exit 1
        fi
        brew install git python
        python3 -m pip install --user python-gnupg
        return
    fi

    # Standard Linux distros
    if command -v apt-get >/dev/null; then
        sudo apt-get update
        sudo apt-get install -y git python3 python3-pip
        python3 -m pip install --user python-gnupg
    elif command -v dnf >/dev/null; then
        sudo dnf install -y git python3 python3-pip
        python3 -m pip install --user python-gnupg
    elif command -v yum >/dev/null; then
        sudo yum install -y git python3 python3-pip
        python3 -m pip install --user python-gnupg
    elif command -v pacman >/dev/null; then
        sudo pacman -Sy --noconfirm git python python-pip
        python3 -m pip install --user python-gnupg
    elif command -v apk >/dev/null; then
        sudo apk add git python3 py3-pip
        python3 -m pip install --user python-gnupg
    elif command -v zypper >/dev/null; then
        sudo zypper install -y git python3 python3-pip
        python3 -m pip install --user python-gnupg
    elif command -v xbps-install >/dev/null; then
        sudo xbps-install -Sy git python3 python3-pip
        python3 -m pip install --user python-gnupg
    elif command -v eopkg >/dev/null; then
        sudo eopkg install -y git python3 python3-pip
        python3 -m pip install --user python-gnupg
    else
        echo "[X] Unsupported Linux distribution. Please install git, python3, and python-gnupg manually."
        exit 1
    fi
}

install_deps

# Install or update vaultpass
echo "[*] Downloading vaultpass files from GitHub..."
git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
echo "[✔] vaultpass installed successfully!"

# Make the script executable and add to PATH
chmod +x "$INSTALL_DIR/core/vaultpass"
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/core/vaultpass" "$HOME/.local/bin/vaultpass"

# Ensure ~/.local/bin is in PATH at the start
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
fi
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    echo "[*] Added ~/.local/bin to PATH in $SHELL_RC"
fi
. "$SHELL_RC"

echo "Type 'vaultpass -h' to get started."
exit 0