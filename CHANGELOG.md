# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI status badge in the READMEs and a ready-to-use social preview image (`data/social-preview.png`, 1280×640).

## [1.2.1] - 2026-11-15

### Added
- **Official asblPixels logo** integrated across the project: app hero banner (Linux + Windows), window/taskbar icon, GNOME icon theme, Windows `.ico`, READMEs (6 languages) and wiki home.
- Multi-size icons (`16`–`512` px) and a multi-resolution Windows icon (`data/ripdvd.ico`).
- Installers now deploy the logo and icons for every desktop size.

### Changed
- Version bumped to 1.2.1.

## [1.2.0] - 2026-11-15

### Added
- **One-line Linux installer** (`scripts/install-linux.sh`): detects Fedora, Arch/Manjaro, Ubuntu/Mint/Pop!_OS and Debian, then installs the right packages, the app, the icon and the menu entry automatically.
- **One-click Windows installer** (`scripts/install-windows.bat`): double-click and follow the guide; checks Python and HandBrake, creates Desktop and Start Menu shortcuts.
- **Complete "About" window** (Linux + Windows): author (asblPixels), credits, MIT license, privacy, legal notice and support links.
- **asblPixels visual identity**: turquoise/ink theme, gradient hero banner, themed buttons, progress bar and a dedicated application icon (`data/ripdvd.svg`).
- **Multilingual documentation**: README in English, French, Spanish, Russian, Chinese and Japanese, plus a 10-page wiki in `docs/wiki/`.
- **CI regression guard** that fails the build if the GTK window stops setting its content (blank-window bug).
- GitHub Copilot project instructions (`.github/copilot-instructions.md`).

### Changed
- **Instant scan**: only the main feature is analysed and previews are skipped (`--main-feature --previews 0`) — typically 3–10× faster, with automatic fallback to a full scan if needed.
- **Faster encoding**: x264 preset `medium` → `fast` (visually identical on DVD sources, noticeably quicker on modest CPUs).
- Encoding targets the main feature directly (`--main-feature`) instead of a title index.
- READMEs present the app as fully cross-platform (Linux + Windows) with per-platform install steps.
- Branches `arch`, `ubuntu`, `debian` and `windows` kept in sync with `main`.

### Fixed
- **Blank white window** caused by a missing `self.set_content(box)` call — fixed and covered by CI.
- Removed the confusing HandBrake path/source line from the main window.

### Removed
- The redundant "asblPixels" pill button from the main window (branding now lives in the hero banner, the footer and the About window).

## [1.1.0] - 2026-11-15

### Added
- **Reprendre** (Resume) button: retry the last encode with the same parameters (title, audio, subtitles).
- **Quitter** (Quit) button: close the application cleanly, stopping any running encode first.
- Clearer README: supported systems table, step-by-step download/install instructions, verification commands.

## [1.0.0] - 2026-11-15

### Added
- Initial release.
- GTK4/libadwaita GUI (`src/ripdvd.py`) wrapping HandBrakeCLI.
- Automatic detection of the longest title (main movie).
- Multi-language audio track selection (French preferred, then English).
- Optional subtitle passthrough.
- Chapter markers preserved in MKV output.
- Live output window (real-time HandBrakeCLI log with auto-scroll).
- Progress bar with percentage.
- Stop/cancel button.
- Rescan button.
- Thread-safe UI updates (GLib.idle_add).
- Headless CLI script (`src/ripdvd-cli.sh`).
- Fedora installer (`scripts/install.sh`) with native/Flatpak HandBrake fallback.
- Debug log at `~/.ripdvd-debug.log`.
- GNOME `.desktop` entry.
- CI workflow (Python syntax + shellcheck).
- Issue templates and contributing guide.

### Fixed
- Removed invalid `--chapters` flag (was causing "missing parameter").
- Single-pass scan (removed second HandBrake invocation that caused "Missing output file name").
- Track parsing now correctly associates audio/subtitle lines with the main title.
- Thread-safety fixes to prevent GTK segfaults.
