# install.ps1 - mkpasswd universal installer (Windows PowerShell, v1.3+)

Write-Host "[*] Installing mkpasswd for Windows..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.mkpasswd"
$coreDir = "$installDir\core"
$systemDir = "$installDir\system"
$backupDir = "$installDir\backup"
$launcher = "$PSScriptRoot\mkpasswd-launcher"
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"

# Create directories
New-Item -ItemType Directory -Force -Path $coreDir | Out-Null
New-Item -ItemType Directory -Force -Path $systemDir | Out-Null
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Copy core and system files
Copy-Item "$PSScriptRoot\core\*" "$coreDir\" -Recurse -Force
Copy-Item "$PSScriptRoot\system\*" "$systemDir\" -Recurse -Force

# Touch/init system files if missing
$versionPath = "$systemDir\version.txt"
$hintPath = "$systemDir\passphrase_hint.txt"
$passwordsPath = "$systemDir\passwords.gpg"
$logPath = "$systemDir\mkpasswd.log"
if (!(Test-Path $versionPath)) { "1.3" | Set-Content $versionPath }
if (!(Test-Path $hintPath)) { "" | Set-Content $hintPath }
if (!(Test-Path $passwordsPath)) { "" | Set-Content $passwordsPath }
if (!(Test-Path $logPath)) { "" | Set-Content $logPath }

# Copy universal launcher
Copy-Item $launcher "$binDir\mkpasswd.bat" -Force

Write-Host "[✔] mkpasswd installed successfully!"
Write-Host "Open any terminal and run: mkpasswd -h" -ForegroundColor Green