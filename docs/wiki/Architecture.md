# Architecture

This page documents the code structure and how RipDvD works internally.

## Overview

RipDvD is a Python application with a GUI frontend and a HandBrakeCLI backend. The architecture is simple:

```
┌─────────────────────────────────────────┐
│           GUI (GTK4/libadwaita)          │
│  ┌─────────────────────────────────┐    │
│  │  RipdvdWindow (Adw.ApplicationWindow) │
│  │  - Buttons, combos, progress bar │    │
│  │  - Live output TextView         │    │
│  └────────────┬────────────────────┘    │
│               │                          │
│  ┌────────────▼────────────────────┐    │
│  │  Worker Threads (threading)     │    │
│  │  - _scan_worker()               │    │
│  │  - _encode_worker()             │    │
│  │  - _resume_worker()             │    │
│  └────────────┬────────────────────┘    │
│               │ subprocess.Popen        │
│  ┌────────────▼────────────────────┐    │
│  │  HandBrakeCLI (external)        │    │
│  │  - DVD scanning                 │    │
│  │  - Video encoding               │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## File structure

```
src/ripdvd.py          # Main application (Linux: GTK4/libadwaita)
src/ripdvd-win.py      # Windows port (tkinter)
src/ripdvd-cli.sh      # Headless CLI ripper
```

## Key components

### RipDvD.py (Linux)

#### Class: `RipdvdWindow(Adw.ApplicationWindow)`

The main application window. Contains:

- **UI elements**: title, subtitle, source label, status label, audio combo, subtitle combo, progress bar, buttons, output label, live log view.
- **State**: `hb` (HandBrake command), `process` (current subprocess), `encoding`, `scanning`, `audio_tracks`, `sub_tracks`, `best_title`, `best_dur_min`, `last_encode_params`.

#### Key methods

| Method | Thread | Description |
|---|---|---|
| `__init__` | Main | Build UI, auto-scan if DVD present |
| `start_scan` | Main | Validate, start scan thread |
| `_scan_worker` | Worker | Run HandBrakeCLI scan, parse results |
| `_scan_done` | Main (idle) | Update UI with scan results |
| `_scan_failed` | Main (idle) | Show error |
| `on_rip_clicked` | Main | Start encoding |
| `_encode_worker` | Worker | Run HandBrakeCLI encode, stream output |
| `_encode_ok` | Main (idle) | Show success |
| `_encode_failed` | Main (idle) | Show error |
| `on_stop_clicked` | Main | Terminate process |
| `on_resume_clicked` | Main | Resume encode |
| `_resume_worker` | Worker | Run HandBrakeCLI encode (resume) |
| `on_quit_clicked` | Main | Quit application |
| `_append_log` | Any (idle) | Thread-safe log append |
| `_clear_log` | Any (idle) | Thread-safe log clear |
| `_update_progress` | Main (idle) | Update progress bar |
| `parse_title_scan` | Worker | Find longest title |
| `parse_tracks_for_title` | Worker | Extract audio/sub tracks for a title |

### Thread safety

All GTK widget access from worker threads is done via `GLib.idle_add()`:

```python
# Worker thread
GLib.idle_add(self._scan_done)  # schedules on main thread

# Thread-safe log append
def _append_log(self, text):
    def _do():
        end = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end, text)
        ...
        return False  # run once
    GLib.idle_add(_do)
```

### HandBrakeCLI integration

The app communicates with HandBrakeCLI via `subprocess.Popen`:

```python
proc = subprocess.Popen(
    hb + ["-i", "/dev/sr0", "--title", "0"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
for line in proc.stdout:
    # process output line by line
```

The `stderr=subprocess.STDOUT` merges stderr into stdout for unified output.

### Scan process

1. Run `HandBrakeCLI -i /dev/sr0 --title 0` (scans all titles).
2. Parse output to find the title with the longest duration.
3. Parse the same output to extract audio and subtitle tracks for that title.
4. No second HandBrake invocation needed.

### Encode process

1. Build command with selected parameters.
2. Run `subprocess.Popen`.
3. Stream stdout line by line, parsing progress percentage.
4. Update progress bar via `GLib.idle_add`.
5. Wait for process to complete.
6. Check return code and output file.

## Windows port (ripdvd-win.py)

The Windows port uses `tkinter` instead of GTK4 because:
- tkinter is built into Python on Windows.
- PyGObject/GTK4 is difficult to install on Windows.
- The Windows version has the same feature set but a different look.

Key differences:
- DVD drive detection uses `ctypes.windll.kernel32.GetLogicalDrives()`.
- HandBrakeCLI is searched in common Windows install locations.
- Output directory uses `%USERPROFILE%\Videos\Rips`.
- Debug log is at `%USERPROFILE%\ripdvd-debug.log`.

## CLI script (ripdvd-cli.sh)

A bash script for headless operation:

1. Checks for HandBrakeCLI.
2. Scans the DVD for the longest title.
3. Encodes with default parameters.
4. Shows progress via `zenity`.

## Data flow

```
User clicks "Rip DVD"
    │
    ▼
on_rip_clicked() [main thread]
    │
    ▼
_encode_worker() [worker thread]
    │
    ├── Build HandBrakeCLI command
    ├── subprocess.Popen
    ├── Stream stdout → parse progress
    ├── GLib.idle_add(_update_progress)  [main thread]
    ├── GLib.idle_add(_append_log)       [main thread]
    │
    ▼
_process.wait()
    │
    ├── rc == 0 and file exists → _encode_ok()
    └── rc != 0 or empty file → _encode_failed()
```

## Dependencies

### Python packages

- `gi` (PyGObject) — GTK4/libadwaita bindings (Linux only)
- `tkinter` — GUI (Windows only, built-in)

### System packages

- `HandBrakeCLI` — encoding engine
- `libdvdcss` — DVD decryption
- `zenity` — dialog boxes (CLI version)

### External tools

- `HandBrakeCLI` — must be in PATH or at a known location
- `update-desktop-database` — for GNOME menu registration (optional)

## Design decisions

1. **HandBrakeCLI over libhb**: Using the CLI instead of the library (libhb) simplifies the code and avoids C bindings. The CLI is well-documented and stable.

2. **Thread-based workers**: Encoding is CPU-intensive and must not block the UI. Worker threads handle the subprocess, while `GLib.idle_add` marshals UI updates to the main thread.

3. **Single-pass scan**: Instead of scanning each title separately (which requires an output file), we scan all titles at once (`--title 0`) and parse the output. This is faster and avoids the "Missing output file name" error.

4. **Passthrough audio/subtitles**: By default, audio and subtitles are copied without re-encoding. This preserves original quality (including 5.1 surround) and speeds up encoding.

5. **Native resolution**: DVDs are SD (480p/576p). Upscaling is not done by default to avoid artificial artifacts and keep files small.

6. **RF 20 for H.264**: Constant quality mode with RF 20 gives near-transparent quality for DVD sources while keeping file sizes reasonable (~1-1.5 GB per movie).
