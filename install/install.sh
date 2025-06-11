#!/bin/bash
set -e

INSTALL_DIR="$HOME/.mkpasswd"
REPO_URL="https://github.com/looneytkp/mkpasswd.git"

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

# Function to install Python if missing
install_python() {
    if ! command -v python3 >/dev/null; then
        echo "[*] Python 3 not found. Attempting to install..."
        if command -v apt-get >/dev/null; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip
        elif command -v yum >/dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v brew >/dev/null; then
            brew install python
        else
            echo "[X] Cannot install Python 3 automatically. Please install and rerun."
            exit 1
        fi
    fi
}

# Function to install python-gnupg if missing
install_python_gnupg() {
    python3 -c "import gnupg" 2>/dev/null || {
        echo "[*] Installing python-gnupg..."
        python3 -m pip install --user python-gnupg
    }
}

# Git check and install
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

install_python
install_python_gnupg

# Install or update mkpasswd
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "[*] mkpasswd already installed. Checking for updates..."
    cd "$INSTALL_DIR"
    git fetch origin main >/dev/null 2>&1
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[!] New version available."
        git log --oneline HEAD..origin/main
        read -p "Do you want to update now? (Y/n): " answer
        if [[ "$answer" =~ ^[Yy]$ || -z "$answer" ]]; then
            git pull origin main
            echo "[✔] mkpasswd updated!"
        else
            echo "Update cancelled."
        fi
    else
        echo "[*] mkpasswd is already up to date."
    fi
else
    echo "[*] Downloading mkpasswd files from GitHub..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    echo "[✔] mkpasswd installed successfully!"
fi

# Make the script executable and add to PATH
chmod +x "$INSTALL_DIR/core/mkpasswd"
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/core/mkpasswd" "$HOME/.local/bin/mkpasswd"
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Type 'mkpasswd -h' to get started."
exit 0