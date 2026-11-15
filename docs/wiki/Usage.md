# Usage

This page explains how to use ripdvd from start to finish.

## Before you start

1. Insert a DVD into your optical drive.
2. Launch RipDvD (from the application menu or command line).
3. Wait for the automatic scan to complete.

## Main workflow

### 1. Automatic scan

When you launch RipDvD with a DVD inserted, it automatically:

1. Detects the DVD drive (`/dev/sr0` on Linux, drive letter on Windows).
2. Scans all titles on the disc.
3. Identifies the **longest title** (usually the main movie).
4. Extracts all **audio tracks** and **subtitle tracks** for that title.
5. Populates the dropdown menus.

The live output window shows the scan progress in real time.

### 2. Select audio language

The **Audio language** dropdown lists all detected audio tracks with their language.
- French is selected by default if available.
- Otherwise, English is selected.
- Otherwise, the first track is selected.

You can change this to any available track.

### 3. Select subtitles (optional)

The **Subtitles** dropdown lists all detected subtitle tracks plus "None".
- "None" is selected by default.
- Choose a track to include it as a passthrough subtitle in the MKV.

### 4. Start encoding

Click **Rip DVD** to start encoding. The app will:

1. Create an output filename: `DVD_YYYYMMDD_HHMMSS.mkv`
2. Run HandBrakeCLI with the selected parameters.
3. Show real-time progress in the progress bar and live output window.
4. Display a notification when complete.

### 5. Output location

The finished MKV is saved to:

- **Linux**: `~/Vidéos/Rips/` (or `~/Videos/Rips/`)
- **Windows**: `%USERPROFILE%\Videos\Rips\`

## Button reference

| Button | Action | When to use |
|---|---|---|
| **Rip DVD** | Start encoding the selected title | After scan is complete |
| **Arrêter** | Cancel the current encode | To stop an in-progress rip |
| **Reprendre** | Resume/retry the last encode with the same parameters | After an error or interruption |
| **Quitter** | Close the application | When you're done |
| **Rescanner** | Re-analyse the disc | After swapping DVDs, or if scan failed |
| **Effacer log** | Clear the live output window | To reduce clutter |

## Tips

### Ripping a TV series DVD

For DVDs with multiple episodes, the app picks the longest title by default.
To rip individual episodes:

1. Note the title numbers from the live output (e.g., "scanning title 1", "scanning title 2").
2. Currently, the app auto-selects the longest. For manual title selection, edit the source or use the CLI version.

> 💡 A future update will add manual title selection to the GUI.

### Batch processing

For ripping multiple DVDs in sequence:

1. Rip the first DVD.
2. When complete, eject and insert the next DVD.
3. Click **Rescanner**.
4. Click **Rip DVD**.

Repeat for each disc.

### Using the CLI version

For automation or headless servers:

```bash
bash src/ripdvd-cli.sh
```

This auto-detects the longest title and rips it with the same defaults, showing progress via `zenity`.

## Output file naming

Files are named: `DVD_YYYYMMDD_HHMMSS.mkv`

Example: `DVD_20261115_143022.mkv`

For resumed encodes: `DVD_YYYYMMDD_HHMMSS_resume.mkv`

## Integration with media servers

### Jellyfin

1. Add `~/Vidéos/Rips/` as a library folder in Jellyfin.
2. Jellyfin will automatically detect and metadata-match the MKV files.
3. Chapter markers, audio tracks, and subtitles are all preserved.

### Kodi

1. Add the folder as a video source in Kodi.
2. Use the Jellyfin add-on for richer metadata.

### Plex

1. Add the folder as a library in Plex.
2. Plex will scan and match the files automatically.

## Keyboard shortcuts

Currently, RipDvD does not have keyboard shortcuts. This is planned for a future release.
