#!/bin/bash
echo "[*] Downloading mkpasswd..."
mkdir -p "$HOME/.mkpasswd"
cd "$HOME/.mkpasswd"
curl -sL https://github.com/looneytkp/mkpasswd/archive/refs/heads/main.zip -o mkpasswd.zip
unzip -o mkpasswd.zip >/dev/null
cp -r mkpasswd-main/* ./
rm -rf mkpasswd.zip mkpasswd-main
echo "[*] Running installer..."
bash install.sh
