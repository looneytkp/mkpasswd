$installPath = "$env:USERPROFILE\.vaultpass"
$binPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\vaultpass.ps1"
$repoURL = "https://github.com/looneytkp/vaultpass.git"

function Install-Vaultpass {
    Write-Host "`n[*] Installing vaultpass..."

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "[*] Git not found. Installing via winget..."
        winget install --id Git.Git -e --source winget
    }

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "[*] Python not found. Installing via winget..."
        winget install --id Python.Python.3 -e --source winget
    }

    Write-Host "[*] Installing python-gnupg..."
    python -m pip install --user python-gnupg

    if (Test-Path $installPath) { Remove-Item -Recurse -Force $installPath }

    git clone $repoURL $installPath

    $launcher = "$installPath\install\vaultpass.ps1"
    Copy-Item $launcher $binPath -Force

    Write-Host "`n[✔] vaultpass installed successfully!"
    Write-Host "[*] Open a new terminal and run: vaultpass"
}

function Uninstall-Vaultpass {
    Write-Host "`n[*] Uninstalling vaultpass..."

    if (Test-Path $binPath) { Remove-Item $binPath -Force }
    if (Test-Path $installPath) { Remove-Item -Recurse -Force $installPath }

    $choice = Read-Host "[?] Also uninstall Git and Python? (y/N)"
    if ($choice -match '^(y|Y)$') {
        winget uninstall --id Git.Git -e
        winget uninstall --id Python.Python.3 -e
    }

    Write-Host "[✔] vaultpass fully uninstalled."
}

if (Test-Path $installPath) {
    Write-Host "`nvaultpass is already installed."
    Write-Host "What would you like to do?"
    Write-Host "1) Reinstall vaultpass"
    Write-Host "2) Uninstall vaultpass"
    Write-Host "3) Cancel"
    $opt = Read-Host "[?] Choose an option (1/2/3)"
    switch ($opt) {
        "1" {
            Uninstall-Vaultpass
            Install-Vaultpass
        }
        "2" { Uninstall-Vaultpass }
        default { Write-Host "[*] Action cancelled." }
    }
}
else {
    Install-Vaultpass
}