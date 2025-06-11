# install.ps1 - Smart mkpasswd Windows Installer v1.4

Write-Host "[*] Installing/updating mkpasswd for Windows..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.mkpasswd"
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

# Install or update mkpasswd
if (Test-Path "$installDir\.git") {
    Write-Host "[*] mkpasswd already installed. Checking for updates..."
    Set-Location $installDir
    git fetch origin main | Out-Null
    $local = git rev-parse @
    $remote = git rev-parse @{u}
    if ($local -ne $remote) {
        Write-Host "[!] New version available."
        git log --oneline HEAD..origin/main
        $answer = Read-Host "Do you want to update now? (Y/n)"
        if ($answer -eq "Y" -or $answer -eq "y" -or $answer -eq "") {
            git pull origin main
            Write-Host "[✔] mkpasswd updated!"
        } else {
            Write-Host "Update cancelled."
        }
    } else {
        Write-Host "[*] mkpasswd is already up to date."
    }
} else {
    Write-Host "[*] Downloading mkpasswd files from GitHub..."
    git clone --depth 1 $repoUrl $installDir
    Write-Host "[✔] mkpasswd installed successfully!"
}

# Create a launcher (mkpasswd.bat) in WindowsApps for global access
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
if (!(Test-Path $binDir)) { New-Item -ItemType Directory -Force -Path $binDir | Out-Null }
$launcherContent = "@echo off`npython `"%USERPROFILE%\.mkpasswd\core\mkpasswd`" %*"
Set-Content -Path "$binDir\mkpasswd.bat" -Value $launcherContent -Encoding ASCII

Write-Host "Open a new terminal (CMD or PowerShell) and run: mkpasswd -h" -ForegroundColor Green