# Troubleshooting

This page covers common issues and their solutions.

## Installation issues

### `ModuleNotFoundError: No module named 'gi'`

**Cause**: PyGObject is not installed.

**Solution**:
```bash
# Fedora
sudo dnf install python3-gobject gtk4 libadwaita

# Arch
sudo pacman -S python-gobject gtk4 libadwaita

# Ubuntu/Debian
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
```

### `HandBrakeCLI` not found

**Cause**: HandBrake is not installed or not in PATH.

**Solution**:
```bash
# Fedora
sudo dnf install HandBrake HandBrake-cli

# Arch
sudo pacman -S handbrake

# Ubuntu/Debian
sudo apt install handbrake-cli

# Windows
# Download from https://handbrake.fr/downloads.php
```

### `gtk4` or `libadwaita` not found

**Cause**: GTK4 or libadwaita packages are missing.

**Solution**:
```bash
# Fedora
sudo dnf install gtk4 libadwaita

# Arch
sudo pacman -S gtk4 libadwaita

# Ubuntu/Debian
sudo apt install gir1.2-gtk-4.0 gir1.2-adw-1
```

## Runtime issues

### App won't start (segfault)

**Cause**: GTK widget accessed from a non-main thread.

**Solution**: Update to the latest version. The fix is in v1.0.0+.

```bash
cd ~/Documents/ripdvd  # or your clone
git pull
bash scripts/install.sh
```

### DVD not detected (`/dev/sr0` not found)

**Cause**: No DVD drive detected or drive not mounted.

**Solutions**:
1. Check the drive is connected: `lsblk | grep sr`
2. Try a different USB port.
3. Wait a few seconds after inserting the disc.
4. Click **Rescanner**.
5. Check permissions: `ls -la /dev/sr0`

### Black screen / "cannot read disc" on encrypted DVDs

**Cause**: `libdvdcss` is not installed.

**Solution**:
```bash
# Fedora
sudo dnf install rpmfusion-free-release-tainted
sudo dnf install libdvdcss

# Arch
yay -S libdvdcss

# Ubuntu/Debian
sudo apt install libdvd-pkg
sudo dpkg-reconfigure libdvd-pkg

# Windows
# HandBrake for Windows includes libdvdcss
```

### Empty output file

**Cause**: HandBrakeCLI failed during encoding.

**Diagnosis**:
1. Open `~/.ripdvd-debug.log` or click **Voir le log de debug**.
2. Look at the last lines for the error message.

**Common causes**:
- Missing `libdvdcss` for encrypted discs.
- HandBrake Flatpak without `--device=all` (fixed in current version).
- Insufficient disk space in output directory.
- Corrupted DVD disc.

### Audio track shows "(inconnue)" (unknown)

**Cause**: The scan couldn't parse the audio track language.

**Solution**:
1. Click **Rescanner**.
2. Check the live output for "checking audio" lines.
3. If the issue persists, the DVD may have an unusual structure.

### Subtitles not detected

**Cause**: The scan couldn't parse subtitle tracks, or the DVD has no subtitles.

**Solution**:
1. Click **Rescanner**.
2. Check the live output for "checking subtitle" lines.
3. Some DVDs (especially older ones) may not have subtitle tracks.

### Encoding is very slow

**Cause**: Software encoding on an older CPU.

**Solutions**:
1. This is expected on older CPUs (e.g., Sandy Bridge i3: ~15-20 min per movie).
2. Use a faster preset: edit `--encoder-preset` to `fast` or `veryfast` in `src/ripdvd.py`.
3. Close other applications to free CPU.
4. Consider a newer CPU or GPU with hardware encoding (future feature).

### "missing parameter (--chapters)"

**Cause**: Old version of the app (pre-v1.0.0).

**Solution**: Update to the latest version.

### App crashes when scanning

**Cause**: Possible issue with the DVD drive or libdvdcss.

**Solution**:
1. Check `~/.ripdvd-debug.log` for errors.
2. Try a different DVD.
3. Ensure `libdvdcss` is installed.
4. Try running HandBrakeCLI manually:
   ```bash
   HandBrakeCLI -i /dev/sr0 --title 0
   ```

## Windows-specific issues

### Python not found

**Cause**: Python is not in PATH.

**Solution**: Reinstall Python and check "Add Python to PATH" during installation.

### HandBrakeCLI not found

**Cause**: HandBrake is not installed or not in the expected location.

**Solution**:
1. Download HandBrake from https://handbrake.fr/downloads.php
2. Install to the default location (`C:\Program Files\HandBrake\`)
3. Re-run the installer.

### DVD drive not detected

**Cause**: No CD-ROM drive found by the detection logic.

**Solution**:
1. Enter the drive letter manually in the Drive field (e.g., `D:\`).
2. Click **Scan**.

### tkinter not available

**Cause**: Python was installed without tkinter.

**Solution**: Reinstall Python from python.org (the standard installer includes tkinter).

## Getting help

If your issue is not covered here:

1. Check the [GitHub Issues](https://github.com/asblPixels/ripdvd/issues) for similar problems.
2. Open a new issue with:
   - Your OS and version
   - HandBrake version (`HandBrakeCLI --version`)
   - The content of `~/.ripdvd-debug.log`
   - Steps to reproduce
3. Use the [Bug Report template](https://github.com/asblPixels/ripdvd/issues/new?template=bug_report.md).
