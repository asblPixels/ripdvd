# Changelog

All notable changes to RipDvD are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Manual title selection
- Hardware encoding (QSV/NVENC)
- Configuration file
- Multiple title queue

## [1.2.1] - 2026-11-15

### Added
- Official asblPixels logo in the app, icons, READMEs and wiki.

### Changed
- Version bumped to 1.2.1.

## [1.2.0] - 2026-11-15

### Added
- One-line Linux installer (auto-detects Fedora, Arch, Ubuntu, Debian — and derivatives).
- Double-click Windows installer (`install-windows.bat`).
- Complete "About" window: author asblPixels, credits, MIT license, privacy, legal notice, support links.
- asblPixels turquoise/ink visual identity, themed widgets, hero banner and application icon.
- README in 6 languages and a 10-page wiki.
- CI guard against the blank-window regression.
- GitHub Copilot project instructions.

### Changed
- Instant scan: main feature only, no previews (`--main-feature --previews 0`), with full-scan fallback.
- Faster encoding preset (`medium` → `fast`).
- Encoding targets `--main-feature` instead of a title index.
- Documentation presents the project as cross-platform (Linux + Windows).

### Fixed
- Blank white window (missing `self.set_content(box)`).
- Removed the HandBrake source line from the main window.

### Removed
- Redundant "asblPixels" pill button from the main window.

## [1.1.0] - 2026-11-15

### Added
- **Reprendre** (Resume) button: retry the last encode with the same parameters.
- **Quitter** (Quit) button: close the application cleanly.
- Supported distributions table in README (Fedora, Arch, Ubuntu, Debian, Windows).
- Branch usage guide in README.
- Multilingual READMEs (French, Spanish, Russian, Chinese, Japanese).
- Credits, acknowledgements, and source references in README.
- Wiki documentation.

### Changed
- Improved README with step-by-step installation instructions.
- Added system requirements table.

## [1.0.0] - 2026-11-15

### Added
- Initial release.
- GTK4/libadwaita GUI (`src/ripdvd.py`) wrapping HandBrakeCLI.
- Automatic detection of the main movie (longest title).
- Multi-language audio track selection (French preferred, then English).
- Optional subtitle passthrough.
- Chapter markers preserved in MKV output.
- Live output window (real-time HandBrakeCLI log with auto-scroll).
- Progress bar with percentage.
- Stop/cancel button.
- Rescan button.
- Thread-safe UI updates (GLib.idle_add).
- Headless CLI script (`src/ripdvd-cli.sh`).
- Fedora installer (`scripts/install.sh`).
- Debug log at `~/.ripdvd-debug.log`.
- GNOME `.desktop` entry.
- CI workflow (Python syntax + shellcheck).
- Issue templates and contributing guide.
- Windows port (`src/ripdvd-win.py`) with tkinter.
- Windows PowerShell installer (`scripts/install-windows.ps1`).
- Arch, Ubuntu, Debian install scripts.

### Fixed
- Removed invalid `--chapters` flag (was causing "missing parameter").
- Single-pass scan (removed second HandBrake invocation that caused "Missing output file name").
- Track parsing now correctly associates audio/subtitle lines with the main title.
- Thread-safety fixes to prevent GTK segfaults.

### Changed
- README rewritten with comprehensive documentation.
- Supported systems table added.
- Installation guide made step-by-step.

## Pre-release (development)

### 2026-11-15 (early)
- Initial prototype: bash script with zenity.
- First GTK4 version with basic rip functionality.
- Added libdvdcss support via RPM Fusion tainted.
- Added multi-language audio selection.
- Added subtitle passthrough.
- Added live output window.
- Added progress bar.
- Fixed thread-safety issues (segfault).
- Created GitHub repository.
- Added CI/CD pipeline.

---

For the full commit history, see the [GitHub commits page](https://github.com/asblPixels/ripdvd/commits/main).
