#!/bin/bash
# remote-install.sh - mkpasswd one-liner installer

set -e

REPO_URL="https://github.com/looneytkp/mkpasswd"
RAW_URL="https://raw.githubusercontent.com/looneytkp/mkpasswd/main/install/install.sh"

echo "[*] Downloading mkpasswd installer..."
bash <(curl -fsSL "$RAW_URL")