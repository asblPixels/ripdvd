#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RipDvD — Windows Edition. Simple DVD ripper for everyone."""

import os
import re
import subprocess
import threading
import shutil
import sys
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
except ImportError:
    print("tkinter not available. Please reinstall Python.", file=sys.stderr)
    sys.exit(1)

APP_TITLE = "RipDvD — by asblPixels"
OUT_DIR = os.path.join(os.path.expanduser("~"), "Videos", "Rips")
DEBUG_LOG = os.path.join(os.path.expanduser("~"), "ripdvd-debug.log")


def find_handbrake():
    if shutil.which("HandBrakeCLI") or shutil.which("HandBrakeCLI.exe"):
        return ["HandBrakeCLI"]
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
    drives = []
    try:
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                letter = chr(65 + i) + ":\\"
                if ctypes.windll.kernel32.GetDriveTypeW(letter) == 5:
                    drives.append(letter)
    except Exception:
        pass
    if not drives:
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            p = letter + ":\\"
            if os.path.exists(p):
                drives.append(p)
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
    audio, subs = [], []
    current_title = None
    cur_audio = cur_sub = None
    for line in text.splitlines():
        m = re.search(r"scanning title (\d+)", line)
        if m:
            current_title = int(m.group(1))
            cur_audio = cur_sub = None
            continue
        if current_title != target_title:
            continue
        m = re.search(r"checking audio (\d+)", line)
        if m:
            cur_audio = int(m.group(1)); cur_sub = None; continue
        m = re.search(r"checking subtitle (\d+)", line)
        if m:
            cur_sub = int(m.group(1)); cur_audio = None; continue
        m = re.search(r"id=0x[0-9a-f]+,\s*lang=(.+?)(?:,|\s*$)", line)
        if m:
            lang = m.group(1).strip()
            if cur_audio is not None and not any(a[0] == cur_audio for a in audio):
                audio.append((cur_audio, f"Track {cur_audio} - {lang}"))
                cur_audio = None
            elif cur_sub is not None and not any(s[0] == cur_sub for s in subs):
                subs.append((cur_sub, f"Track {cur_sub} - {lang}"))
                cur_sub = None
    if not audio:
        audio = [(1, "Track 1 - (unknown)")]
    return audio, subs


class RipDvDWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("560x680")
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")

        # ---- Couleurs asblPixels : turquoise (#00C9A0) + encre (#04302A) ----
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Teal.Horizontal.TProgressbar",
            troughcolor="#d9f5ee", background="#00c9a0", bordercolor="#00c9a0",
            lightcolor="#00c9a0", darkcolor="#00b08c",
        )

        self.hb = find_handbrake()
        self.process = None
        self.encoding = False
        self.scanning = False
        self.audio_tracks = []
        self.sub_tracks = []
        self.best_title = 1
        self.best_dur_min = 0
        self.last_encode_params = None

        self.drives = detect_dvd_drives()
        self.dvd_drive = self.drives[0] if self.drives else None

        self._build_ui()

        if self.hb is None:
            self.after(200, self._show_setup_wizard)
        elif self.dvd_drive:
            self.status_var.set("DVD drive found. Scanning...")
            self.after(100, self.start_scan)
        else:
            self.status_var.set("No DVD drive found. Select one and click Scan.")

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#04302a", pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="RipDvD", font=("Segoe UI", 22, "bold"), fg="#ffffff", bg="#04302a").pack()
        tk.Label(header, text="From disc to digital - effortlessly", font=("Segoe UI", 10), fg="#8fe3d0", bg="#04302a").pack()
        tk.Label(header, text="by asblPixels", font=("Segoe UI", 10, "bold"), fg="#00e0b0", bg="#04302a").pack(pady=(2, 0))
        tk.Frame(self, bg="#00c9a0", height=3).pack(fill=tk.X)

        # Status
        sf = tk.Frame(self, bg="#f0f0f0", pady=6)
        sf.pack(fill=tk.X, padx=12)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sf, textvariable=self.status_var, font=("Segoe UI", 11), fg="#333", bg="#f0f0f0", wraplength=520).pack()

        # Drive
        df = tk.LabelFrame(self, text=" DVD Drive ", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", padx=8, pady=6)
        df.pack(fill=tk.X, padx=12, pady=4)
        row = tk.Frame(df, bg="#f0f0f0")
        row.pack(fill=tk.X)
        tk.Label(row, text="Drive:", font=("Segoe UI", 10), bg="#f0f0f0").pack(side=tk.LEFT)
        self.drive_var = tk.StringVar(value=self.dvd_drive or "")
        self.drive_combo = ttk.Combobox(row, textvariable=self.drive_var, values=self.drives, width=10, font=("Segoe UI", 10))
        self.drive_combo.pack(side=tk.LEFT, padx=6)
        tk.Button(row, text="  Scan  ", font=("Segoe UI", 10, "bold"), bg="#00c9a0", fg="#04302a", activebackground="#00b08c", activeforeground="#04302a", command=self.start_scan, relief=tk.FLAT, padx=8, pady=2).pack(side=tk.LEFT)

        # Audio
        af = tk.LabelFrame(self, text=" Audio Language ", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", padx=8, pady=6)
        af.pack(fill=tk.X, padx=12, pady=4)
        self.audio_var = tk.StringVar(value="(scan required)")
        self.audio_combo = ttk.Combobox(af, textvariable=self.audio_var, state="readonly", font=("Segoe UI", 10))
        self.audio_combo.pack(fill=tk.X)

        # Subtitles
        sf2 = tk.LabelFrame(self, text=" Subtitles ", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", padx=8, pady=6)
        sf2.pack(fill=tk.X, padx=12, pady=4)
        self.sub_var = tk.StringVar(value="None")
        self.sub_combo = ttk.Combobox(sf2, textvariable=self.sub_var, state="readonly", font=("Segoe UI", 10))
        self.sub_combo.pack(fill=tk.X)

        # Progress
        pf = tk.LabelFrame(self, text=" Progress ", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", padx=8, pady=6)
        pf.pack(fill=tk.X, padx=12, pady=4)
        self.progress = ttk.Progressbar(pf, mode="determinate", maximum=100, style="Teal.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=2)
        self.pct_var = tk.StringVar(value="0 %")
        tk.Label(pf, textvariable=self.pct_var, font=("Segoe UI", 10), bg="#f0f0f0").pack()

        # Output
        self.out_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.out_var, font=("Segoe UI", 9), fg="#555", bg="#f0f0f0", wraplength=520).pack(padx=12, pady=2)

        # Buttons
        bf = tk.Frame(self, bg="#f0f0f0", pady=6)
        bf.pack(fill=tk.X, padx=12)
        btn_style = {"font": ("Segoe UI", 10, "bold"), "relief": tk.FLAT, "padx": 10, "pady": 4}
        self.btn_rip = tk.Button(bf, text="  RIP DVD  ", bg="#00c9a0", fg="#04302a", command=self.on_rip, activebackground="#00b08c", activeforeground="#04302a", **btn_style)
        self.btn_rip.pack(side=tk.LEFT, padx=3)
        self.btn_stop = tk.Button(bf, text="  STOP  ", bg="#dc3545", fg="white", command=self.on_stop, state=tk.DISABLED, **btn_style)
        self.btn_stop.pack(side=tk.LEFT, padx=3)
        self.btn_resume = tk.Button(bf, text="Resume", command=self.on_resume, state=tk.DISABLED, **btn_style)
        self.btn_resume.pack(side=tk.LEFT, padx=3)
        self.btn_rescan = tk.Button(bf, text="Rescan", command=self.start_scan, **btn_style)
        self.btn_rescan.pack(side=tk.LEFT, padx=3)
        self.btn_quit = tk.Button(bf, text="Quit", command=self.on_quit, **btn_style)
        self.btn_quit.pack(side=tk.RIGHT, padx=3)
        self.btn_about = tk.Button(bf, text="About", command=self.on_about, **btn_style)
        self.btn_about.pack(side=tk.RIGHT, padx=3)

        # Live log
        lf = tk.LabelFrame(self, text=" Live Output ", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", padx=8, pady=6)
        lf.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        self.log = scrolledtext.ScrolledText(lf, height=10, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.log.pack(fill=tk.BOTH, expand=True, pady=4)
        tk.Button(lf, text="Clear Log", font=("Segoe UI", 9), command=lambda: self.log.delete("1.0", tk.END), relief=tk.FLAT).pack(pady=2)

        # Footer
        footer = tk.Label(self, text="© 2026 asblPixels  |  MIT License  |  Open Source  |  github.com/asblPixels/ripdvd", font=("Segoe UI", 8, "bold"), fg="#00876c", bg="#f0f0f0", cursor="hand2")
        footer.pack(side=tk.BOTTOM, pady=4)
        footer.bind("<Button-1>", lambda _e: self.on_about())

    def _show_setup_wizard(self):
        messagebox.showwarning("Setup Required",
            "HandBrakeCLI was not found on your system.\n\n"
            "Please:\n"
            "1. Download HandBrake from https://handbrake.fr/downloads.php\n"
            "2. Install it (default location is fine)\n"
            "3. Restart RipDvD\n\n"
            "RipDvD needs HandBrake to convert your DVDs.")

    def start_scan(self):
        if self.scanning or self.encoding:
            return
        if self.hb is None:
            self._show_setup_wizard()
            return
        drive = self.drive_var.get().strip()
        if not drive:
            messagebox.showerror("Error", "Please select a DVD drive.")
            return
        if not drive.endswith("\\"):
            drive += "\\"
        self.dvd_drive = drive
        self.scanning = True
        self.btn_rip.config(state=tk.DISABLED)
        self.btn_rescan.config(state=tk.DISABLED)
        self.status_var.set("Scanning DVD...")
        self.progress["value"] = 0
        self.pct_var.set("...")
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
                self.after(0, lambda: self._scan_failed("Cannot analyse DVD.\nCheck drive / libdvdcss."))
                return

            self.best_title = best_title
            self.best_dur_min = best_ms // 60000
            audio, subs = parse_tracks_for_title(scan0, best_title)
            self.audio_tracks = audio
            self.sub_tracks = subs

            with open(DEBUG_LOG, "w") as f:
                f.write(f"=== TITLE {best_title} ({best_ms} ms) ===\n")
                f.write(scan0)

            self._log(f"\n-> Main title: {best_title} ({best_ms // 60000} min)\n")
            self._log(f"-> {len(audio)} audio track(s), {len(subs)} subtitle track(s).\n")
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
        self._log(f"\n[ERROR] {msg}\n")
        messagebox.showerror("Error", msg)

    def on_rip(self):
        if self.encoding or self.scanning:
            return
        if self.hb is None:
            self._show_setup_wizard()
            return
        if not self.audio_tracks:
            messagebox.showerror("Error", "No audio tracks detected. Rescan the DVD.")
            return

        self.encoding = True
        self.btn_rip.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_rescan.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.status_var.set("Encoding...")
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
                self._log("\n[!] Stop requested by user.\n")
            except Exception:
                pass
        self.status_var.set("Stop requested...")

    def on_resume(self):
        if self.encoding or self.scanning:
            return
        if self.hb is None:
            self._show_setup_wizard()
            return
        if self.last_encode_params is None:
            self.start_scan()
            return
        self.encoding = True
        self.btn_rip.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_rescan.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.status_var.set("Resuming encode...")
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

    def on_about(self):
        win = tk.Toplevel(self)
        win.title("About RipDvD")
        win.geometry("640x660")
        win.configure(bg="#ffffff")
        win.transient(self)

        header = tk.Frame(win, bg="#04302a", pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="RipDvD", font=("Segoe UI", 20, "bold"),
                 fg="#ffffff", bg="#04302a").pack()
        tk.Label(header, text="Version 1.1.0 — From disc to digital, effortlessly",
                 font=("Segoe UI", 10), fg="#8fe3d0", bg="#04302a").pack()
        tk.Frame(win, bg="#00c9a0", height=3).pack(fill=tk.X)

        txt = scrolledtext.ScrolledText(
            win, wrap=tk.WORD, font=("Segoe UI", 10),
            bg="#ffffff", fg="#1d1d1d", relief=tk.FLAT, padx=16, pady=12,
        )
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", (
            "DEVELOPED BY asblPixels\n"
            "RipDvD is a free and open-source project created and maintained by asblPixels.\n"
            "https://github.com/asblPixels\n\n"
            "ABOUT THE APP\n"
            "RipDvD turns your DVDs into MKV files in one click. Pick the audio language\n"
            "and subtitles, then start the rip: the movie is encoded in H.264 (RF 20),\n"
            "at its native resolution, with its chapters, in %USERPROFILE%\\Videos\\Rips.\n\n"
            "CREDITS & ACKNOWLEDGEMENTS\n"
            "- HandBrake — encoding engine (handbrake.fr)\n"
            "- libdvdcss / VideoLAN — DVD decryption (videolan.org)\n"
            "- Python / tkinter — programming language & UI toolkit\n"
            "- Microsoft Windows — operating system\n\n"
            "LICENSE\n"
            "RipDvD is free software released under the MIT License. You may use, copy,\n"
            "modify and redistribute it freely, provided you keep the copyright notice\n"
            "and the license text.\n\n"
            "PRIVACY\n"
            "No personal data is collected, transmitted or sold. Everything runs locally\n"
            "on your computer; the app makes no network connection.\n\n"
            "LEGAL NOTICE\n"
            "RipDvD is intended to back up DVDs you legally own. Decrypting copy-protected\n"
            "discs may be illegal or restricted in some countries. It is your responsibility\n"
            "to check your local laws. The authors cannot be held liable for any illegal use.\n\n"
            "SOURCES & SUPPORT\n"
            "Source code, documentation and bug reports:\n"
            "https://github.com/asblPixels/ripdvd\n"
            "Debug log: %USERPROFILE%\\ripdvd-debug.log\n\n"
            "© 2026 asblPixels — All rights reserved. Open-source project under MIT License."
        ))
        txt.config(state=tk.DISABLED)

        def open_url(url):
            import webbrowser
            webbrowser.open(url)

        bar = tk.Frame(win, bg="#ffffff", pady=8)
        bar.pack(fill=tk.X)
        tk.Button(bar, text="GitHub", font=("Segoe UI", 10, "bold"),
                  bg="#00c9a0", fg="#04302a", relief=tk.FLAT, padx=10, pady=4,
                  command=lambda: open_url("https://github.com/asblPixels/ripdvd")
                  ).pack(side=tk.LEFT, padx=8)
        tk.Button(bar, text="MIT License", font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=10, pady=4,
                  command=lambda: open_url("https://github.com/asblPixels/ripdvd/blob/main/LICENSE")
                  ).pack(side=tk.LEFT)
        tk.Button(bar, text="Close", font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=10, pady=4, command=win.destroy
                  ).pack(side=tk.RIGHT, padx=8)

    def _update_progress(self, pct):
        self.progress["value"] = pct
        self.pct_var.set(f"{pct:.1f} %")

    def _encode_ok(self, outfile, size):
        self.encoding = False
        self.btn_rip.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_rescan.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.NORMAL)
        self.status_var.set("Done!")
        self.progress["value"] = 100
        self.pct_var.set("100 %")
        self.out_var.set(f"{outfile}\n({size})")
        self._log(f"\n[OK] Done: {outfile} ({size})\n")
        messagebox.showinfo("RipDvD", f"Encoding complete!\n\n{outfile}\n({size})")

    def _encode_failed(self, msg):
        self.encoding = False
        self.btn_rip.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_rescan.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.NORMAL)
        self.status_var.set("Error")
        self.progress["value"] = 0
        self.pct_var.set("0 %")
        self._log(f"\n[ERROR] {msg}\n")
        messagebox.showerror("Error", msg)

    @staticmethod
    def _human_size(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"


def main():
    app = RipDvDWin()
    app.mainloop()


if __name__ == "__main__":
    main()
