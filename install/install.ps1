# install.ps1 - mkpasswd Windows PowerShell installer

Write-Host "[*] Installing mkpasswd for Windows..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.mkpasswd"
$coreDir = "$installDir\core"
$systemDir = "$installDir\system"
$backupDir = "$installDir\backup"
$installSrc = "$PSScriptRoot\core"
$systemSrc = "$PSScriptRoot\system"
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"

# Create directories
New-Item -ItemType Directory -Force -Path $coreDir | Out-Null
New-Item -ItemType Directory -Force -Path $systemDir | Out-Null
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Copy core and system files
Copy-Item "$installSrc\*" "$coreDir\" -Recurse -Force
Copy-Item "$systemSrc\*" "$systemDir\" -Recurse -Force

# System files (touch equivalents)
$versionPath = "$systemDir\version.txt"
$hintPath = "$systemDir\passphrase_hint.txt"
$passwordsPath = "$systemDir\passwords.gpg"
$logPath = "$systemDir\mkpasswd.log"
if (!(Test-Path $versionPath)) { "1.3" | Set-Content $versionPath }
if (!(Test-Path $hintPath)) { "" | Set-Content $hintPath }
if (!(Test-Path $passwordsPath)) { "" | Set-Content $passwordsPath }
if (!(Test-Path $logPath)) { "" | Set-Content $logPath }

# Create a mkpasswd.cmd launcher in WindowsApps for global usage
$cmdLauncher = @"
@echo off
python "%USERPROFILE%\.mkpasswd\core\mkpasswd" %*
"@
$cmdPath = "$binDir\mkpasswd.cmd"
Set-Content -Path $cmdPath -Value $cmdLauncher -Encoding ASCII

Write-Host "[✔] mkpasswd installed successfully!"
Write-Host "Open a new terminal (CMD or PowerShell) and run: mkpasswd -h" -ForegroundColor Green