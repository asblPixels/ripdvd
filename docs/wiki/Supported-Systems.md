# Supported Systems

This page documents the compatibility matrix for RipDvD across different systems.

## Operating systems

| OS | Version | Branch | Status | Notes |
|---|---|---|---|---|
| Fedora | 43+ | `main` | ✅ Tested | Primary development platform |
| Arch Linux | Rolling | `arch` | ✅ Supported | Via pacman + AUR |
| Ubuntu | 22.04+ | `ubuntu` | ✅ Supported | Via apt |
| Debian | 12+ | `debian` | ✅ Supported | Via apt |
| Windows | 10/11 | `windows` | ✅ Supported | tkinter port, PowerShell installer |
| Linux Mint | 21+ | `ubuntu` | ⚠️ Untested | Should work (Ubuntu-based) |
| Pop!_OS | 22.04+ | `ubuntu` | ⚠️ Untested | Should work (Ubuntu-based) |
| openSUSE | Leap 15.5+ | — | ⚠️ Untested | Manual install needed |
| Manjaro | Rolling | `arch` | ⚠️ Untested | Should work (Arch-based) |

## Desktop environments

| DE | Status | Notes |
|---|---|---|
| GNOME 45+ | ✅ Full support | Primary target |
| KDE Plasma | ✅ Works | GTK4 apps run fine |
| XFCE | ✅ Works | GTK4 apps run fine |
| Cinnamon | ✅ Works | GTK4 apps run fine |
| MATE | ✅ Works | GTK4 apps run fine |

## Architecture

| Architecture | Status |
|---|---|
| x86_64 (amd64) | ✅ Supported |
| aarch64 (ARM64) | ⚠️ Untested | HandBrakeCLI must be available for ARM |
| i686 (32-bit) | ❌ Not supported | HandBrake no longer builds for 32-bit |

## Hardware

| Component | Minimum | Recommended |
|---|---|---|
| CPU | Any x86_64 | Intel Core i5 or AMD Ryzen 5 (4+ cores) |
| RAM | 2 GB | 4 GB+ |
| Disk | 10 GB free | 50 GB+ (for large collections) |
| Optical drive | USB DVD reader | Internal SATA DVD drive |
| GPU | None required | Any (for future hardware encoding) |

## Encoding performance

| CPU | Preset | Time per 2h movie |
|---|---|---|
| Intel i3-2330M (Sandy Bridge, 2 cores) | medium | ~15-20 min |
| Intel i5 (4 cores) | medium | ~8-12 min |
| Intel i7 / AMD Ryzen 5 (6+ cores) | medium | ~4-6 min |
| Intel i7 / AMD Ryzen 5 (6+ cores) | fast | ~2-3 min |

> Note: Times are approximate and depend on disc read speed, disk I/O, and system load.

## Known limitations

1. **No hardware encoding** — Currently uses software x264 only. Intel QSV and NVIDIA NVENC are detected but not used (planned for future release).
2. **No Blu-ray support** — Only DVD (VIDEO_TS) is supported. Blu-ray (BDMV) is not yet supported.
3. **Single title selection** — The app auto-selects the longest title. Manual title selection is planned.
4. **No resume of partial encodes** — "Resume" re-encodes from scratch. True resume is not supported by HandBrakeCLI.
5. **Windows port uses tkinter** — The Windows version uses tkinter instead of GTK4, so the UI looks different from the Linux version.
6. **No macOS support** — Not currently planned, but contributions are welcome.

## Tested configurations

| Configuration | Status | Date |
|---|---|---|
| Fedora 45, GNOME 49, i3-2330M | ✅ Tested | 2026-11-15 |
| Fedora 45, GNOME 49, x86_64 (VM) | ⚠️ Partial | 2026-11-15 |
