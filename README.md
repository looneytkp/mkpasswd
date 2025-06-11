# vaultpass

**vaultpass** is a cross-platform, open-source, command-line password manager with GPG encryption.

## Features

- Secure password storage and generation (short/long/custom)
- Stores username/email with each password
- Full search/list/delete/edit support
- Local vault encrypted with your passphrase (GPG)
- Automatic backups and easy restore
- Detailed logs of actions
- Weekly update checks and changelog
- Linux, Windows, macOS, and Termux support

## Install

**Linux/macOS/Termux:**
    
    bash <(curl -fsSL https://raw.githubusercontent.com/looneytkp/vaultpass/main/install/install.sh)

**Windows PowerShell:**
    
    irm https://raw.githubusercontent.com/looneytkp/vaultpass/main/install/install.ps1 | iex

## Usage

    vaultpass -h         # Show help
    vaultpass --update   # Check for updates
    vaultpass -l ID      # Generate long password for ID
    vaultpass -s ID      # Generate short password for ID
    vaultpass -L         # List all saved passwords
    vaultpass -S ID      # Search for password by ID
    vaultpass -d ID      # Delete a password by ID
    vaultpass -b         # Backup vault
    vaultpass -r         # Restore from backup
    vaultpass -e ID      # Edit username/email for entry
    vaultpass -c         # Show changelog
    vaultpass --log      # Show log

## Requirements

- Python 3 (`python3`)
- python-gnupg (`pip install --user python-gnupg`)
- git

*The installer will handle all dependencies!*