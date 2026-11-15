<div align="center">

<img src="data/logo.png" width="220" alt="RipDvD logo">

# 🎬 RipDvD

### From disc to digital — effortlessly.

**A minimalist, open-source DVD ripper for Linux & Windows (Fedora, Arch, Ubuntu, Debian, Windows)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%26%20Windows-blue.svg)](https://github.com/asblPixels/ripdvd)
[![Desktop](https://img.shields.io/badge/desktop-GNOME%2049-green.svg)](https://gnome.org/)
[![GUI](https://img.shields.io/badge/GUI-GTK4%20%2F%20libadwaita-teal.svg)](https://gnome.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Backend](https://img.shields.io/badge/backend-HandBrakeCLI-orange.svg)](https://handbrake.fr/)
[![CI](https://github.com/asblPixels/ripdvd/actions/workflows/ci.yml/badge.svg)](https://github.com/asblPixels/ripdvd/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/asblPixels/ripdvd.svg)](https://github.com/asblPixels/ripdvd/releases)
[![Stars](https://img.shields.io/github/stars/asblPixels/ripdvd.svg?style=social)](https://github.com/asblPixels/ripdvd)

<br>

[🇬🇧 English](README.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇷🇺 Русский](README.ru.md) · [🇨🇳 中文](README.zh.md) · [🇯🇵 日本語](README.ja.md)

</div>

---

## 📖 About

**RipDvD** is a free, open-source, minimalist DVD ripping application built for Linux and Windows.
It provides a clean, native GUI (GTK4 / libadwaita on Linux, tkinter on Windows) on top of
[HandBrakeCLI](https://handbrake.fr/), turning your DVD collection into high-quality
MKV files ready for your home media server (Jellyfin, Kodi, Plex).

> **Origin**: This project is created and maintained by **[asblPixels](https://github.com/asblPixels)**
> as part of its open-source software initiative. It is released under the MIT License
> and is free to use, modify and distribute.

### ✨ Why RipDvD?

Most DVD rippers are either command-line only, overly complex, platform-locked, or Windows-only.
RipDvD aims to be **the simplest possible tool** that works everywhere: insert a disc, click one button,
get a perfect MKV. No configuration required, but full control when you want it.
It runs on **Fedora, Arch, Ubuntu, Debian** (Linux) and **Windows 10/11**.

### 📺 Your own streaming service — built from your shelf

Subscriptions go up, ads creep in, and films vanish from catalogues overnight.
Meanwhile, your DVDs are gathering dust. RipDvD turns them into the first brick of **your own home streaming service**:

```
  📀 Your DVDs  ──►  🎬 RipDvD (one click)  ──►  🗄️ Jellyfin / Kodi / Plex  ──►  📺 TV · 📱 phone · 💻 tablet
```

- 💸 **No monthly fee** — free tools, an old recycled PC is enough as a server.
- 🔒 **Nothing disappears** — your films stay in your library, not in someone's catalogue.
- 🌐 **Works offline** — everything lives at home, on your network.
- 👨‍👩‍👧 **For the whole household** — every screen in the house gets the same library.
- 🖼️ **Media-server friendly** — clean MKV files with chapters; Jellyfin/Kodi fetch posters and summaries automatically.
- 🏡 **Save family memories** — home-made DVDs (weddings, birthdays, first steps) don't last forever. Digitise them before they fade.

## 🎯 Features

- 🖱️ **One click** — insert a DVD: the movie is detected, the language is pre-selected, just click *Numériser le film* (Digitise the movie).
- ⚡ **Instant scan** — only the main movie is analysed, no preview generation (3–10× faster).
- 🔍 **Automatic title detection** — picks the longest title (the main movie) automatically.
- 🌍 **Languages at hand** — audio and subtitles chosen right above the button, with readable names ("Français · 5.1"); French by default, then English.
- 📑 **Chapter markers** — preserved in the MKV for easy navigation in Jellyfin/Kodi.
- 📊 **Clear progress** — large percentage and estimated time remaining.
- ⏸️ **Stop / Resume** — interrupt at any time, restart with the same settings.
- 🧹 **Clean interface** — secondary options (rescan, movies folder, log) live in the ☰ menu.
- 🎨 **Native GNOME look** — GTK4 + libadwaita, light and dark themes, asblPixels turquoise accent.
- ℹ️ **About window** — author, credits, license, privacy and legal notice in one place.
- 🧵 **Thread-safe** — all UI updates marshalled to the GTK main thread.
- 🐛 **Debug log** — full output saved to `~/.ripdvd-debug.log`.

## 📋 Default output profile

| Parameter | Value |
|---|---|
| Container | MKV (Matroska) |
| Video codec | H.264 (x264), RF 20, encoder preset `fast` (`medium` in the CLI script) |
| Resolution | Native DVD (480p NTSC / 576p PAL) — no upscaling |
| Framerate | Source (25 / 29.97 fps) |
| Audio | Passthrough (copy) of AC3, DTS and MP2 tracks — keeps the original 5.1; LPCM tracks are converted to AAC |
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

### ⚡ One-line install (recommended)

**Copy-paste this single command into your terminal:**

```bash
curl -fsSL https://raw.githubusercontent.com/asblPixels/ripdvd/main/scripts/install-linux.sh | bash
```

That's it! The installer will:
1. Detect your Linux distribution automatically.
2. Install all required dependencies.
3. Download and install RipDvD.
4. Set up a menu entry.

> **No technical knowledge required.** Just paste and press Enter.

### Step 1 — Download (manual)

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

Or search for **RipDvD** in the GNOME application menu.

### Windows

**No technical knowledge required!** Just 3 steps:

1. **Download** the ZIP: https://github.com/asblPixels/ripdvd/archive/refs/heads/main.zip
2. **Extract** it to a folder (e.g., your Desktop).
3. **Double-click** `scripts\install-windows.bat` and follow the on-screen instructions.

That's it! A **RipDvD** shortcut will appear on your Desktop. Double-click it to start ripping DVDs.

> The installer automatically checks for Python and HandBrake, and guides you if anything is missing.

#### Manual steps (if the installer doesn't work)

1. **Install Python**: Download from https://www.python.org/downloads/ — check "Add Python to PATH".
2. **Install HandBrakeCLI** (command line version): `winget install HandBrake.HandBrake.CLI`, or download it from https://handbrake.fr/downloads2.php
3. **Run the app**: from the extracted RipDvD folder, `python src\ripdvd-win.py`

#### Windows notes

- The Windows version uses **tkinter** (built into Python) instead of GTK4.
- DVD drive detection is automatic. If not detected, enter the drive letter manually (e.g., `D:\`).
- libdvdcss is **not** included with HandBrake for Windows: for copy-protected DVDs, place `libdvdcss-2.dll` next to `HandBrakeCLI.exe`.
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

1. Insert a DVD and launch **RipDvD**: the disc is scanned automatically.
2. The **Film détecté** (movie detected) screen shows the runtime and offers the **audio language** and **subtitles** (pre-set: French, no subtitles).
3. Click **Numériser le film**.
4. Follow the percentage and time remaining. **Arrêter** stops the encode.
5. When done, click **Ouvrir le dossier**: the MKV is in `~/Vidéos/Rips/`.

### The ☰ menu

| Entry | Shortcut | Action |
|---|---|---|
| **Analyser le disque** | Ctrl+R | Re-scan the disc (after swapping DVDs). |
| **Ouvrir le dossier des films** | — | Open `~/Vidéos/Rips/`. |
| **Afficher le journal** | Ctrl+L | Show the live HandBrakeCLI output. |
| **À propos de RipDvD** | — | Version, credits, license, privacy. |
| **Quitter** | Ctrl+Q | Close RipDvD (asks for confirmation during an encode). |

After a failure or a stop, the screen offers **Réessayer** / **Reprendre** with the same settings.

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
This is expected — x264 software encoding on a Sandy Bridge i3 takes ~10–15 min per movie. The app uses the `fast` encoder preset for a good quality/speed balance. For even faster rips, edit `--encoder-preset` to `veryfast` in `src/ripdvd.py`.

## 🤝 Need a hand?

RipDvD is made by **Pixel's ASBL**, a nonprofit digital-inclusion workshop in Boussu, Belgium.
No DVD drive, or you'd rather not do it yourself? Visit our workshop — we digitise your family videos
and help you set up your home media server (Jellyfin/Kodi).

📍 Rue Alfred Dendal 56, 7300 Boussu (BE) · 📞 +32 456 96 03 28 · ✉️ info@asblpixels.be · [Facebook](https://www.facebook.com/asblpixels)

⭐ **Like the project? Star the repo** — it's the easiest way to help other people find it.

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

**RipDvD** is created and maintained by **[asblPixels](https://github.com/asblPixels)**
as part of its open-source software initiative.

Contributions, bug reports and feature requests are welcome!

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

## ⚠️ Legal note

RipDvD is intended for making personal copies of DVDs **you own**, for use within **your own household**.

- ✅ Home-made and unprotected discs (family videos, your own recordings) — no restriction.
- ⚠️ Commercial DVDs are usually copy-protected (CSS). Decrypting them may be restricted in your country, even for a private copy. Check your local laws.
- ❌ Do not share ripped films outside your household (e.g. opening your media server to other people). RipDvD is not a piracy tool and must not be used as one.

---

<div align="center">

Made with ❤️ by [asblPixels](https://github.com/asblPixels) · Open Source · MIT License

</div>
