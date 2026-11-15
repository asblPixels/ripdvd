# Installation

This page provides detailed installation instructions for all supported systems.

## Prerequisites

Before installing ripdvd, ensure you have:

- A DVD drive (internal or USB)
- An internet connection
- Sudo/administrator privileges

## Fedora (main branch)

### Step 1 — Install dependencies

```bash
sudo dnf install -y python3 python3-gobject gtk4 libadwaita zenity HandBrake HandBrake-cli
```

### Step 2 — Install libdvdcss (for encrypted DVDs)

```bash
sudo dnf install -y rpmfusion-free-release-tainted
sudo dnf install -y libdvdcss
```

### Step 3 — Run the installer

```bash
git clone https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install.sh
```

### Step 4 — Launch

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

Or search for **ripdvd** in the GNOME application menu.

---

## Arch Linux (arch branch)

### Step 1 — Install dependencies

```bash
sudo pacman -Sy --needed python python-gobject gtk4 libadwaita zenity handbrake
```

### Step 2 — Install libdvdcss (from AUR)

```bash
yay -S libdvdcss   # or paru -S libdvdcss
```

### Step 3 — Run the installer

```bash
git clone -b arch https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install-arch.sh
```

### Step 4 — Launch

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

---

## Ubuntu (ubuntu branch)

### Step 1 — Install dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 handbrake-cli zenity
```

### Step 2 — Install libdvdcss

```bash
sudo apt install -y libdvd-pkg
sudo dpkg-reconfigure libdvd-pkg
```

### Step 3 — Run the installer

```bash
git clone -b ubuntu https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install-ubuntu.sh
```

### Step 4 — Launch

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

---

## Debian (debian branch)

### Step 1 — Install dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 handbrake-cli zenity
```

### Step 2 — Install libdvdcss

```bash
sudo apt install -y libdvd-pkg
sudo dpkg-reconfigure libdvd-pkg
```

### Step 3 — Run the installer

```bash
git clone -b debian https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install-debian.sh
```

### Step 4 — Launch

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

---

## Windows (windows branch)

### Step 1 — Install Python

Download and install Python 3.10+ from https://www.python.org/downloads/
Make sure to check **"Add Python to PATH"** during installation.

### Step 2 — Install HandBrake

Download HandBrake for Windows from https://handbrake.fr/downloads.php
Install it (default location is fine).

### Step 3 — Download ripdvd

```powershell
git clone -b windows https://github.com/asblPixels/ripdvd.git
cd ripdvd
```

Or download the ZIP from https://github.com/asblPixels/ripdvd/archive/refs/heads/windows.zip

### Step 4 — Run the installer

Open PowerShell and run:

```powershell
.\scripts\install-windows.ps1
```

The installer will:
1. Verify Python is installed.
2. Verify HandBrakeCLI is available.
3. Create the output directory (`%USERPROFILE%\Videos\Rips`).
4. Copy the app to `%LOCALAPPDATA%\ripdvd\ripdvd.py`.
5. Create Desktop and Start Menu shortcuts.

### Step 5 — Launch

Double-click the **ripdvd** shortcut on your Desktop, or search for **ripdvd** in the Start Menu.

## Verification

After installation, verify everything works:

```bash
# Linux
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')"
command -v HandBrakeCLI && echo "HandBrakeCLI OK"

# Windows (PowerShell)
python -c "import tkinter; print('tkinter OK')"
Get-Command HandBrakeCLI
```

## Troubleshooting installation

See the [Troubleshooting](Troubleshooting) page for common issues.
