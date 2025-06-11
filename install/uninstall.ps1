# uninstall.ps1 - mkpasswd universal uninstaller (Windows PowerShell)

Write-Host "[*] Uninstalling mkpasswd..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.mkpasswd"
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
$backupDir = "$installDir\backup"
$vaultFile = "$installDir\system\passwords.gpg"

# Offer backup before removal
if (Test-Path $vaultFile) {
    $response = Read-Host "Do you want to backup your password vault before uninstalling? (Y/n)"
    if ($response -eq "Y" -or $response -eq "y" -or $response -eq "") {
        if (!(Test-Path $backupDir)) { New-Item -ItemType Directory -Force -Path $backupDir | Out-Null }
        $backupPath = "$backupDir\passwords_uninstall_$(Get-Date -Format 'yyyyMMddHHmmss').gpg"
        Copy-Item $vaultFile $backupPath -Force
        Write-Host "[✔] Passwords backed up to $backupPath" -ForegroundColor Green
    }
}

# Remove .mkpasswd directory
if (Test-Path $installDir) {
    Remove-Item $installDir -Recurse -Force
    Write-Host "[*] Removed $installDir"
}

# Remove launcher
$batPath = "$binDir\mkpasswd.bat"
if (Test-Path $batPath) {
    Remove-Item $batPath -Force
    Write-Host "[*] Removed mkpasswd launcher from WindowsApps"
}

Write-Host "[✔] mkpasswd and all related files removed." -ForegroundColor Green
Write-Host "[!] If you backed up your vault, it is in: $backupDir" -ForegroundColor Yellow