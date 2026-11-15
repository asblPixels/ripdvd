# ripdvd

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Fedora%20Linux-blue.svg)](https://fedoraproject.org/)
[![GUI](https://img.shields.io/badge/GUI-GTK4%20%2F%20libadwaita-green.svg)](https://gnome.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![HandBrake](https://img.shields.io/badge/backend-HandBrakeCLI-orange.svg)](https://handbrake.fr/)

> **One click. One DVD. One MKV file.**
>
> A minimalist, open-source DVD ripper for Linux (Fedora/GNOME). A clean GTK4/libadwaita GUI
> wrapping [HandBrakeCLI](https://handbrake.fr/) that converts your DVDs into high-quality MKV
> files with chapter markers, multi-language audio and subtitles — optimized for home media
> servers (Jellyfin, Kodi, Plex).

<p align="center">
  <img src="docs/screenshot-main.png" alt="ripdvd main window" width="420">
</p>

---

## ✨ Features

- **One-click ripping** — insert a DVD, click *Rip DVD*, get a ready-to-stream MKV.
- **Automatic title detection** — picks the longest title (the main movie) automatically.
- **Multi-language audio** — detects every audio track and lets you pick the language (French preferred by default, then English).
- **Subtitles** — optional passthrough of any subtitle track (VobSub), or none.
- **Chapter markers** — preserved in the MKV for easy navigation in Jellyfin/Kodi.
- **Live output window** — real-time HandBrakeCLI log (tail) with auto-scroll.
- **Progress bar** — percentage updated live during encoding.
- **Stop button** — cancel an in-progress encode at any time.
- **Native GNOME look** — GTK4 + libadwaita, fits perfectly on Fedora Workstation.
- **Thread-safe** — UI updates are marshalled to the GTK main thread.
- **Rescan button** — re-analyse the disc without restarting the app.
- **Debug log** — full output saved to `~/.ripdvd-debug.log` for troubleshooting.

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

## 🖥️ Requirements

### Supported systems

| Component | Required |
|---|---|
| **Operating system** | Fedora 43+ (tested on Fedora 45). Any recent Fedora/RHEL-based distro should work. |
| **Desktop** | GNOME (GTK4/libadwaita). Works on X11 and Wayland. |
| **Architecture** | x86_64 |
| **CPU** | Any x86_64 (software encoding via x264). No GPU required. |
| **RAM** | 2 GB minimum, 4 GB recommended |
| **Disk** | ~1.5 GB free per movie (output) + ~8 GB temp during encoding |
| **Optical drive** | Internal or USB DVD reader (appears as `/dev/sr0`) |

### Software dependencies

- Python 3.10+
- `python3-gobject`, `gtk4`, `libadwaita`
- `HandBrakeCLI` (native preferred; Flatpak `fr.handbrake.ghb` as fallback)
- `zenity` (error dialogs)
- `libdvdcss` (encrypted commercial DVDs only)

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

### Verify everything works

```bash
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')"
command -v HandBrakeCLI && echo "HandBrakeCLI OK"
```

Both should print `OK`.

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
| **Rescanner** | Re-analyse the disc (useful after swapping DVDs). |
| **Reprendre** | Resume/retry the last encode with the same parameters. |
| **Quitter** | Close the application (stops any running encode first). |

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

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m "feat: add my feature"`.
4. Push and open a Pull Request.

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgements

- [HandBrake](https://handbrake.fr/) — the encoding engine.
- [libdvdcss](https://www.videolan.org/developers/libdvdcss.html) — DVD decryption.
- [GNOME / GTK4 / libadwaita](https://gnome.org/) — the UI toolkit.
- [RPM Fusion](https://rpmfusion.org/) — packaging for Fedora.

---

> ⚠️ **Legal note**: This tool is intended for backing up DVDs you own for personal use.
> Decrypting copy-protected discs may be restricted in your country. Check your local laws.
