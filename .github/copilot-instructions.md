# Copilot instructions — RipDvD

RipDvD is a deliberately minimal DVD ripper: **one disc, one click, one MKV**.
It wraps `HandBrakeCLI` and ships as a native GUI on Linux (GTK4/libadwaita) and
Windows (tkinter), plus a headless shell CLI.

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/ripdvd.py` | Linux GUI — GTK4 + libadwaita (`Adw.ApplicationWindow`) |
| `src/ripdvd-win.py` | Windows GUI — tkinter, no external dependency |
| `src/ripdvd-cli.sh` | Headless bash ripper (no GUI) |
| `scripts/install.sh` | Fedora installer (native or Flatpak HandBrake) |
| `scripts/install-arch.sh` | Arch / Manjaro installer |
| `scripts/install-ubuntu.sh` | Ubuntu / Mint / Pop!_OS installer |
| `scripts/install-debian.sh` | Debian installer |
| `scripts/install-linux.sh` | Universal one-line installer (auto-detects the distro) |
| `scripts/install-windows.bat` | Double-click Windows installer |
| `scripts/install-windows.ps1` | PowerShell installer (manual path) |
| `data/ripdvd.desktop` | GNOME desktop entry (`Icon=ripdvd`) |
| `data/ripdvd.svg` | Application icon (asblPixels turquoise) |
| `docs/wiki/` | Wiki sources (Home, Installation, Usage, …) |
| `.github/workflows/ci.yml` | Syntax, lint and blank-window regression checks |

## Product rules (do not regress)

1. **Zero configuration.** The user inserts a disc, clicks *Rip DVD*, gets an MKV.
   Never add mandatory dialogs or advanced settings before the main action.
2. **Automatic main-movie detection.** The longest title is the target. Encoding uses
   `--main-feature`, never a hard-coded title index.
3. **Fast scan is mandatory.** Scan with `--main-feature --previews 0`; if parsing yields
   no duration, fall back to `--title 0 --previews 0`. Never reintroduce a full scan with
   previews on the happy path.
4. **Output contract:** MKV, H.264 (x264, RF 20), native DVD resolution, source frame rate,
   chapters preserved, all detected audio/subtitles available, saved to `~/Vidéos/Rips`
   (`%USERPROFILE%\Videos\Rips` on Windows).
5. **Thread safety.** Worker threads must never touch widgets directly:
   Linux uses `GLib.idle_add(...)`, Windows uses `self.after(0, ...)`.
6. **Never remove `self.set_content(box)`** in `RipdvDWindow.__init__` (Linux):
   without it the window shows up blank/white. CI checks this.
7. **Buttons required in the UI:** Rip, Stop, Resume (Reprendre), Rescan, Clear log,
   About (À propos), Quit (Quitter). Labels are French on Linux, English on Windows.
8. **Branding.** asblPixels must be visible in the app (hero banner caption, footer and
   About window) but must never block the workflow. Palette: turquoise `#00C9A0` /
   `#00E0B0` on ink `#04302A`.
9. **Legal.** The About window must keep: author/asblPixels, version, MIT license,
   privacy (no data collected, no network), legal notice (backup of owned DVDs,
   local laws) and support links.

## Coding conventions

- Python 3.10+, standard library only, no new third-party dependency.
- Keep the UI construction in `_build_ui`-style methods and the process handling in
  `*_worker` methods executed in daemon threads.
- User-facing strings: French for the Linux app, English for the Windows app.
- Shell scripts: POSIX-friendly bash, `set -e`, quote variables, idempotent.
- Never commit credentials or tokens. The installers must not contain secrets.

## Review checklist

- [ ] App launches without a traceback (Linux needs `python3-gobject`, `gtk4`, `libadwaita`).
- [ ] `python3 -m py_compile src/ripdvd.py src/ripdvd-win.py` passes.
- [ ] `bash -n scripts/*.sh` passes.
- [ ] The GTK window still calls `self.set_content(box)`.
- [ ] Scan and encode commands still include `--main-feature` and `--previews 0` for the scan.
- [ ] All branches (`main`, `arch`, `ubuntu`, `debian`, `windows`) stay in sync.

## Out of scope

- Adding network features, telemetry, accounts or cloud services.
- Bundling HandBrake binaries inside the repository.
- Breaking the single-file/single-click philosophy in the name of flexibility.
