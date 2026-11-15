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
    from tkinter import ttk, messagebox, font as tkfont
except ImportError:
    print("tkinter not available. Please reinstall Python.", file=sys.stderr)
    sys.exit(1)

APP_TITLE = "RipDvD"
VERSION = "1.3.0"
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


def find_logo():
    """Locate the app logo (asblPixels identity) on Windows."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "logo.png"),
        os.path.join(here, "data", "logo.png"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "RipDvD", "logo.png"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def find_icon():
    """Locate the .ico used for the window/taskbar icon on Windows."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "ripdvd.ico"),
        os.path.join(here, "data", "ripdvd.ico"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "RipDvD", "ripdvd.ico"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
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


# ---------------------------------------------------------------------------
#  Interface — sobre, aérée, un écran par étape
# ---------------------------------------------------------------------------
C = {
    "bg":       "#fafbfb",
    "text":     "#1d2a2e",
    "muted":    "#6b7a7f",
    "soft":     "#eff3f3",
    "line":     "#e2e8e8",
    "accent":   "#00a884",
    "accent_h": "#00916f",
    "accent_s": "#e1f5ef",
    "warn":     "#b26a00",
    "warn_s":   "#fff1db",
    "ghost":    "#e9eded",
    "ghost_h":  "#dde3e3",
    "disabled": "#9fd9c9",
}


def pick_fonts(root):
    fams = set(tkfont.families(root))
    base = next((f for f in ("Segoe UI Variable Text", "Segoe UI", "Inter", "Cantarell",
                             "Helvetica Neue", "Arial") if f in fams), "TkDefaultFont")
    light = next((f for f in ("Segoe UI Light", "Segoe UI Variable Display Light",
                              "Inter Light", "Inter ExtraLight") if f in fams), base)
    return base, light


def friendly_track(label):
    """« Track 2 - Français (AC3) (5.1 ch) » → « Français · 5.1 »."""
    name = re.sub(r"^(Track|Piste) \d+\s*[-—]\s*", "", label)
    lang = name.split(" (")[0].strip() or name
    ch = re.search(r"\((\d\.\d) ch\)", name)
    return f"{lang} · {ch.group(1)}" if ch else lang


def friendly_list(labels):
    names = [friendly_track(l) for l in labels]
    out = []
    for n, l in zip(names, labels):
        if names.count(n) > 1:
            num = re.match(r"(?:Track|Piste) (\d+)", l)
            n = f"{n} · piste {num.group(1)}" if num else n
        out.append(n)
    return out


def human_duration(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def human_eta(h, m, s):
    total = h * 60 + m + (1 if s >= 30 else 0)
    if total < 1:
        return "Moins d'une minute restante"
    return f"Environ {human_duration(total)} restantes"


class PillButton(tk.Canvas):
    """Bouton plat aux coins arrondis (principal ou discret)."""

    def __init__(self, parent, text, command, font, kind="primary", height=52, width=None):
        self.kind = kind
        bg = parent["bg"]
        super().__init__(parent, height=height, bg=bg, highlightthickness=0, bd=0,
                         cursor="hand2", width=width or 10)
        self.text, self.command, self.font, self.h = text, command, font, height
        self.enabled = True
        self.hover = False
        self.bind("<Configure>", lambda _e: self._draw())
        self.bind("<Enter>", lambda _e: self._set_hover(True))
        self.bind("<Leave>", lambda _e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._click)

    def _colors(self):
        if self.kind == "primary":
            fill = C["disabled"] if not self.enabled else (C["accent_h"] if self.hover else C["accent"])
            return fill, "#ffffff"
        if self.kind == "ghost":
            return (C["ghost_h"] if self.hover else C["ghost"]), C["text"]
        return self["bg"], (C["accent"] if self.hover else C["muted"])  # "link"

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.h
        fill, fg = self._colors()
        if self.kind != "link":
            r = h / 2
            self.create_oval(0, 0, h, h, fill=fill, outline=fill)
            self.create_oval(w - h, 0, w, h, fill=fill, outline=fill)
            self.create_rectangle(r, 0, w - r, h, fill=fill, outline=fill)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg, font=self.font)

    def _set_hover(self, v):
        self.hover = v and self.enabled
        self._draw()

    def _click(self, _e):
        if self.enabled and self.command:
            self.command()

    def set_text(self, text):
        self.text = text
        self._draw()

    def set_enabled(self, v):
        self.enabled = v
        self.config(cursor="hand2" if v else "arrow")
        self._draw()


class Bubble(tk.Canvas):
    """Pastille ronde douce avec un pictogramme dessiné."""

    def __init__(self, parent, glyph="disc", warning=False, size=96):
        super().__init__(parent, width=size, height=size, bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.size = size
        self.set(glyph, warning)

    def set(self, glyph, warning=False):
        s = self.size
        self.delete("all")
        bg, fg = (C["warn_s"], C["warn"]) if warning else (C["accent_s"], C["accent"])
        self.create_oval(0, 0, s, s, fill=bg, outline=bg)
        c = s / 2
        if glyph == "disc":
            r = s * 0.25
            self.create_oval(c - r, c - r, c + r, c + r, outline=fg, width=3)
            self.create_oval(c - 4, c - 4, c + 4, c + 4, outline=fg, width=3)
        elif glyph == "check":
            self.create_line(c - 15, c + 1, c - 4, c + 12, c + 17, c - 11,
                             fill=fg, width=5, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        elif glyph == "warn":
            self.create_line(c, c - 16, c, c + 4, fill=fg, width=5, capstyle=tk.ROUND)
            self.create_oval(c - 3, c + 11, c + 3, c + 17, fill=fg, outline=fg)


class RipDvDWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        icon = find_icon()
        if icon:
            try:
                self.iconbitmap(icon)
            except Exception:
                pass
        self.geometry("460x640")
        self.minsize(380, 560)
        self.configure(bg=C["bg"])

        base, light = pick_fonts(self)
        self.F = {
            "title":   (base, 20, "bold"),
            "sub":     (base, 11),
            "body":    (base, 10),
            "small":   (base, 9),
            "eyebrow": (base, 8, "bold"),
            "btn":     (base, 11, "bold"),
            "pct":     (light, 54),
            "mono":    ("Consolas", 9),
        }
        self._style()

        self.hb = find_handbrake()
        self.process = None
        self.encoding = False
        self.scanning = False
        self.stop_requested = False
        self.retry_is_scan = False
        self.audio_tracks = []
        self.sub_tracks = []
        self.best_title = 1
        self.best_dur_min = 0
        self.last_encode_params = None
        self.log_visible = False

        self.drives = detect_dvd_drives()
        self.dvd_drive = self.drives[0] if self.drives else None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_quit)
        self.bind_all("<Control-q>", lambda _e: self.on_quit())
        self.bind_all("<Control-r>", lambda _e: self.start_scan())
        self.bind_all("<Control-l>", lambda _e: self.toggle_log())

        if self.hb is None:
            self.show("missing")
        elif self.dvd_drive:
            self.after(150, self.start_scan)
        else:
            self._show_empty(no_drive=True)

    # ------------------------------------------------------------------ style
    def _style(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure("Slim.Horizontal.TProgressbar", troughcolor=C["line"],
                     background=C["accent"], bordercolor=C["line"],
                     lightcolor=C["accent"], darkcolor=C["accent"], thickness=6)
        st.configure("Soft.TCombobox", fieldbackground=C["soft"], background=C["soft"],
                     bordercolor=C["soft"], lightcolor=C["soft"], darkcolor=C["soft"],
                     arrowcolor=C["muted"], foreground=C["text"], padding=(8, 4))
        st.map("Soft.TCombobox", fieldbackground=[("readonly", C["soft"])],
               selectbackground=[("readonly", C["soft"])],
               selectforeground=[("readonly", C["text"])])
        self.option_add("*TCombobox*Listbox.font", self.F["body"])
        self.option_add("*TCombobox*Listbox.selectBackground", C["accent"])

    # ------------------------------------------------------------- briques
    def _label(self, parent, text, font, color=None, **kw):
        return tk.Label(parent, text=text, font=self.F[font], fg=color or C["text"],
                        bg=parent["bg"], justify=tk.CENTER, **kw)

    def _page(self):
        outer = tk.Frame(self.stage, bg=C["bg"])
        inner = tk.Frame(outer, bg=C["bg"])
        inner.place(relx=0.5, rely=0.47, anchor="center", relwidth=0.84)
        return outer, inner

    def _hero(self, box, glyph, title, sub, warning=False):
        bubble = Bubble(box, glyph, warning)
        bubble.pack()
        t = self._label(box, title, "title", wraplength=360)
        t.pack(pady=(26, 0))
        s = self._label(box, sub, "sub", C["muted"], wraplength=340)
        s.pack(pady=(6, 0))
        return bubble, t, s

    # ------------------------------------------------------------ interface
    def _build_ui(self):
        # Barre du haut : titre + menu ☰
        top = tk.Frame(self, bg=C["bg"], height=48)
        top.pack(fill=tk.X)
        self._label(top, "RipDvD", "btn").place(relx=0.5, rely=0.5, anchor="center")
        self.menu_btn = tk.Label(top, text="☰", font=(self.F["body"][0], 15),
                                 fg=C["muted"], bg=C["bg"], cursor="hand2", padx=14)
        self.menu_btn.place(relx=1.0, rely=0.5, anchor="e")
        self.menu_btn.bind("<Button-1>", self._open_menu)

        self.menu = tk.Menu(self, tearoff=0, font=self.F["body"], bd=0,
                            activebackground=C["accent_s"], activeforeground=C["text"])
        self.menu.add_command(label="Analyser le disque", accelerator="Ctrl+R",
                              command=self.start_scan)
        self.menu.add_command(label="Ouvrir le dossier des films", command=self.open_folder)
        self.menu.add_command(label="Afficher le journal", accelerator="Ctrl+L",
                              command=self.toggle_log)
        self.menu.add_separator()
        self.menu.add_command(label="À propos de RipDvD", command=self.on_about)
        self.menu.add_command(label="Quitter", accelerator="Ctrl+Q", command=self.on_quit)

        # Zone des écrans
        self.stage = tk.Frame(self, bg=C["bg"])
        self.stage.pack(fill=tk.BOTH, expand=True)
        self.pages = {}
        for name in ("empty", "scanning", "ready", "encoding", "done", "error", "missing"):
            outer, inner = self._page()
            getattr(self, f"_page_{name}")(inner)
            self.pages[name] = outer

        # Journal repliable
        self.log_frame = tk.Frame(self, bg=C["soft"])
        bar = tk.Frame(self.log_frame, bg=C["soft"])
        bar.pack(fill=tk.X, padx=14, pady=(8, 2))
        self._label(bar, "Journal", "btn").pack(side=tk.LEFT)
        for txt, cb in (("Masquer", self.toggle_log), ("Effacer", self._clear_log)):
            b = tk.Label(bar, text=txt, font=self.F["small"], fg=C["muted"], bg=C["soft"],
                         cursor="hand2", padx=6)
            b.pack(side=tk.RIGHT)
            b.bind("<Button-1>", lambda _e, f=cb: f())
        self.log = tk.Text(self.log_frame, height=9, font=self.F["mono"], bg=C["soft"],
                           fg=C["text"], relief=tk.FLAT, bd=0, wrap=tk.WORD,
                           padx=14, pady=6, highlightthickness=0)
        self.log.pack(fill=tk.BOTH, expand=True)

    def _open_menu(self, _e):
        x = self.menu_btn.winfo_rootx()
        y = self.menu_btn.winfo_rooty() + self.menu_btn.winfo_height()
        self.menu.tk_popup(x - 180, y)

    # -------------------------------------------------------------- écrans
    def _page_empty(self, box):
        _, self.empty_title, self.empty_sub = self._hero(
            box, "disc", "Insérez un DVD", "Le film est détecté automatiquement.")
        self.drive_row = tk.Frame(box, bg=C["bg"])
        self.drive_row.pack(pady=(22, 0))
        self._label(self.drive_row, "Lecteur", "body", C["muted"]).pack(side=tk.LEFT, padx=(0, 8))
        self.drive_var = tk.StringVar(value=self.dvd_drive or "")
        self.drive_combo = ttk.Combobox(self.drive_row, textvariable=self.drive_var,
                                        values=self.drives, width=6, state="readonly",
                                        style="Soft.TCombobox", font=self.F["body"])
        self.drive_combo.pack(side=tk.LEFT)
        if len(self.drives) < 2:
            self.drive_row.pack_forget()
        self.empty_btn = PillButton(box, "Analyser le disque", self.start_scan,
                                    self.F["btn"], width=230)
        self.empty_btn.pack(pady=(34, 0))

    def _page_scanning(self, box):
        self.spinner = tk.Canvas(box, width=56, height=56, bg=C["bg"], highlightthickness=0)
        self.spinner.pack()
        self._spin_angle = 0
        self._label(box, "Analyse du disque", "title").pack(pady=(28, 0))
        self._label(box, "Recherche du film principal…", "sub", C["muted"]).pack(pady=(6, 0))

    def _spin(self):
        if not self.scanning:
            return
        self.spinner.delete("all")
        self.spinner.create_oval(6, 6, 50, 50, outline=C["line"], width=5)
        self.spinner.create_arc(6, 6, 50, 50, start=self._spin_angle, extent=100,
                                style=tk.ARC, outline=C["accent"], width=5)
        self._spin_angle = (self._spin_angle - 12) % 360
        self.after(30, self._spin)

    def _page_ready(self, box):
        Bubble(box, "disc").pack()
        self._label(box, "Film détecté", "title").pack(pady=(22, 0))
        self.ready_sub = self._label(box, "", "sub", C["muted"])
        self.ready_sub.pack(pady=(4, 0))

        card = tk.Frame(box, bg=C["soft"])
        card.pack(fill=tk.X, pady=(30, 0))
        self.audio_var = tk.StringVar()
        self.sub_var = tk.StringVar()
        self.audio_combo = self._option_row(card, "Langue audio", self.audio_var)
        tk.Frame(card, bg=C["line"], height=1).pack(fill=tk.X, padx=16)
        self.sub_combo = self._option_row(card, "Sous-titres", self.sub_var)

        self.btn_rip = PillButton(box, "Numériser le film", self.on_rip, self.F["btn"])
        self.btn_rip.pack(fill=tk.X, pady=(28, 0))
        self._label(box, "Enregistré dans Vidéos › Rips", "small", C["muted"]).pack(pady=(12, 0))

    def _option_row(self, card, title, var):
        row = tk.Frame(card, bg=C["soft"])
        row.pack(fill=tk.X, padx=16, pady=10)
        self._label(row, title, "body").pack(side=tk.LEFT)
        combo = ttk.Combobox(row, textvariable=var, state="readonly", width=18,
                             style="Soft.TCombobox", font=self.F["body"], justify=tk.RIGHT)
        combo.pack(side=tk.RIGHT)
        return combo

    def _page_encoding(self, box):
        self._label(box, "NUMÉRISATION EN COURS", "eyebrow", C["muted"]).pack()
        self.pct_var = tk.StringVar(value="0 %")
        tk.Label(box, textvariable=self.pct_var, font=self.F["pct"], fg=C["text"],
                 bg=C["bg"]).pack(pady=(4, 0))
        self.progress = ttk.Progressbar(box, mode="determinate", maximum=100,
                                        style="Slim.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=(14, 0))
        self.eta_var = tk.StringVar(value="Calcul du temps restant…")
        tk.Label(box, textvariable=self.eta_var, font=self.F["sub"], fg=C["muted"],
                 bg=C["bg"]).pack(pady=(14, 0))
        self.btn_stop = PillButton(box, "Arrêter", self.on_stop, self.F["body"],
                                   kind="ghost", height=40, width=130)
        self.btn_stop.pack(pady=(44, 0))

    def _page_done(self, box):
        _, _, self.done_sub = self._hero(box, "check", "Film enregistré", "")
        PillButton(box, "Ouvrir le dossier", self.open_folder,
                   self.F["btn"]).pack(fill=tk.X, pady=(34, 0))
        PillButton(box, "Numériser un autre DVD", self.start_scan, self.F["body"],
                   kind="link", height=36).pack(fill=tk.X, pady=(6, 0))

    def _page_error(self, box):
        _, self.err_title, self.err_sub = self._hero(box, "warn", "", "", warning=True)
        self.btn_retry = PillButton(box, "Réessayer", self.on_retry, self.F["btn"])
        self.btn_retry.pack(fill=tk.X, pady=(34, 0))
        PillButton(box, "Voir les détails", lambda: self.toggle_log(True), self.F["body"],
                   kind="link", height=36).pack(fill=tk.X, pady=(6, 0))

    def _page_missing(self, box):
        self._hero(box, "warn", "HandBrakeCLI est introuvable",
                   "RipDvD en a besoin pour numériser les disques. Installez la version "
                   "« ligne de commande », puis relancez RipDvD.", warning=True)
        cmd = tk.Entry(box, font=self.F["mono"], fg=C["text"], bg=C["soft"], relief=tk.FLAT,
                       justify=tk.CENTER, readonlybackground=C["soft"], bd=0)
        cmd.insert(0, "winget install HandBrake.HandBrake.CLI")
        cmd.config(state="readonly")
        cmd.pack(fill=tk.X, pady=(24, 0), ipady=8)
        PillButton(box, "Page de téléchargement", lambda: self._open_url(
            "https://handbrake.fr/downloads2.php"), self.F["body"],
            kind="link", height=36).pack(fill=tk.X, pady=(10, 0))

    # ------------------------------------------------------------ navigation
    def show(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill=tk.BOTH, expand=True)
        self.current = name

    def _show_empty(self, no_drive=False):
        if no_drive:
            self.empty_title.config(text="Aucun lecteur DVD")
            self.empty_sub.config(text="Branchez un lecteur, insérez un DVD, puis lancez l'analyse.")
        else:
            self.empty_title.config(text="Insérez un DVD")
            self.empty_sub.config(text="Le film est détecté automatiquement.")
        self.show("empty")

    def _show_error(self, title, sub, retry="Réessayer"):
        self.err_title.config(text=title)
        self.err_sub.config(text=sub)
        self.btn_retry.set_text(retry)
        self.show("error")

    def toggle_log(self, force=None):
        self.log_visible = (not self.log_visible) if force is None else force
        if self.log_visible:
            self.log_frame.pack(fill=tk.X, side=tk.BOTTOM)
        else:
            self.log_frame.pack_forget()

    def _log(self, text):
        self.after(0, lambda: (self.log.insert(tk.END, text), self.log.see(tk.END)))

    def _clear_log(self):
        self.log.delete("1.0", tk.END)

    # ------------------------------------------------------- analyse (moteur)
    def start_scan(self):
        if self.scanning or self.encoding:
            return
        if self.hb is None:
            self.show("missing")
            return
        self.drives = detect_dvd_drives() or self.drives
        self.drive_combo["values"] = self.drives
        if len(self.drives) > 1:
            self.drive_row.pack(pady=(22, 0), before=self.empty_btn)
        drive = (self.drive_var.get() or (self.drives[0] if self.drives else "")).strip()
        if not drive:
            self._show_empty(no_drive=True)
            return
        if not drive.endswith("\\"):
            drive += "\\"
        self.dvd_drive = drive
        self.scanning = True
        self.show("scanning")
        self._spin()
        self._clear_log()
        self._log("=== DVD SCAN ===\n")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _run_scan(self, args):
        proc = subprocess.Popen(self.hb + args, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        lines = []
        for line in proc.stdout:
            lines.append(line)
            self._log(line)
        proc.wait()
        return "".join(lines)

    def _scan_worker(self):
        try:
            self._log(f"Launching: {' '.join(self.hb)} -i {self.dvd_drive} --main-feature "
                      f"(fast scan, no previews)\n")
            scan0 = self._run_scan(["-i", self.dvd_drive, "--scan", "--main-feature",
                                    "--previews", "0"])
            best_title, best_ms = parse_title_scan(scan0)
            if best_ms == 0:
                self._log("\n[Fast scan returned nothing - full scan...]\n")
                scan0 = self._run_scan(["-i", self.dvd_drive, "--title", "0", "--previews", "0"])
                best_title, best_ms = parse_title_scan(scan0)
            if best_ms == 0:
                with open(DEBUG_LOG, "w") as f:
                    f.write(scan0)
                self.after(0, self._scan_failed)
                return
            self.best_title = best_title
            self.best_dur_min = best_ms // 60000
            self.audio_tracks, self.sub_tracks = parse_tracks_for_title(scan0, best_title)
            with open(DEBUG_LOG, "w") as f:
                f.write(f"=== TITLE {best_title} ({best_ms} ms) ===\n")
                f.write(scan0)
            self._log(f"\n-> Main title: {best_title} ({best_ms // 60000} min)\n")
            self._log(f"-> {len(self.audio_tracks)} audio track(s), "
                      f"{len(self.sub_tracks)} subtitle track(s).\n")
            self.after(0, self._scan_done)
        except Exception as e:
            self._log(f"\nScan error: {e}\n")
            self.after(0, self._scan_failed)

    def _scan_done(self):
        self.scanning = False
        self.audio_names = friendly_list([a[1] for a in self.audio_tracks])
        self.audio_combo["values"] = self.audio_names or ["(aucune)"]
        idx = 0
        for i, (_n, lbl) in enumerate(self.audio_tracks):
            low = lbl.lower()
            if "fran" in low or "fra" in low:
                idx = i
                break
        else:
            for i, (_n, lbl) in enumerate(self.audio_tracks):
                if "english" in lbl.lower() or "eng" in lbl.lower():
                    idx = i
                    break
        self.audio_var.set(self.audio_names[idx] if self.audio_names else "(aucune)")
        self.sub_names = ["Aucun"] + friendly_list([s[1] for s in self.sub_tracks])
        self.sub_combo["values"] = self.sub_names
        self.sub_var.set("Aucun")
        n = len(self.audio_tracks)
        self.ready_sub.config(
            text=f"{human_duration(self.best_dur_min)}  ·  {n} piste{'s' if n > 1 else ''} audio")
        self.btn_rip.set_enabled(True)
        self.show("ready")

    def _scan_failed(self):
        self.scanning = False
        self.retry_is_scan = True
        self._show_error("Disque illisible",
                         "Le disque est peut-être protégé (libdvdcss requis), rayé, "
                         "ou le lecteur n'est pas prêt.", "Analyser à nouveau")

    # --------------------------------------------------- numérisation (moteur)
    def on_rip(self):
        if self.encoding or self.scanning:
            return
        if not self.audio_tracks:
            self.start_scan()
            return
        a = self.audio_names.index(self.audio_var.get()) if self.audio_var.get() in self.audio_names else 0
        audio_idx = self.audio_tracks[a][0]
        s = self.sub_names.index(self.sub_var.get()) if self.sub_var.get() in self.sub_names else 0
        sub_idx = self.sub_tracks[s - 1][0] if s > 0 else None
        self.last_encode_params = (self.best_title, audio_idx, sub_idx)
        self._start_encode(resume=False)

    def on_retry(self):
        if self.retry_is_scan or self.last_encode_params is None:
            self.start_scan()
        else:
            self._start_encode(resume=True)

    def _start_encode(self, resume):
        if self.encoding or self.scanning:
            return
        self.retry_is_scan = False
        self.encoding = True
        self.stop_requested = False
        self.btn_stop.set_enabled(True)
        self.btn_stop.set_text("Arrêter")
        self._update_progress(0.0)
        self.eta_var.set("Calcul du temps restant…")
        self.show("encoding")
        self._clear_log()
        self._log("=== RESUME ENCODING ===\n" if resume else "=== ENCODING ===\n")
        threading.Thread(target=self._encode_worker, args=(resume,), daemon=True).start()

    def _encode_worker(self, resume):
        _title, audio_idx, sub_idx = self.last_encode_params
        name = f"DVD_{datetime.now():%Y%m%d_%H%M%S}" + ("_resume" if resume else "")
        os.makedirs(OUT_DIR, exist_ok=True)
        outfile = os.path.join(OUT_DIR, f"{name}.mkv")

        cmd = self.hb + [
            "-i", self.dvd_drive,
            "--main-feature",
            "-o", outfile,
            "--preset", "Fast 480p30",
            "--maxWidth", "720", "--maxHeight", "576",  # résolution DVD d'origine (PAL 576 / NTSC 480)
            "--encoder", "x264",
            "--quality", "20",
            "--encoder-preset", "fast",
            "--aencoder", "copy",
            "--audio-copy-mask", "aac,ac3,eac3,dts,dtshd,mp2,mp3",  # son d'origine copié tel quel
            "--audio-fallback", "av_aac",
            "--audio", str(audio_idx),
        ]
        if sub_idx is not None:
            cmd += ["--subtitle", str(sub_idx)]
        self._log("Command: " + " ".join(cmd) + "\n\n")

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True)
        except Exception as e:
            self._log(f"Launch failed: {e}\n")
            self.after(0, self._encode_failed)
            return

        tail = []
        for line in self.process.stdout:
            tail.append(line)
            if len(tail) > 50:
                tail.pop(0)
            self._log(line)
            m = re.search(r",\s*([\d.]+)\s*%", line)
            if m:
                self.after(0, lambda p=float(m.group(1)): self._update_progress(p))
            e = re.search(r"ETA (\d+)h(\d+)m(\d+)s", line)
            if e:
                txt = human_eta(*map(int, e.groups()))
                self.after(0, lambda t=txt: self.eta_var.set(t))

        self.process.wait()
        rc = self.process.returncode
        self.process = None

        with open(DEBUG_LOG, "a") as f:
            f.write(f"\n\n=== {'RESUME' if resume else 'ENCODE'} (rc={rc}) ===\n")
            f.write("CMD: " + " ".join(cmd) + "\n")
            f.write("".join(tail))

        if rc != 0 or not os.path.isfile(outfile) or os.path.getsize(outfile) == 0:
            self._log(f"\n[ERROR] Failed (code {rc}). Full log: {DEBUG_LOG}\n")
            self.after(0, self._encode_failed)
            return
        size = self._human_size(os.path.getsize(outfile))
        self.after(0, lambda: self._encode_ok(outfile, size))

    def _update_progress(self, pct):
        self.progress["value"] = pct
        self.pct_var.set(f"{int(pct)} %")

    def on_stop(self):
        if self.process is not None:
            self.stop_requested = True
            self.btn_stop.set_enabled(False)
            self.eta_var.set("Arrêt en cours…")
            try:
                self.process.terminate()
                self._log("\n[!] Stop requested by user.\n")
            except Exception:
                pass

    def _encode_ok(self, outfile, size):
        self.encoding = False
        self.last_outfile = outfile
        self.done_sub.config(text=f"{os.path.basename(outfile)}  ·  {size}")
        self._log(f"\n[OK] Done: {outfile} ({size})\n")
        self.show("done")
        self.bell()

    def _encode_failed(self):
        self.encoding = False
        if self.stop_requested:
            self._show_error("Numérisation arrêtée",
                             "Vous pouvez la relancer avec les mêmes réglages.", "Reprendre")
        else:
            self._show_error("La numérisation a échoué",
                             "Vérifiez le disque et l'espace libre, puis réessayez.")

    # ------------------------------------------------------------ secondaires
    def open_folder(self):
        os.makedirs(OUT_DIR, exist_ok=True)
        try:
            os.startfile(OUT_DIR)  # Windows
        except Exception:
            messagebox.showinfo("RipDvD", f"Vos films sont dans :\n{OUT_DIR}")

    @staticmethod
    def _open_url(url):
        import webbrowser
        webbrowser.open(url)

    def on_quit(self):
        if self.process is not None:
            if not messagebox.askyesno("Arrêter la numérisation ?",
                                       "Le film en cours ne sera pas enregistré.\n\n"
                                       "Arrêter et quitter ?", icon="warning"):
                return
            try:
                self.process.terminate()
            except Exception:
                pass
        self.destroy()

    def on_about(self):
        win = tk.Toplevel(self, bg=C["bg"])
        win.title("À propos de RipDvD")
        win.geometry("400x520")
        win.resizable(False, False)
        win.transient(self)
        box = tk.Frame(win, bg=C["bg"])
        box.place(relx=0.5, rely=0.46, anchor="center", relwidth=0.84)
        Bubble(box, "disc", size=80).pack()
        self._label(box, "RipDvD", "title").pack(pady=(18, 0))
        self._label(box, f"Version {VERSION}  ·  Pixel's ASBL", "sub", C["muted"]).pack(pady=(4, 0))
        self._label(box, "Vos DVD, sauvés en un clic.\nGratuit, sans publicité, licence MIT.",
                    "body", wraplength=320).pack(pady=(22, 0))
        self._label(box, "Aucune donnée n'est collectée : tout se passe sur votre ordinateur.\n"
                         "À utiliser pour vos propres DVD, au sein de votre foyer. Le "
                         "déchiffrement des disques protégés peut être restreint dans votre pays.",
                    "small", C["muted"], wraplength=320).pack(pady=(14, 0))
        self._label(box, "Construit avec HandBrake et libdvdcss (VideoLAN).",
                    "small", C["muted"]).pack(pady=(10, 0))
        PillButton(box, "Site du projet", lambda: self._open_url(
            "https://github.com/asblPixels/ripdvd"), self.F["btn"], height=44).pack(
            fill=tk.X, pady=(26, 0))
        PillButton(box, "Fermer", win.destroy, self.F["body"], kind="link",
                   height=34).pack(fill=tk.X, pady=(4, 0))

    @staticmethod
    def _human_size(n):
        for unit in ("o", "Ko", "Mo", "Go"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} To"


def main():
    app = RipDvDWin()
    app.mainloop()


if __name__ == "__main__":
    main()
