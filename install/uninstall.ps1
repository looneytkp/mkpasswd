# uninstall.ps1 - Windows uninstaller for vaultpass

$InstallDir = "$HOME\.vaultpass"
$Launcher = "$HOME\AppData\Local\Microsoft\WindowsApps\vaultpass.ps1"

Write-Host "[*] Uninstalling vaultpass..."

# Remove launcher
if (Test-Path $Launcher) {
    Remove-Item $Launcher -Force
    Write-Host "[*] Removed vaultpass launcher from WindowsApps."
}

# Remove installation
if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
    Write-Host "[*] Removed vaultpass install directory."
}

# Ask to uninstall Git and Python (optional)
$confirm = Read-Host "[?] Do you want to uninstall Git and Python manually? (y/N)"
if ($confirm -match '^(y|Y)$') {
    Write-Host "You can remove them via Apps & Features in Windows Settings."
}

Write-Host ""
Write-Host "[✔] vaultpass has been completely uninstalled."