#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.."; pwd)"

echo "[?] Uninstall Vaultpass and delete ALL its data, binaries, and project files? (Y/n): "
read answer

if [[ "$answer" =~ ^[Yy]$ || -z "$answer" ]]; then
    rm -rf "$HOME/.vaultpass"
    rm -f "$HOME/.local/bin/vaultpass"
    if grep -q 'export PATH="\$HOME/.local/bin:\$PATH"' "$HOME/.bashrc"; then
        sed -i '/export PATH="\$HOME\/.local\/bin:\$PATH"/d' "$HOME/.bashrc"
    fi
    rm -rf "$PROJECT_DIR"
    echo "[✔] Vaultpass and all related files have been completely removed."
else
    echo "[!] Uninstall cancelled."
fi