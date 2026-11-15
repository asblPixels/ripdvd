<div align="center">

# 🎬 ripdvd

### One click. One DVD. One MKV file.

**A minimalist, open-source DVD ripper for Linux (Fedora / GNOME)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Fedora%20Linux-blue.svg)](https://fedoraproject.org/)
[![Desktop](https://img.shields.io/badge/desktop-GNOME%2049-green.svg)](https://gnome.org/)
[![GUI](https://img.shields.io/badge/GUI-GTK4%20%2F%20libadwaita-teal.svg)](https://gnome.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Backend](https://img.shields.io/badge/backend-HandBrakeCLI-orange.svg)](https://handbrake.fr/)
[![Release](https://img.shields.io/github/v/release/asblPixels/ripdvd.svg)](https://github.com/asblPixels/ripdvd/releases)
[![Stars](https://img.shields.io/github/stars/asblPixels/ripdvd.svg?style=social)](https://github.com/asblPixels/ripdvd)

<br>

[🇬🇧 English](README.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇷🇺 Русский](README.ru.md) · [🇨🇳 中文](README.zh.md) · [🇯🇵 日本語](README.ja.md)

</div>

---

## 📖 About

**ripdvd** is a free, open-source, minimalist DVD ripping application built for Linux.
It provides a clean, native GNOME (GTK4 / libadwaita) graphical interface on top of
[HandBrakeCLI](https://handbrake.fr/), turning your DVD collection into high-quality
MKV files ready for your home media server (Jellyfin, Kodi, Plex).

> **Origin**: This project is created and maintained by **[asblPixels](https://github.com/asblPixels)**
> as part of its open-source software initiative. It is released under the MIT License
> and is free to use, modify and distribute.

### ✨ Why ripdvd?

Most DVD rippers on Linux are either command-line only, overly complex, or Windows-only.
ripdvd aims to be **the simplest possible tool**: insert a disc, click one button,
get a perfect MKV. No configuration required, but full control when you want it.

## 🎯 Features

- 🖱️ **One-click ripping** — insert a DVD, click *Rip DVD*, get a ready-to-stream MKV.
- 🔍 **Automatic title detection** — picks the longest title (the main movie) automatically.
- 🌍 **Multi-language audio** — detects every audio track; French preferred by default, then English.
- 💬 **Subtitles** — optional passthrough of any subtitle track (VobSub), or none.
- 📑 **Chapter markers** — preserved in the MKV for easy navigation in Jellyfin/Kodi.
- 📺 **Live output window** — real-time HandBrakeCLI log (tail) with auto-scroll.
- 📊 **Progress bar** — percentage updated live during encoding.
- ⏸️ **Stop button** — cancel an in-progress encode at any time.
- 🔄 **Resume button** — retry the last encode with the same parameters.
- 🚪 **Quit button** — close the app cleanly (stops any running encode first).
- 🔄 **Rescan button** — re-analyse the disc without restarting the app.
- 🧹 **Clear log** — clear the live output window.
- 🎨 **Native GNOME look** — GTK4 + libadwaita, fits perfectly on Fedora Workstation.
- 🧵 **Thread-safe** — all UI updates marshalled to the GTK main thread.
- 🐛 **Debug log** — full output saved to `~/.ripdvd-debug.log`.

## 📋 Default output profile

| Parameter | Value |
|---|---|
| Container | MKV (Matroska) |
| Video codec | H.264 (x264), RF 20, preset `medium` |
| Resolution | Native DVD (480p NTSC / 576p PAL) — no upscaling |
| Framerate | Source (25 / 29.97 fps) |
| Audio | Passthrough (copy) — keeps original 5.1 when present |
| Subtitles | Passthrough (optional) |
| Chapters | Preserved |
| Typical size | ~1.0 – 1.5 GB per 2-hour movie |

> 💡 DVDs are SD sources. Keeping native resolution avoids artificial upscaling and keeps
> files small while looking great on any TV.

## 🖥️ Supported systems

| Component | Requirement |
|---|---|
| **Operating system** | Fedora 43+ (tested on Fedora 45). Any recent Fedora/RHEL-based distro should work. |
| **Desktop** | GNOME (GTK4/libadwaita). Works on X11 and Wayland. |
| **Architecture** | x86_64 |
| **CPU** | Any x86_64 (software encoding via x264). No GPU required. |
| **RAM** | 2 GB minimum, 4 GB recommended |
| **Disk** | ~1.5 GB free per movie (output) + ~8 GB temp during encoding |
| **Optical drive** | Internal or USB DVD reader (appears as `/dev/sr0`) |

### Supported distributions

This repository provides distribution-specific branches with adapted installers:

| Branch | Distribution | Install script |
|---|---|---|
| `main` / `fedora` | Fedora 43+ | `scripts/install.sh` |
| `arch` | Arch Linux | `scripts/install-arch.sh` |
| `ubuntu` | Ubuntu 22.04+ | `scripts/install-ubuntu.sh` |
| `debian` | Debian 12+ | `scripts/install-debian.sh` |
| `windows` | Windows 10/11 | `scripts/install-windows.ps1` |

To use a specific branch:

```bash
git clone -b <branch> https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install-<distro>.sh   # or .ps1 on Windows
```

## 🚀 Installation

### Step 1 — Download

```bash
git clone https://github.com/asblPixels/ripdvd.git
cd ripdvd
```

> Don't have `git`? Download the ZIP from
> https://github.com/asblPixels/ripdvd/archive/refs/heads/main.zip and extract it.

### Step 2 — Install dependencies

```bash
sudo dnf install -y python3 python3-gobject gtk4 libadwaita zenity HandBrake HandBrake-cli
```

For encrypted commercial DVDs, also install `libdvdcss`:

```bash
sudo dnf install -y rpmfusion-free-release-tainted
sudo dnf install -y libdvdcss
```

### Step 3 — Run the installer

```bash
bash scripts/install.sh
```

The installer will:
1. Verify Python/GTK dependencies.
2. Install HandBrake (native, with Flatpak fallback if native is unavailable).
3. Copy the app to `~/.local/bin/ripdvd-gui.py`.
4. Register a GNOME menu entry (`ripdvd`).

### Step 4 — Launch

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

Or search for **ripdvd** in the GNOME application menu.

### Windows

For Windows 10/11, use the `windows` branch:

```powershell
git clone -b windows https://github.com/asblPixels/ripdvd.git
cd ripdvd
.\scripts\install-windows.ps1
```

Or download the ZIP from https://github.com/asblPixels/ripdvd/archive/refs/heads/windows.zip

#### Step 1 — Install Python

1. Download Python 3.10+ from https://www.python.org/downloads/
2. Run the installer.
3. **Important**: Check **"Add Python to PATH"** during installation.
4. Verify: open PowerShell and run `python --version`

#### Step 2 — Install HandBrake

1. Download HandBrake for Windows from https://handbrake.fr/downloads.php
2. Run the installer (default location: `C:\Program Files\HandBrake\`).
3. Verify: `Get-Command HandBrakeCLI` in PowerShell.

#### Step 3 — Run the installer

Open PowerShell (as current user, no admin needed) and run:

```powershell
cd ripdvd
.\scripts\install-windows.ps1
```

The installer will:
1. Verify Python is installed and in PATH.
2. Verify HandBrakeCLI is available.
3. Create the output directory (`%USERPROFILE%\Videos\Rips`).
4. Copy the app to `%LOCALAPPDATA%\ripdvd\ripdvd.py`.
5. Create a Desktop shortcut and Start Menu entry.

#### Step 4 — Launch

Double-click the **ripdvd** shortcut on your Desktop, or search for **ripdvd** in the Start Menu.

Or from PowerShell:
```powershell
python "$env:LOCALAPPDATA\ripdvd\ripdvd.py"
```

#### Windows notes

- The Windows version uses **tkinter** (built into Python) instead of GTK4, so the UI looks different from the Linux version but has the same features.
- DVD drive detection is automatic (scans for CD-ROM drives). If not detected, enter the drive letter manually (e.g., `D:\`).
- libdvdcss is included with HandBrake for Windows — no separate installation needed.
- Output files are saved to `%USERPROFILE%\Videos\Rips\`.

### Verify everything works (all platforms)

```bash
# Linux
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')"
command -v HandBrakeCLI && echo "HandBrakeCLI OK"

# Windows (PowerShell)
python -c "import tkinter; print('tkinter OK')"
Get-Command HandBrakeCLI
```

## 🎬 Usage

1. Insert a DVD into your drive.
2. Launch **ripdvd** from the GNOME application menu (or `python3 ~/.local/bin/ripdvd-gui.py`).
3. The app scans the disc automatically and detects the main movie (longest title).
4. Pick the **audio language** and optional **subtitles** from the dropdowns.
5. Click **Rip DVD**.
6. Watch the live progress in the log window.
7. The finished MKV lands in `~/Vidéos/Rips/` (or `~/Videos/Rips/`).

### Buttons

| Button | Action |
|---|---|
| **Rip DVD** | Start encoding the selected title. |
| **Arrêter** | Cancel the current encode. |
| **Reprendre** | Resume/retry the last encode with the same parameters. |
| **Quitter** | Close the application (stops any running encode first). |
| **Rescanner** | Re-analyse the disc (useful after swapping DVDs). |
| **Effacer log** | Clear the live output window. |

### CLI version

A headless bash script is also provided for automation:

```bash
bash src/ripdvd-cli.sh
```

It auto-detects the longest title and rips it with the same defaults, showing progress via `zenity`.

## 🗂️ Project structure

```
ripdvd/
├── src/
│   ├── ripdvd.py          # GTK4/libadwaita GUI application
│   └── ripdvd-cli.sh      # Headless CLI ripper
├── scripts/
│   └── install.sh         # Fedora installer
├── data/
│   └── ripdvd.desktop     # GNOME menu entry
├── docs/
│   └── screenshot-main.png
├── .github/
│   ├── workflows/         # CI (syntax checks)
│   └── ISSUE_TEMPLATE/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

## 🐛 Troubleshooting

### App won't start — `ModuleNotFoundError: No module named 'gi'`
Install PyGObject: `sudo dnf install python3-gobject gtk4 libadwaita`

### Segfault / crash on launch
Make sure you're on the latest version (thread-safe UI updates). Re-run `bash scripts/install.sh`.

### DVD not detected (`/dev/sr0` not found)
- Check the drive is connected: `lsblk | grep sr`
- Some USB drives need a moment after insertion; click **Rescanner**.

### Black screen / "cannot read disc" on encrypted DVDs
Install `libdvdcss`:
```bash
sudo dnf install rpmfusion-free-release-tainted
sudo dnf install libdvdcss
```

### Empty output file
Open the debug log (`~/.ripdvd-debug.log`) or click **Voir le log de debug**. The last lines show the HandBrake error. Common causes:
- Missing `libdvdcss` for encrypted discs.
- HandBrake Flatpak without `--device=all` (fixed in current version).
- Insufficient disk space in `~/Vidéos/Rips/`.

### Slow encoding on older CPUs
This is expected — x264 software encoding on a Sandy Bridge i3 takes ~10–15 min per movie. The app uses `medium` preset for a good quality/speed balance. For faster rips, edit `--encoder-preset` to `fast` or `veryfast` in `src/ripdvd.py`.

## 🙏 Acknowledgements

This project would not exist without the incredible work of:

- **[HandBrake](https://handbrake.fr/)** and its team — the encoding engine that powers everything.
- **[libdvdcss](https://www.videolan.org/developers/libdvdcss.html)** (VideoLAN) — DVD decryption.
- **[GNOME / GTK4 / libadwaita](https://gnome.org/)** — the UI toolkit.
- **[RPM Fusion](https://rpmfusion.org/)** — packaging for Fedora.
- **[Fedora Project](https://fedoraproject.org/)** — the operating system.
- All open-source contributors and the community.

## 📚 Sources & references

- HandBrake CLI documentation: https://handbrake.fr/docs/en/latest/cli/
- HandBrake presets reference: https://handbrake.fr/docs/en/latest/technical/video-bframes.html
- libdvdcss documentation: https://www.videolan.org/developers/libdvdcss.html
- GTK4 / libadwaita documentation: https://docs.gtk.org/gtk4/ and https://gnome.pages.gitlab.gnome.org/libadwaita/
- PyGObject documentation: https://pygobject.readthedocs.io/
- RPM Fusion configuration: https://rpmfusion.org/Configuration
- Fedora multimedia guide: https://docs.fedoraproject.org/en-US/quick-docs/assembly_installing-plugins-for-playing-movies-and-music/

## 👨‍💻 Creators

**ripdvd** is created and maintained by **[asblPixels](https://github.com/asblPixels)**
as part of its open-source software initiative.

Contributions, bug reports and feature requests are welcome!

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

## ⚠️ Legal note

This tool is intended for backing up DVDs you own for personal use.
Decrypting copy-protected discs may be restricted in your country. Check your local laws.

---

<div align="center">

Made with ❤️ by [asblPixels](https://github.com/asblPixels) · Open Source · MIT License

</div>
