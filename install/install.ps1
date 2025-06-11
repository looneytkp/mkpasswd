# install.ps1 - vaultpass Universal Windows Installer
Write-Host "[*] Starting vaultpass installer for Windows..." -ForegroundColor Cyan

$installDir = "$env:USERPROFILE\.vaultpass"
$binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
$batPath = "$binDir\vaultpass.bat"
$repoUrl = "https://github.com/looneytkp/vaultpass.git"

# --- Remove any old install ---
if (Test-Path $installDir) {
    Write-Host "[*] Removing previous vaultpass install at $installDir..."
    Remove-Item $installDir -Recurse -Force
}
if (Test-Path $batPath) {
    Write-Host "[*] Removing old vaultpass launcher at $batPath..."
    Remove-Item $batPath -Force
}

# --- Dependency installers ---
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
function Install-Python {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "[*] Python not found. Downloading and installing Python..." -ForegroundColor Yellow
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Python.Python.3 -e --accept-package-agreements --accept-source-agreements
        } else {
            Write-Host "[!] Please install Python 3 manually from https://www.python.org/downloads/"
            exit 1
        }
    }
}
function Install-Gnupg {
    try {
        python -c "import gnupg" 2>$null
    } catch {
        Write-Host "[*] Installing python-gnupg..."
        python -m pip install --user python-gnupg
    }
}

# --- Install dependencies ---
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    Install-Git
} else {
    Write-Host "[*] 'git' found. Checking for updates..."
    Update-Git
}
Install-Python
Install-Gnupg

# --- Install vaultpass ---
Write-Host "[*] Downloading vaultpass files from GitHub..."
git clone --depth 1 $repoUrl $installDir
Write-Host "[✔] vaultpass installed successfully!" -ForegroundColor Green

# --- Create launcher (vaultpass.bat) in WindowsApps for global access ---
if (!(Test-Path $binDir)) { New-Item -ItemType Directory -Force -Path $binDir | Out-Null }
$launcherContent = "@echo off`npython `"%USERPROFILE%\.vaultpass\core\vaultpass`" %*"
Set-Content -Path $batPath -Value $launcherContent -Encoding ASCII

Write-Host ""
Write-Host "Open a new terminal (CMD or PowerShell) and run: vaultpass -h" -ForegroundColor Cyan
Write-Host ""
exit 0