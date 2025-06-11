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

# Remove mkpasswd directory
if (Test-Path $installDir) {
    Remove-Item $installDir -Recurse -Force
    Write-Host "[*] Removed $installDir"
}

# Remove launcher from WindowsApps
$batPath = "$binDir\mkpasswd.bat"
if (Test-Path $batPath) {
    Remove-Item $batPath -Force
    Write-Host "[*] Removed mkpasswd launcher from WindowsApps"
}

# Optionally uninstall git
if (Get-Command git.exe -ErrorAction SilentlyContinue) {
    $unGit = Read-Host "Do you want to uninstall Git for Windows as well? (y/N)"
    if ($unGit -eq "y" -or $unGit -eq "Y") {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "[*] Uninstalling Git for Windows using winget..."
            winget uninstall --id Git.Git -e --accept-package-agreements --accept-source-agreements
        } else {
            Write-Host "[!] winget not available. Please uninstall Git manually via Control Panel or Settings."
        }
    }
}

# Optionally uninstall Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $unPy = Read-Host "Do you want to uninstall Python as well? (y/N)"
    if ($unPy -eq "y" -or $unPy -eq "Y") {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "[*] Uninstalling Python using winget..."
            winget uninstall --id Python.Python.3 -e --accept-package-agreements --accept-source-agreements
        } else {
            Write-Host "[!] winget not available. Please uninstall Python manually via Control Panel or Settings."
        }
    }
}

Write-Host "[✔] mkpasswd and all related files removed." -ForegroundColor Green
Write-Host "[!] If you backed up your vault, it is in: $backupDir" -ForegroundColor Yellow