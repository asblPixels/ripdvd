# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
