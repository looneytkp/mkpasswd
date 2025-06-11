# install.ps1 - Smart mkpasswd Windows Installer

Write-Host "[*] Installing mkpasswd for Windows..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.mkpasswd"
$coreDir = "$installDir\core"
$systemDir = "$installDir\system"
$backupDir = "$installDir\backup"
$remoteDir = "$installDir\remote"
$tmpDir = Join-Path $env:TEMP "mkpasswd_tmp_$(Get-Random)"

$repoUrl = "https://github.com/looneytkp/mkpasswd.git"

function Install-Git {
    Write-Host "[*] 'git' not found. Downloading and installing Git for Windows..." -ForegroundColor Yellow
    $gitInstaller = "$env:TEMP\Git-Setup.exe"
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/latest/download/Git-2.44.0-64-bit.exe" -OutFile $gitInstaller
    Start-Process -Wait -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART"
    Remove-Item $gitInstaller
}

function Update-Git {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "[*] Updating git with winget..."
        winget upgrade --id Git.Git -e --accept-package-agreements --accept-source-agreements
    } else {
        Write-Host "[*] winget not available. Please update git manually if needed."
    }
}

# Check for git
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    Install-Git
} else {
    Write-Host "[*] 'git' found. Checking for updates..."
    Update-Git
}

Write-Host "[*] Downloading mkpasswd files from GitHub..."
git clone --depth 1 $repoUrl $tmpDir

# Prepare directories
New-Item -ItemType Directory -Force -Path $coreDir | Out-Null
New-Item -ItemType Directory -Force -Path $systemDir | Out-Null
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
New-Item -ItemType Directory -Force -Path $remoteDir | Out-Null

# Copy files
Copy-Item "$tmpDir\core\*" $coreDir -Recurse -Force
Copy-Item "$tmpDir\install\*" "$installDir\install" -Recurse -Force
Copy-Item "$tmpDir\system\*" $systemDir -Recurse -Force
Copy-Item "$tmpDir\backup\*" $backupDir -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item "$tmpDir\remote\*" $remoteDir -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item "$tmpDir\README.md" $installDir -Force

# System files
$versionPath = "$systemDir\version.txt"
$hintPath = "$systemDir\passphrase_hint.txt"
$passwordsPath = "$systemDir\passwords.gpg"
$logPath = "$systemDir\mkpasswd.log"
if (!(Test-Path $versionPath)) { "1.3" | Set-Content $versionPath }
if (!(Test-Path $hintPath)) { "" | Set-Content $hintPath }
if (!(Test-Path $passwordsPath)) { "" | Set-Content $passwordsPath }
if (!(Test-Path $logPath)) { "" | Set-Content $logPath }

# Create a launcher (mkpasswd.bat) in WindowsApps for global access
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
if (!(Test-Path $binDir)) { New-Item -ItemType Directory -Force -Path $binDir | Out-Null }
$launcherContent = "@echo off`npython `"%USERPROFILE%\.mkpasswd\core\mkpasswd`" %*"
Set-Content -Path "$binDir\mkpasswd.bat" -Value $launcherContent -Encoding ASCII

# Cleanup
Remove-Item $tmpDir -Recurse -Force

Write-Host "[✔] mkpasswd installed successfully!"
Write-Host "Open a new terminal (CMD or PowerShell) and run: mkpasswd -h" -ForegroundColor Green