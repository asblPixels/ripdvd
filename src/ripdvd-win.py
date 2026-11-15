#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ripdvd-win — Windows port of ripdvd (tkinter, no GTK dependency)."""

import os
import re
import subprocess
import threading
import shutil
import sys
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
except ImportError:
    print("tkinter not available. Install Python with tkinter support.", file=sys.stderr)
    sys.exit(1)

APP_TITLE = "RipDvD (Windows)"
OUT_DIR = os.path.join(os.path.expanduser("~"), "Videos", "Rips")
DEBUG_LOG = os.path.join(os.path.expanduser("~"), "ripdvd-debug.log")


def find_handbrake():
    """Locate HandBrakeCLI.exe on Windows."""
    # Check PATH
    if shutil.which("HandBrakeCLI") or shutil.which("HandBrakeCLI.exe"):
        return ["HandBrakeCLI"]
    # Common install locations
    candidates = [
        r"C:\Program Files\HandBrake\HandBrakeCLI.exe",
        r"C:\Program Files (x86)\HandBrake\HandBrakeCLI.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\HandBrake\HandBrakeCLI.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return [c]
    return None


def detect_dvd_drives():
    """Return list of CD/DVD drive letters on Windows."""
    drives = []
    try:
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                letter = chr(65 + i) + ":\\"
                # Check drive type: 5 = CD-ROM
                dtype = ctypes.windll.kernel32.GetDriveTypeW(letter)
                if dtype == 5:
                    drives.append(letter)
    except Exception:
        pass
    # Fallback: try D: through Z:
    if not drives:
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            path = letter + ":\\"
            if os.path.exists(path):
                drives.append(path)
    return drives


def parse_title_scan(text):
    best_title, best_ms = 1, 0
    current = None
    for line in text.splitlines():
        m = re.search(r"scanning title (\d+)", line)
        if m:
            current = int(m.group(1))
        m = re.search(r"duration is \S+ \((\d+) ms\)", line)
        if m and current is not None:
            ms = int(m.group(1))
            if ms > best_ms:
                best_ms, best_title = ms, current
            current = None
    return best_title, best_ms


def parse_tracks_for_title(text, target_title):
    audio = []
    subs = []
    current_title = None
    cur_audio = None
    cur_sub = None
    for line in text.splitlines():
        m = re.search(r"scanning title (\d+)", line)
        if m:
            current_title = int(m.group(1))
            cur_audio = None
            cur_sub = None
            continue
        if current_title != target_title:
            continue
        m = re.search(r"checking audio (\d+)", line)
        if m:
            cur_audio = int(m.group(1))
            cur_sub = None
            continue
        m = re.search(r"checking subtitle (\d+)", line)
        if m:
            cur_sub = int(m.group(1))
            cur_audio = None
            continue
        m = re.search(r"id=0x[0-9a-f]+,\s*lang=(.+?)(?:,|\s*$)", line)
        if m:
            lang = m.group(1).strip()
            if cur_audio is not None and not any(a[0] == cur_audio for a in audio):
                audio.append((cur_audio, f"Track {cur_audio} — {lang}"))
                cur_audio = None
            elif cur_sub is not None and not any(s[0] == cur_sub for s in subs):
                subs.append((cur_sub, f"Track {cur_sub} — {lang}"))
                cur_sub = None
    if not audio:
        audio = [(1, "Track 1 — (unknown)")]
    return audio, subs


class RipdvdWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("520x620")
        self.resizable(True, True)

        self.hb = find_handbrake()
        self.process = None
        self.encoding = False
        self.scanning = False
        self.audio_tracks = []
        self.sub_tracks = []
        self.best_title = 1
        self.best_dur_min = 0
        self.last_encode_params = None
        self.dvd_drive = None

        self.drives = detect_dvd_drives()
        if self.drives:
            self.dvd_drive = self.drives[0]

        self._build_ui()

        if self.dvd_drive:
            self.status_var.set(f"Drive detected: {self.dvd_drive}. Scanning…")
            self.after(100, self.start_scan)
        else:
            self.status_var.set("No DVD drive detected. Enter drive letter and scan.")

    def _build_ui(self):
        # Top frame
        top = tk.Frame(self, text="RipDvD — Windows Edition", padx=10, pady=10)
        top.pack(fill=tk.X, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(top, textvariable=self.status_var, wraplength=480, fg="gray").pack()

        # Drive selection
        drive_frame = tk.Frame(self, text="DVD Drive", padx=10, pady=5)
        drive_frame.pack(fill=tk.X, padx=10, pady=5)
        df = tk.Frame(drive_frame)
        df.pack(fill=tk.X)
        tk.Label(df, text="Drive:").pack(side=tk.LEFT)
        self.drive_var = tk.StringVar(value=self.dvd_drive or "")
        self.drive_combo = ttk.Combobox(df, textvariable=self.drive_var, values=self.drives, width=12)
        self.drive_combo.pack(side=tk.LEFT, padx=5)
        tk.Button(df, text="Scan", command=self.start_scan).pack(side=tk.LEFT, padx=5)

        # Audio
        audio_frame = tk.Frame(self, text="Audio language", padx=10, pady=5)
        audio_frame.pack(fill=tk.X, padx=10, pady=5)
        self.audio_var = tk.StringVar(value="(scan required)")
        self.audio_combo = ttk.Combobox(audio_frame, textvariable=self.audio_var, state="readonly", width=40)
        self.audio_combo.pack(fill=tk.X)

        # Subtitles
        sub_frame = tk.Frame(self, text="Subtitles", padx=10, pady=5)
        sub_frame.pack(fill=tk.X, padx=10, pady=5)
        self.sub_var = tk.StringVar(value="None")
        self.sub_combo = ttk.Combobox(sub_frame, textvariable=self.sub_var, state="readonly", width=40)
        self.sub_combo.pack(fill=tk.X)

        # Progress
        prog_frame = tk.Frame(self, text="Progress", padx=10, pady=5)
        prog_frame.pack(fill=tk.X, padx=10, pady=5)
        self.progress = ttk.Progressbar(prog_frame, mode="determinate", maximum=100)
        self.progress.pack(fill=tk.X)
        self.pct_var = tk.StringVar(value="0 %")
        tk.Label(prog_frame, textvariable=self.pct_var).pack()

        # Buttons
        btn_frame = tk.Frame(self, padx=10, pady=5)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        self.btn_rip = tk.Button(btn_frame, text="Rip DVD", bg="#0078d4", fg="white", command=self.on_rip)
        self.btn_rip.pack(side=tk.LEFT, padx=3)
        self.btn_stop = tk.Button(btn_frame, text="Stop", bg="#d32f2f", fg="white", command=self.on_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=3)
        self.btn_resume = tk.Button(btn_frame, text="Resume", command=self.on_resume, state=tk.DISABLED)
        self.btn_resume.pack(side=tk.LEFT, padx=3)
        self.btn_rescan = tk.Button(btn_frame, text="Rescan", command=self.start_scan)
        self.btn_rescan.pack(side=tk.LEFT, padx=3)
        self.btn_quit = tk.Button(btn_frame, text="Quit", command=self.on_quit)
        self.btn_quit.pack(side=tk.RIGHT, padx=3)

        # Output
        self.out_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.out_var, wraplength=480, fg="gray").pack(padx=10, pady=5)

        # Live log
        log_frame = tk.Frame(self, text="Live output", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log = scrolledtext.ScrolledText(log_frame, height=12, font=("Consolas", 9))
        self.log.pack(fill=tk.BOTH, expand=True)
        tk.Button(log_frame, text="Clear log", command=lambda: self.log.delete("1.0", tk.END)).pack(pady=3)

    def _log(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def _set_status(self, text):
        self.status_var.set(text)

    def start_scan(self):
        if self.scanning or self.encoding:
            return
        if self.hb is None:
            messagebox.showerror("Error", "HandBrakeCLI not found.\nInstall HandBrake for Windows.")
            return
        drive = self.drive_var.get().strip()
        if not drive:
            messagebox.showerror("Error", "No DVD drive selected.")
            return
        if not drive.endswith("\\"):
            drive += "\\"
        self.dvd_drive = drive
        self.scanning = True
        self.btn_rip.config(state=tk.DISABLED)
        self.btn_rescan.config(state=tk.DISABLED)
        self.status_var.set("Scanning DVD…")
        self.progress["value"] = 0
        self.pct_var.set("…")
        self.log.delete("1.0", tk.END)
        self._log("=== DVD SCAN ===\n")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        try:
            self._log(f"Launching: {' '.join(self.hb)} -i {self.dvd_drive} --title 0\n")
            proc = subprocess.Popen(
                self.hb + ["-i", self.dvd_drive, "--title", "0"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            lines = []
            for line in proc.stdout:
                lines.append(line)
                self._log(line)
            proc.wait()
            scan0 = "".join(lines)

            best_title, best_ms = parse_title_scan(scan0)
            if best_ms == 0:
                with open(DEBUG_LOG, "w") as f:
                    f.write(scan0)
                self.after(0, lambda: self._scan_failed("Cannot analyse DVD.\nCheck libdvdcss / drive."))
                return

            self.best_title = best_title
            self.best_dur_min = best_ms // 60000
            audio, subs = parse_tracks_for_title(scan0, best_title)
            self.audio_tracks = audio
            self.sub_tracks = subs

            with open(DEBUG_LOG, "w") as f:
                f.write(f"=== TITLE {best_title} ({best_ms} ms) ===\n")
                f.write(scan0)

            self._log(f"\n→ Main title: {best_title} ({best_ms // 60000} min)\n")
            self._log(f"→ {len(audio)} audio track(s), {len(subs)} subtitle track(s).\n")
            self.after(0, self._scan_done)
        except Exception as e:
            self.after(0, lambda: self._scan_failed(f"Scan error:\n{e}"))

    def _scan_done(self):
        self.scanning = False
        self.btn_rip.config(state=tk.NORMAL)
        self.btn_rescan.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.NORMAL)

        labels = [a[1] for a in self.audio_tracks]
        self.audio_combo["values"] = labels if labels else ["(none)"]
        if labels:
            self.audio_var.set(labels[0])
            # prefer French then English
            for lbl in labels:
                low = lbl.lower()
                if "fran" in low or "fra" in low:
                    self.audio_var.set(lbl)
                    break
            else:
                for lbl in labels:
                    if "english" in lbl.lower() or "eng" in lbl.lower():
                        self.audio_var.set(lbl)
                        break

        sub_labels = ["None"] + [s[1] for s in self.sub_tracks]
        self.sub_combo["values"] = sub_labels
        self.sub_var.set("None")

        self.status_var.set(f"Title {self.best_title} detected ({self.best_dur_min} min). Ready.")
        self.progress["value"] = 0
        self.pct_var.set("0 %")

    def _scan_failed(self, msg):
        self.scanning = False
        self.btn_rip.config(state=tk.NORMAL)
        self.btn_rescan.config(state=tk.NORMAL)
        self.status_var.set("Scan failed.")
        self._log(f"\n❌ {msg}\n")
        messagebox.showerror("Error", msg)

    def on_rip(self):
        if self.encoding or self.scanning:
            return
        if self.hb is None:
            messagebox.showerror("Error", "HandBrakeCLI not found.")
            return
        if not self.audio_tracks:
            messagebox.showerror("Error", "No audio tracks detected. Rescan the DVD.")
            return

        self.encoding = True
        self.btn_rip.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_rescan.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.status_var.set("Encoding…")
        self.progress["value"] = 0
        self.pct_var.set("0 %")
        self.out_var.set("")
        self.log.delete("1.0", tk.END)
        self._log("=== ENCODING ===\n")
        threading.Thread(target=self._encode_worker, daemon=True).start()

    def _encode_worker(self):
        audio_idx = 1
        for a in self.audio_tracks:
            if a[1] == self.audio_var.get():
                audio_idx = a[0]
                break
        sub_idx = None
        sub_sel = self.sub_var.get()
        if sub_sel != "None":
            for s in self.sub_tracks:
                if s[1] == sub_sel:
                    sub_idx = s[0]
                    break

        self.last_encode_params = (self.best_title, audio_idx, sub_idx)

        name = f"DVD_{datetime.now():%Y%m%d_%H%M%S}"
        os.makedirs(OUT_DIR, exist_ok=True)
        outfile = os.path.join(OUT_DIR, f"{name}.mkv")

        cmd = self.hb + [
            "-i", self.dvd_drive,
            "-t", str(self.best_title),
            "-o", outfile,
            "--preset", "Fast 480p30",
            "--encoder", "x264",
            "--quality", "20",
            "--encoder-preset", "medium",
            "--aencoder", "copy",
            "--audio", str(audio_idx),
        ]
        if sub_idx is not None:
            cmd += ["--subtitle", str(sub_idx)]

        self._log("Command: " + " ".join(cmd) + "\n\n")

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
        except Exception as e:
            self.after(0, lambda: self._encode_failed(f"Launch failed:\n{e}"))
            return

        tail = []
        for line in self.process.stdout:
            tail.append(line)
            if len(tail) > 50:
                tail.pop(0)
            self._log(line)
            m = re.search(r",\s*([\d.]+)\s*%", line)
            if m:
                pct = float(m.group(1))
                self.after(0, lambda p=pct: self._update_progress(p))

        self.process.wait()
        rc = self.process.returncode
        self.process = None

        with open(DEBUG_LOG, "a") as f:
            f.write(f"\n\n=== ENCODE (rc={rc}) ===\n")
            f.write("CMD: " + " ".join(cmd) + "\n")
            f.write("".join(tail))

        if rc != 0:
            tail_text = "".join(tail[-20:]).strip()
            self.after(0, lambda: self._encode_failed(
                f"Encoding failed (code {rc}).\n\nLast lines:\n{tail_text}"))
            return
        if not os.path.isfile(outfile) or os.path.getsize(outfile) == 0:
            tail_text = "".join(tail[-20:]).strip()
            self.after(0, lambda: self._encode_failed(
                f"Output file empty or missing.\n\nLast lines:\n{tail_text}"))
            return

        size = self._human_size(os.path.getsize(outfile))
        self.after(0, lambda: self._encode_ok(outfile, size))

    def on_stop(self):
        if self.process is not None:
            try:
                self.process.terminate()
                self._log("\n⚠ Stop requested by user.\n")
            except Exception:
                pass
        self.status_var.set("Stop requested…")

    def on_resume(self):
        if self.encoding or self.scanning:
            return
        if self.hb is None:
            messagebox.showerror("Error", "HandBrakeCLI not found.")
            return
        if self.last_encode_params is None:
            self.start_scan()
            return
        self.encoding = True
        self.btn_rip.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_rescan.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.status_var.set("Resuming encode…")
        self.progress["value"] = 0
        self.pct_var.set("0 %")
        self.out_var.set("")
        self.log.delete("1.0", tk.END)
        self._log("=== RESUME ENCODING ===\n")
        threading.Thread(target=self._resume_worker, daemon=True).start()

    def _resume_worker(self):
        title, audio_idx, sub_idx = self.last_encode_params
        name = f"DVD_{datetime.now():%Y%m%d_%H%M%S}_resume"
        os.makedirs(OUT_DIR, exist_ok=True)
        outfile = os.path.join(OUT_DIR, f"{name}.mkv")

        cmd = self.hb + [
            "-i", self.dvd_drive,
            "-t", str(title),
            "-o", outfile,
            "--preset", "Fast 480p30",
            "--encoder", "x264",
            "--quality", "20",
            "--encoder-preset", "medium",
            "--aencoder", "copy",
            "--audio", str(audio_idx),
        ]
        if sub_idx is not None:
            cmd += ["--subtitle", str(sub_idx)]

        self._log("Command: " + " ".join(cmd) + "\n\n")

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
        except Exception as e:
            self.after(0, lambda: self._encode_failed(f"Launch failed:\n{e}"))
            return

        tail = []
        for line in self.process.stdout:
            tail.append(line)
            if len(tail) > 50:
                tail.pop(0)
            self._log(line)
            m = re.search(r",\s*([\d.]+)\s*%", line)
            if m:
                pct = float(m.group(1))
                self.after(0, lambda p=pct: self._update_progress(p))

        self.process.wait()
        rc = self.process.returncode
        self.process = None

        if rc != 0:
            tail_text = "".join(tail[-20:]).strip()
            self.after(0, lambda: self._encode_failed(
                f"Resume failed (code {rc}).\n\nLast lines:\n{tail_text}"))
            return
        if not os.path.isfile(outfile) or os.path.getsize(outfile) == 0:
            tail_text = "".join(tail[-20:]).strip()
            self.after(0, lambda: self._encode_failed(
                f"Output file empty or missing.\n\nLast lines:\n{tail_text}"))
            return

        size = self._human_size(os.path.getsize(outfile))
        self.after(0, lambda: self._encode_ok(outfile, size))

    def on_quit(self):
        if self.process is not None:
            try:
                self.process.terminate()
            except Exception:
                pass
        self.destroy()

    def _update_progress(self, pct):
        self.progress["value"] = pct
        self.pct_var.set(f"{pct:.1f} %")

    def _encode_ok(self, outfile, size):
        self.encoding = False
        self.btn_rip.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_rescan.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.NORMAL)
        self.status_var.set("Done ✅")
        self.progress["value"] = 100
        self.pct_var.set("100 %")
        self.out_var.set(f"{outfile}\n({size})")
        self._log(f"\n✅ Done: {outfile} ({size})\n")
        messagebox.showinfo("RipDvD", f"Encoding complete:\n{outfile}\n({size})")

    def _encode_failed(self, msg):
        self.encoding = False
        self.btn_rip.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_rescan.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.NORMAL)
        self.status_var.set("Error")
        self.progress["value"] = 0
        self.pct_var.set("0 %")
        self._log(f"\n❌ {msg}\n")
        messagebox.showerror("Error", msg)

    @staticmethod
    def _human_size(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"


def main():
    app = RipdvdWin()
    app.mainloop()


if __name__ == "__main__":
    main()
