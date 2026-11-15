# Configuration

This page documents the settings, presets, and customization options for RipDvD.

## Default encoding profile

The default profile is optimized for DVD sources and home media server playback:

| Parameter | Value | CLI flag |
|---|---|---|
| Container | MKV | `--mux mkv` (implicit) |
| Video codec | H.264 (x264) | `--encoder x264` |
| Quality | RF 20 | `--quality 20` |
| Encoder preset | `medium` | `--encoder-preset medium` |
| Resolution | Native (no scaling) | (preset handles this) |
| Framerate | Source | (preset handles this) |
| Audio | Copy (passthrough) | `--aencoder copy` |
| Subtitles | Passthrough (optional) | `--subtitle N` |
| Chapters | Preserved | (default) |

## Preset: Fast 480p30

The app uses HandBrake's built-in `Fast 480p30` preset as a base, then overrides:
- Encoder: x264
- Quality: RF 20
- Preset: medium
- Audio: copy

This gives a good balance between quality and encoding speed on older CPUs.

## Customizing the encoding

To change the encoding parameters, edit `src/ripdvd.py` (or `src/ripdvd-win.py` for Windows).

### Change video quality

Find this line in `_encode_worker` and `_resume_worker`:

```python
"--quality", "20",
```

- Lower value = higher quality, larger file (e.g., 18)
- Higher value = lower quality, smaller file (e.g., 22)
- Recommended range: 18–23 for H.264

### Change encoder preset

```python
"--encoder-preset", "medium",
```

Options (fastest to slowest): `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`

- `fast` or `veryfast` for quicker encoding on slow CPUs
- `slow` or `slower` for better compression

### Change audio encoding

```python
"--aencoder", "copy",
```

Options:
- `copy` — passthrough original audio (recommended, keeps 5.1)
- `av_aac` — re-encode to AAC (smaller, but loses 5.1 unless configured)
- `ac3` — re-encode to AC3

### Change video codec

```python
"--encoder", "x264",
```

Options:
- `x264` — H.264 (best compatibility)
- `x265` — H.265/HEVC (smaller files, slower encoding, less compatible)
- `svt_av1` — AV1 (best compression, very slow, modern clients only)

### Change output resolution

The default keeps native DVD resolution. To upscale, add:

```python
"--width", "1280",
"--height", "720",
```

> ⚠️ Upscaling SD to HD increases file size and encoding time significantly.

## Output directory

Default output directory:

- **Linux**: `~/Vidéos/Rips/`
- **Windows**: `%USERPROFILE%\Videos\Rips\`

To change it, edit `OUT_DIR` in the source file:

```python
OUT_DIR = os.path.join(os.path.expanduser("~"), "Vidéos", "Rips")
```

## Debug log

The full HandBrakeCLI output is saved to:

- **Linux**: `~/.ripdvd-debug.log`
- **Windows**: `%USERPROFILE%\ripdvd-debug.log`

This is useful for troubleshooting. The log is overwritten on each scan and appended during encoding.

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `LIBVA_DRIVER_NAME` | VA-API driver for hardware decoding | `i965` (auto-detected) |

## HandBrake preset reference

For more details on HandBrake presets and parameters, see:
- https://handbrake.fr/docs/en/latest/technical/video-bframes.html
- https://handbrake.fr/docs/en/latest/cli/

## Future configuration options

The following are planned for future releases:

- GUI-based preset selector
- Custom output directory picker
- Audio bitrate selection
- Subtitle burn-in option
- Multiple title selection (for TV series)
- Queue management (batch multiple DVDs)
- Configuration file (`~/.config/ripdvd/config.json`)
- Save/load user presets
