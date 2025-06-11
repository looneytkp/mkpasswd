# install.ps1 - Windows installer for vaultpass

$InstallDir = "$HOME\.vaultpass"
$RepoURL = "https://github.com/looneytkp/vaultpass.git"
$BinPath = "$HOME\AppData\Local\Microsoft\WindowsApps"
$Launcher = "$InstallDir\core\vaultpass"

Write-Host "[*] Installing vaultpass..."

# Remove old install
if (Test-Path $InstallDir) {
    Write-Host "[*] Removing previous installation..."
    Remove-Item $InstallDir -Recurse -Force
}

# Ensure Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Git not found. Please install Git manually from https://git-scm.com/"
    exit 1
}

# Ensure Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python not found. Please install Python 3 manually from https://www.python.org/downloads/"
    exit 1
}

# Clone the repo
git clone $RepoURL $InstallDir

# Create launcher path if needed
$ShortcutPath = "$BinPath\vaultpass.ps1"
if (-not (Test-Path $BinPath)) {
    New-Item -ItemType Directory -Force -Path $BinPath | Out-Null
}

# Copy launcher
Copy-Item "$InstallDir\install\vaultpass.ps1" $ShortcutPath -Force

Write-Host ""
Write-Host "[✔] vaultpass installed successfully!"
Write-Host "[*] You can now run 'vaultpass' from PowerShell (you may need to restart your terminal)."