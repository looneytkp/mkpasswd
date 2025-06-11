#!/bin/bash
echo "[!] This will remove mkpasswd and all saved passwords."
read -p "Are you sure? (Y/n): " confirm
[[ "$confirm" =~ ^[Nn]$ ]] && exit 0
rm -f "$PREFIX/bin/mkpasswd"
rm -rf "$HOME/.mkpasswd"
echo "[✔] mkpasswd uninstalled."
