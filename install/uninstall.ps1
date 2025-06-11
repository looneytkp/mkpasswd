# uninstall.ps1 - mkpasswd Windows PowerShell uninstaller

Write-Host "[*] Uninstalling mkpasswd..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.mkpasswd"
$systemDir = "$installDir\system"
$backupDir = "$installDir\backup"
$vaultFile = "$systemDir\passwords.gpg"
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"

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

# Remove launcher from WindowsApps
$cmdPath = "$binDir\mkpasswd.cmd"
if (Test-Path $cmdPath) {
    Remove-Item $cmdPath -Force
    Write-Host "[*] Removed mkpasswd command from WindowsApps"
}

Write-Host "[✔] mkpasswd and all related files removed." -ForegroundColor Green
Write-Host "[!] If you backed up your vault, it is in: $backupDir" -ForegroundColor Yellow
