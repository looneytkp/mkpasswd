#!/bin/bash
set -e

INSTALL_DIR="$HOME/.mkpasswd"
REPO_URL="https://github.com/looneytkp/mkpasswd.git"

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