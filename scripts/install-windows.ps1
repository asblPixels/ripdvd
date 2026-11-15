# install-ripdvd.ps1 — installs ripdvd on Windows
# Run in PowerShell as Administrator or current user

$ErrorActionPreference = "Stop"

Write-Host "=== ripdvd Windows Installer ===" -ForegroundColor Cyan

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}
Write-Host "Python found: $($python.Source)" -ForegroundColor Green

# Check HandBrakeCLI
$hb = Get-Command HandBrakeCLI -ErrorAction SilentlyContinue
if (-not $hb) {
    $hbPaths = @(
        "C:\Program Files\HandBrake\HandBrakeCLI.exe",
        "C:\Program Files (x86)\HandBrake\HandBrakeCLI.exe",
        "$env:LOCALAPPDATA\HandBrake\HandBrakeCLI.exe"
    )
    $found = $false
    foreach ($p in $hbPaths) {
        if (Test-Path $p) { $found = $true; break }
    }
    if (-not $found) {
        Write-Host "HandBrakeCLI not found." -ForegroundColor Yellow
        Write-Host "Please download HandBrake for Windows from https://handbrake.fr/downloads.php"
        Write-Host "Install it, then re-run this script."
        exit 1
    }
}
Write-Host "HandBrakeCLI found." -ForegroundColor Green

# Create output directory
$outDir = Join-Path $env:USERPROFILE "Videos\Rips"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    Write-Host "Created output directory: $outDir"
}

# Copy application
$installDir = Join-Path $env:LOCALAPPDATA "ripdvd"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}
Copy-Item -Path "src\ripdvd-win.py" -Destination "$installDir\ripdvd.py" -Force
Write-Host "Installed to $installDir\ripdvd.py" -ForegroundColor Green

# Create shortcut on Desktop
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\ripdvd.lnk")
$shortcut.TargetPath = "python"
$shortcut.Arguments = "`"$installDir\ripdvd.py`""
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = "python,0"
$shortcut.Save()
Write-Host "Desktop shortcut created." -ForegroundColor Green

# Create Start Menu entry
$startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$shortcut2 = $WshShell.CreateShortcut("$startMenu\ripdvd.lnk")
$shortcut2.TargetPath = "python"
$shortcut2.Arguments = "`"$installDir\ripdvd.py`""
$shortcut2.WorkingDirectory = $installDir
$shortcut2.IconLocation = "python,0"
$shortcut2.Save()
Write-Host "Start Menu entry created." -ForegroundColor Green

Write-Host ""
Write-Host "=== Installation complete ===" -ForegroundColor Cyan
Write-Host "Launch ripdvd from the Desktop shortcut or Start Menu."
Write-Host "Output files will be saved to: $outDir"
Write-Host ""
Write-Host "Note: For encrypted DVDs, ensure libdvdcss is available."
Write-Host "HandBrake for Windows includes libdvdcss support."
