#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RipDvD-gui — One-click DVD ripper (GTK4/libadwaita, GNOME-native)."""

import os
import re
import subprocess
import threading
import shutil
import sys
from datetime import datetime

# ---- Dependency check ----
try:
    import gi
except ImportError:
    msg = ("Module Python 'gi' manquant.\n"
           "Installez : sudo dnf install python3-gobject gtk4 libadwaita")
    try:
        subprocess.run(["zenity", "--error", "--title=RipDvD", f"--text={msg}"])
    except Exception:
        print(msg, file=sys.stderr)
    sys.exit(1)

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Adw, GLib, Gio, Gdk, Pango

APP_ID = "io.github.ripdvd"
OUT_DIR = os.path.join(os.path.expanduser("~"), "Vidéos", "Rips")
DEBUG_LOG = os.path.join(os.path.expanduser("~"), ".ripdvd-debug.log")

def find_handbrake():
    if shutil.which("HandBrakeCLI"):
        return ["HandBrakeCLI"], False, "natif"
    if os.path.isfile("/app/bin/HandBrakeCLI"):
        return ["/app/bin/HandBrakeCLI"], False, "natif (/app)"
    try:
        r = subprocess.run(
            ["flatpak", "run", "--device=all", "--command=HandBrakeCLI",
             "fr.handbrake.ghb", "--version"],
            capture_output=True, timeout=20,
        )
        if r.returncode == 0:
            return ["flatpak", "run", "--device=all", "--command=HandBrakeCLI",
                    "fr.handbrake.ghb"], True, "flatpak"
    except Exception:
        pass
    return None, False, None


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
    """Parse audio/subtitle tracks for a specific title from a full (title 0) scan."""
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
                audio.append((cur_audio, f"Piste {cur_audio} — {lang}"))
                cur_audio = None
            elif cur_sub is not None and not any(s[0] == cur_sub for s in subs):
                subs.append((cur_sub, f"Piste {cur_sub} — {lang}"))
                cur_sub = None
    if not audio:
        audio = [(1, "Piste 1 — (inconnue)")]
    return audio, subs


VERSION = "1.3.0"

# ---- Thème : sobre, aéré, accent turquoise asblPixels ----
THEME_CSS = """
@define-color accent_color #00896e;
@define-color accent_bg_color #00a884;
@define-color accent_fg_color #ffffff;

/* Titres et chiffres */
.page-title   { font-size: 22pt; font-weight: 800; letter-spacing: -0.5px; }
.page-sub     { font-size: 11pt; opacity: 0.62; }
.big-percent  { font-size: 60pt; font-weight: 300; letter-spacing: -2px;
                font-feature-settings: "tnum"; }
.eyebrow      { font-size: 9pt; font-weight: 700; letter-spacing: 1.2px;
                opacity: 0.55; }

/* Pastille d'icône douce */
.icon-bubble  { background-color: alpha(@accent_bg_color, 0.12);
                color: @accent_color; border-radius: 999px; padding: 26px; }
.icon-bubble.warning { background-color: alpha(@warning_bg_color, 0.14);
                       color: @warning_color; }

/* Liste "verre" : pas de bordure, pas d'ombre */
.soft-list    { background-color: alpha(@window_fg_color, 0.045);
                border-radius: 18px; box-shadow: none; border: none; }
.soft-list > row { background-color: transparent; border-radius: 18px; }
.soft-list > row:not(:last-child) { border-bottom: 1px solid alpha(@window_fg_color, 0.06); }

/* Bouton d'action principal */
.cta          { min-height: 52px; border-radius: 26px; font-size: 12pt;
                font-weight: 700; padding-left: 28px; padding-right: 28px; }
.quiet        { opacity: 0.75; }

/* Barre de progression fine */
progressbar.slim > trough            { min-height: 6px; border-radius: 3px;
                                       background-color: alpha(@window_fg_color, 0.08); }
progressbar.slim > trough > progress { min-height: 6px; border-radius: 3px; }

/* Panneau du journal */
.log-panel    { background-color: alpha(@window_fg_color, 0.035); }
.log-view, .log-view text { background-color: transparent; font-size: 9pt; }
"""


def install_theme():
    """Applique le thème RipDvD à l'application."""
    css = Gtk.CssProvider()
    css.load_from_data(THEME_CSS.encode("utf-8"))
    display = Gdk.Display.get_default()
    if display is not None:
        Gtk.StyleContext.add_provider_for_display(
            display, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


def human_duration(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def human_eta(h, m, s):
    total = h * 60 + m + (1 if s >= 30 else 0)
    if total < 1:
        return "Moins d'une minute restante"
    return f"Environ {human_duration(total)} restantes"


def friendly_track(label):
    """« Piste 2 — Français (AC3) (5.1 ch) » → « Français · 5.1 »."""
    name = re.sub(r"^Piste \d+\s*—\s*", "", label)
    lang = name.split(" (")[0].strip() or name
    ch = re.search(r"\((\d\.\d) ch\)", name)
    return f"{lang} · {ch.group(1)}" if ch else lang


def friendly_list(labels):
    """Noms lisibles ; ajoute le n° de piste seulement en cas de doublon."""
    names = [friendly_track(l) for l in labels]
    out = []
    for i, (n, l) in enumerate(zip(names, labels)):
        if names.count(n) > 1:
            num = re.match(r"Piste (\d+)", l)
            n = f"{n} · piste {num.group(1)}" if num else n
        out.append(n)
    return out


def make_spinner(size=48):
    if hasattr(Adw, "Spinner"):  # libadwaita ≥ 1.6
        sp = Adw.Spinner()
    else:
        sp = Gtk.Spinner()
        sp.start()
    sp.set_size_request(size, size)
    sp.set_halign(Gtk.Align.CENTER)
    return sp


class RipdvdWindow(Adw.ApplicationWindow):
    DRIVE = "/dev/sr0"

    def __init__(self, app):
        super().__init__(application=app, title="RipDvD")
        self.set_default_size(460, 640)
        self.set_size_request(360, 520)

        self.hb, self.is_flatpak, self.hb_source = find_handbrake()
        self.process = None
        self.encoding = False
        self.scanning = False
        self.stop_requested = False
        self.audio_tracks = []
        self.sub_tracks = []
        self.best_title = 1
        self.best_dur_min = 0
        self.last_encode_params = None   # (titre, piste audio, piste sous-titres)
        self.last_outfile = None

        self._build_actions()
        self.set_content(self._build_ui())
        self.connect("close-request", self._on_close_request)

        if self.hb is None:
            self.stack.set_visible_child_name("missing")
        elif os.path.exists(self.DRIVE):
            GLib.idle_add(self.start_scan)
        else:
            self._show_empty(no_drive=True)

    # ================================================================
    #  Construction de l'interface
    # ================================================================
    def _build_actions(self):
        def add(name, cb):
            act = Gio.SimpleAction.new(name, None)
            act.connect("activate", lambda *_: cb())
            self.add_action(act)
            return act

        self.act_rescan = add("rescan", self.start_scan)
        add("open-folder", self.open_folder)
        add("about", self.show_about)
        add("quit", self.close)
        self.act_log = Gio.SimpleAction.new_stateful(
            "show-log", None, GLib.Variant.new_boolean(False))
        self.act_log.connect("change-state", self._on_toggle_log)
        self.add_action(self.act_log)

    def _build_ui(self):
        # ---- Barre de titre : titre seul + menu des options secondaires
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title="RipDvD", subtitle=""))

        menu = Gio.Menu()
        main = Gio.Menu()
        main.append("Analyser le disque", "win.rescan")
        main.append("Ouvrir le dossier des films", "win.open-folder")
        main.append("Afficher le journal", "win.show-log")
        menu.append_section(None, main)
        other = Gio.Menu()
        other.append("À propos de RipDvD", "win.about")
        other.append("Quitter", "win.quit")
        menu.append_section(None, other)
        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        menu_btn.set_tooltip_text("Menu")
        header.pack_end(menu_btn)

        # ---- Pages (une seule visible à la fois)
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE,
                               transition_duration=220, vexpand=True)
        self.stack.add_named(self._page_empty(), "empty")
        self.stack.add_named(self._page_scanning(), "scanning")
        self.stack.add_named(self._page_ready(), "ready")
        self.stack.add_named(self._page_encoding(), "encoding")
        self.stack.add_named(self._page_done(), "done")
        self.stack.add_named(self._page_error(), "error")
        self.stack.add_named(self._page_missing(), "missing")

        clamp = Adw.Clamp(maximum_size=420, tightening_threshold=360, child=self.stack)
        clamp.set_margin_start(28)
        clamp.set_margin_end(28)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        body.append(clamp)
        body.append(self._log_panel())

        self.toasts = Adw.ToastOverlay(child=body)

        view = Adw.ToolbarView()
        view.add_top_bar(header)
        view.set_content(self.toasts)

        self._set_model(self.audio_row, ["—"])
        self._set_model(self.sub_row, ["Aucun"])
        return view

    # ---- Briques réutilisables
    @staticmethod
    def _vbox(spacing=0, center=True):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
        if center:
            box.set_valign(Gtk.Align.CENTER)
        box.set_vexpand(True)
        box.set_margin_top(32)
        box.set_margin_bottom(40)
        return box

    @staticmethod
    def _bubble(icon, warning=False):
        img = Gtk.Image.new_from_icon_name(icon)
        img.set_pixel_size(44)
        img.add_css_class("icon-bubble")
        if warning:
            img.add_css_class("warning")
        img.set_halign(Gtk.Align.CENTER)
        return img

    @staticmethod
    def _label(text, css, wrap=True):
        lbl = Gtk.Label(label=text, wrap=wrap, justify=Gtk.Justification.CENTER)
        lbl.set_halign(Gtk.Align.CENTER)
        for c in css.split():
            lbl.add_css_class(c)
        return lbl

    @staticmethod
    def _cta(text, cb, full=True):
        btn = Gtk.Button(label=text)
        btn.add_css_class("suggested-action")
        btn.add_css_class("cta")
        if not full:
            btn.set_halign(Gtk.Align.CENTER)
        btn.connect("clicked", lambda _b: cb())
        return btn

    @staticmethod
    def _link(text, cb):
        btn = Gtk.Button(label=text, halign=Gtk.Align.CENTER)
        btn.add_css_class("flat")
        btn.add_css_class("quiet")
        btn.connect("clicked", lambda _b: cb())
        return btn

    def _hero(self, box, icon, title, sub, warning=False):
        box.append(self._bubble(icon, warning))
        t = self._label(title, "page-title")
        t.set_margin_top(28)
        box.append(t)
        s = self._label(sub, "page-sub")
        s.set_margin_top(8)
        box.append(s)
        return t, s

    # ---- 1. Aucun disque
    def _page_empty(self):
        box = self._vbox()
        self.empty_title, self.empty_sub = self._hero(
            box, "media-optical-symbolic", "Insérez un DVD",
            "Le film est détecté automatiquement.")
        btn = self._cta("Analyser le disque", self.start_scan, full=False)
        btn.set_margin_top(40)
        box.append(btn)
        return box

    # ---- 2. Analyse
    def _page_scanning(self):
        box = self._vbox()
        box.append(make_spinner(48))
        t = self._label("Analyse du disque", "page-title")
        t.set_margin_top(32)
        box.append(t)
        s = self._label("Recherche du film principal…", "page-sub")
        s.set_margin_top(8)
        box.append(s)
        return box

    # ---- 3. Prêt
    def _page_ready(self):
        box = self._vbox(center=False)
        box.set_valign(Gtk.Align.CENTER)

        box.append(self._bubble("media-optical-symbolic"))
        t = self._label("Film détecté", "page-title")
        t.set_margin_top(24)
        box.append(t)
        self.ready_sub = self._label("", "page-sub")
        self.ready_sub.set_margin_top(6)
        box.append(self.ready_sub)

        lst = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        lst.add_css_class("boxed-list")
        lst.add_css_class("soft-list")
        lst.set_margin_top(36)
        self.audio_row = Adw.ComboRow(title="Langue audio")
        self.sub_row = Adw.ComboRow(title="Sous-titres")
        lst.append(self.audio_row)
        lst.append(self.sub_row)
        box.append(lst)

        self.btn_rip = self._cta("Numériser le film", self.on_rip_clicked)
        self.btn_rip.set_margin_top(32)
        box.append(self.btn_rip)

        hint = self._label("Enregistré dans Vidéos › Rips", "caption dim-label")
        hint.set_margin_top(14)
        box.append(hint)
        return box

    # ---- 4. Numérisation en cours
    def _page_encoding(self):
        box = self._vbox()
        eyebrow = self._label("NUMÉRISATION EN COURS", "eyebrow", wrap=False)
        box.append(eyebrow)
        self.pct_label = self._label("0 %", "big-percent", wrap=False)
        self.pct_label.set_margin_top(10)
        box.append(self.pct_label)

        self.progress = Gtk.ProgressBar()
        self.progress.add_css_class("slim")
        self.progress.set_margin_top(20)
        box.append(self.progress)

        self.eta_label = self._label("Calcul du temps restant…", "page-sub")
        self.eta_label.set_margin_top(16)
        box.append(self.eta_label)

        self.btn_stop = Gtk.Button(label="Arrêter", halign=Gtk.Align.CENTER)
        self.btn_stop.add_css_class("pill")
        self.btn_stop.set_margin_top(48)
        self.btn_stop.connect("clicked", self.on_stop_clicked)
        box.append(self.btn_stop)
        return box

    # ---- 5. Terminé
    def _page_done(self):
        box = self._vbox()
        _, self.done_sub = self._hero(box, "object-select-symbolic",
                                      "Film enregistré", "")
        btn = self._cta("Ouvrir le dossier", self.open_folder)
        btn.set_margin_top(40)
        box.append(btn)
        again = self._link("Numériser un autre DVD", self.start_scan)
        again.set_margin_top(8)
        box.append(again)
        return box

    # ---- 6. Erreur / interruption
    def _page_error(self):
        box = self._vbox()
        self.err_title, self.err_sub = self._hero(
            box, "dialog-warning-symbolic", "", "", warning=True)
        self.btn_retry = self._cta("Réessayer", self.on_retry_clicked)
        self.btn_retry.set_margin_top(40)
        box.append(self.btn_retry)
        details = self._link("Voir les détails", lambda: self.act_log.change_state(
            GLib.Variant.new_boolean(True)))
        details.set_margin_top(8)
        box.append(details)
        return box

    # ---- 7. HandBrake absent
    def _page_missing(self):
        box = self._vbox()
        self._hero(box, "dialog-warning-symbolic", "HandBrake est introuvable",
                   "RipDvD utilise HandBrakeCLI pour numériser les disques. "
                   "Installez-le, puis relancez RipDvD.", warning=True)
        cmd = Gtk.Label(label="sudo dnf install HandBrake-cli", selectable=True)
        cmd.add_css_class("monospace")
        cmd.add_css_class("dim-label")
        cmd.set_margin_top(28)
        box.append(cmd)
        return box

    # ---- Journal (replié par défaut)
    def _log_panel(self):
        self.log_view = Gtk.TextView(editable=False, cursor_visible=False,
                                     monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.log_view.add_css_class("log-view")
        self.log_view.set_left_margin(16)
        self.log_view.set_right_margin(16)
        self.log_buffer = self.log_view.get_buffer()

        scrolled = Gtk.ScrolledWindow(vexpand=False)
        scrolled.set_min_content_height(170)
        scrolled.set_child(self.log_view)

        bar = Gtk.Box(spacing=6)
        bar.set_margin_start(16)
        bar.set_margin_end(8)
        bar.set_margin_top(6)
        bar.set_margin_bottom(2)
        title = Gtk.Label(label="Journal", xalign=0, hexpand=True)
        title.add_css_class("heading")
        bar.append(title)
        for icon, tip, cb in (("edit-clear-all-symbolic", "Effacer", self._clear_log),
                              ("window-close-symbolic", "Masquer",
                               lambda: self.act_log.change_state(GLib.Variant.new_boolean(False)))):
            b = Gtk.Button(icon_name=icon, tooltip_text=tip)
            b.add_css_class("flat")
            b.add_css_class("circular")
            b.connect("clicked", lambda _b, f=cb: f())
            bar.append(b)

        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel.add_css_class("log-panel")
        panel.append(bar)
        panel.append(scrolled)

        self.log_revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_UP, child=panel)
        return self.log_revealer

    def _on_toggle_log(self, action, value):
        action.set_state(value)
        self.log_revealer.set_reveal_child(value.get_boolean())

    # ================================================================
    #  Petits utilitaires
    # ================================================================
    @staticmethod
    def _set_model(row, labels):
        row.set_model(Gtk.StringList.new(labels))

    @staticmethod
    def _row_index(row):
        sel = row.get_selected()
        return sel if sel != Gtk.INVALID_LIST_POSITION else 0

    def _append_log(self, text):
        def _do():
            self.log_buffer.insert(self.log_buffer.get_end_iter(), text)
            self.log_view.scroll_to_mark(self.log_buffer.get_insert(), 0.0, True, 0.0, 1.0)
            return False
        GLib.idle_add(_do)

    def _clear_log(self):
        GLib.idle_add(lambda: self.log_buffer.set_text("") or False)

    def toast(self, text):
        self.toasts.add_toast(Adw.Toast(title=text, timeout=3))

    def _busy(self, busy):
        self.act_rescan.set_enabled(not busy)

    def _show_empty(self, no_drive=False):
        if no_drive:
            self.empty_title.set_label("Aucun lecteur DVD")
            self.empty_sub.set_label("Branchez un lecteur, insérez un DVD, puis lancez l'analyse.")
        else:
            self.empty_title.set_label("Insérez un DVD")
            self.empty_sub.set_label("Le film est détecté automatiquement.")
        self.stack.set_visible_child_name("empty")

    def _show_error(self, title, sub, retry_label="Réessayer"):
        self.err_title.set_label(title)
        self.err_sub.set_label(sub)
        self.btn_retry.set_label(retry_label)
        self.stack.set_visible_child_name("error")

    # ================================================================
    #  Analyse du disque (moteur inchangé)
    # ================================================================
    def start_scan(self):
        if self.scanning or self.encoding:
            return
        if self.hb is None:
            self.stack.set_visible_child_name("missing")
            return
        if not os.path.exists(self.DRIVE):
            self._show_empty(no_drive=True)
            return
        self.scanning = True
        self._busy(True)
        self.stack.set_visible_child_name("scanning")
        self._clear_log()
        self._append_log("=== SCAN DU DVD ===\n")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _run_scan(self, args):
        """Lance un scan HandBrakeCLI et renvoie sa sortie complète."""
        proc = subprocess.Popen(self.hb + args, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        lines = []
        for line in proc.stdout:
            lines.append(line)
            self._append_log(line)
        proc.wait()
        return "".join(lines)

    def _scan_worker(self):
        try:
            drive = self.DRIVE
            self._append_log(f"Lancement : {' '.join(self.hb)} -i {drive} --main-feature "
                             f"(scan rapide, sans aperçus)\n")
            scan0 = self._run_scan(["-i", drive, "--scan", "--main-feature", "--previews", "0"])
            best_title, best_ms = parse_title_scan(scan0)

            if best_ms == 0:
                self._append_log("\n[Scan rapide sans résultat — analyse complète…]\n")
                scan0 = self._run_scan(["-i", drive, "--title", "0", "--previews", "0"])
                best_title, best_ms = parse_title_scan(scan0)

            if best_ms == 0:
                with open(DEBUG_LOG, "w") as f:
                    f.write(scan0)
                GLib.idle_add(self._scan_failed)
                return

            self.best_title = best_title
            self.best_dur_min = best_ms // 60000
            audio, subs = parse_tracks_for_title(scan0, best_title)
            self.audio_tracks, self.sub_tracks = audio, subs

            with open(DEBUG_LOG, "w") as f:
                f.write(f"=== TITLE {best_title} ({best_ms} ms) ===\n")
                f.write(scan0)
                f.write("\n\n=== AUDIO ===\n" + repr(audio))
                f.write("\n=== SUBS ===\n" + repr(subs))

            self._append_log(f"\n→ Titre principal : {best_title} ({best_ms // 60000} min)\n")
            self._append_log(f"→ {len(audio)} piste(s) audio, {len(subs)} piste(s) sous-titres.\n")
            GLib.idle_add(self._scan_done)
        except Exception as e:
            self._append_log(f"\nErreur de scan : {e}\n")
            GLib.idle_add(self._scan_failed)

    def _scan_done(self):
        self.scanning = False
        self._busy(False)

        self._set_model(self.audio_row, friendly_list([a[1] for a in self.audio_tracks]) or ["(aucune)"])
        default_idx = 0
        for i, (_idx, label) in enumerate(self.audio_tracks):
            low = label.lower()
            if "fran" in low or "fra" in low:
                default_idx = i
                break
        else:
            for i, (_idx, label) in enumerate(self.audio_tracks):
                if "english" in label.lower() or "eng" in label.lower():
                    default_idx = i
                    break
        if self.audio_tracks:
            self.audio_row.set_selected(default_idx)

        self._set_model(self.sub_row, ["Aucun"] + friendly_list([s[1] for s in self.sub_tracks]))
        self.sub_row.set_selected(0)

        n = len(self.audio_tracks)
        self.ready_sub.set_label(
            f"{human_duration(self.best_dur_min)}  ·  {n} piste{'s' if n > 1 else ''} audio")
        self.stack.set_visible_child_name("ready")
        return False

    def _scan_failed(self):
        self.scanning = False
        self._busy(False)
        self._show_error("Disque illisible",
                         "Le disque est peut-être protégé (libdvdcss requis), rayé, "
                         "ou le lecteur n'est pas prêt.", "Analyser à nouveau")
        self._retry_is_scan = True
        return False

    # ================================================================
    #  Numérisation (commande HandBrake inchangée)
    # ================================================================
    def on_rip_clicked(self):
        if self.encoding or self.scanning:
            return
        if not self.audio_tracks:
            self.start_scan()
            return
        audio_idx = self.audio_tracks[self._row_index(self.audio_row)][0]
        sub_sel = self._row_index(self.sub_row)
        sub_idx = self.sub_tracks[sub_sel - 1][0] if sub_sel > 0 and self.sub_tracks else None
        self.last_encode_params = (self.best_title, audio_idx, sub_idx)
        self._start_encode(resume=False)

    def on_retry_clicked(self):
        if getattr(self, "_retry_is_scan", False) or self.last_encode_params is None:
            self.start_scan()
        else:
            self._start_encode(resume=True)

    def _start_encode(self, resume):
        if self.encoding or self.scanning:
            return
        if not os.path.exists(self.DRIVE):
            self._show_empty(no_drive=True)
            return
        self._retry_is_scan = False
        self.encoding = True
        self.stop_requested = False
        self._busy(True)
        self.btn_stop.set_sensitive(True)
        self._update_progress(0.0)
        self.eta_label.set_label("Calcul du temps restant…")
        self.stack.set_visible_child_name("encoding")
        self._clear_log()
        self._append_log("=== REPRISE DE L'ENCODAGE ===\n" if resume else "=== ENCODAGE ===\n")
        threading.Thread(target=self._encode_worker, args=(resume,), daemon=True).start()

    def _encode_worker(self, resume):
        _title, audio_idx, sub_idx = self.last_encode_params
        name = f"DVD_{datetime.now():%Y%m%d_%H%M%S}" + ("_resume" if resume else "")
        os.makedirs(OUT_DIR, exist_ok=True)
        outfile = os.path.join(OUT_DIR, f"{name}.mkv")

        cmd = self.hb + [
            "-i", self.DRIVE,
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
        self._append_log("Commande : " + " ".join(cmd) + "\n\n")

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True)
        except Exception as e:
            self._append_log(f"Échec du lancement : {e}\n")
            GLib.idle_add(self._encode_failed)
            return

        tail = []
        for line in self.process.stdout:
            tail.append(line)
            if len(tail) > 50:
                tail.pop(0)
            self._append_log(line)
            m = re.search(r",\s*([\d.]+)\s*%", line)
            if m:
                GLib.idle_add(self._update_progress, float(m.group(1)))
            e = re.search(r"ETA (\d+)h(\d+)m(\d+)s", line)
            if e:
                GLib.idle_add(self.eta_label.set_label, human_eta(*map(int, e.groups())))

        self.process.wait()
        rc = self.process.returncode
        self.process = None

        with open(DEBUG_LOG, "a") as f:
            f.write(f"\n\n=== {'RESUME' if resume else 'ENCODE'} (rc={rc}) ===\n")
            f.write("CMD: " + " ".join(cmd) + "\n")
            f.write("".join(tail))

        if rc != 0 or not os.path.isfile(outfile) or os.path.getsize(outfile) == 0:
            self._append_log(f"\n❌ Échec (code {rc}). Log complet : {DEBUG_LOG}\n")
            GLib.idle_add(self._encode_failed)
            return
        GLib.idle_add(self._encode_ok, outfile, self._human_size(os.path.getsize(outfile)))

    def _update_progress(self, pct):
        self.progress.set_fraction(pct / 100.0)
        self.pct_label.set_label(f"{int(pct)} %")
        return False

    def on_stop_clicked(self, _btn=None):
        if self.process is not None:
            self.stop_requested = True
            self.btn_stop.set_sensitive(False)
            self.eta_label.set_label("Arrêt en cours…")
            try:
                self.process.terminate()
                self._append_log("\n⚠ Arrêt demandé par l'utilisateur.\n")
            except Exception:
                pass

    def _encode_ok(self, outfile, size):
        self.encoding = False
        self._busy(False)
        self.last_outfile = outfile
        self.done_sub.set_label(f"{os.path.basename(outfile)}  ·  {size}")
        self.stack.set_visible_child_name("done")
        self._append_log(f"\n✅ Terminé : {outfile} ({size})\n")
        notif = Gio.Notification.new("RipDvD")
        notif.set_body(f"Film enregistré : {os.path.basename(outfile)} ({size})")
        self.get_application().send_notification("ripdvd-done", notif)
        return False

    def _encode_failed(self):
        self.encoding = False
        self._busy(False)
        if self.stop_requested:
            self._show_error("Numérisation arrêtée",
                             "Vous pouvez la relancer avec les mêmes réglages.", "Reprendre")
        else:
            self._show_error("La numérisation a échoué",
                             "Vérifiez le disque et l'espace libre, puis réessayez.")
        return False

    # ================================================================
    #  Actions secondaires
    # ================================================================
    def open_folder(self):
        os.makedirs(OUT_DIR, exist_ok=True)
        try:
            Gio.AppInfo.launch_default_for_uri(Gio.File.new_for_path(OUT_DIR).get_uri(), None)
        except Exception:
            self.toast(f"Dossier : {OUT_DIR}")

    def _on_close_request(self, _win):
        if self.process is None:
            return False
        dialog = Adw.AlertDialog.new("Arrêter la numérisation ?",
                                     "Le film en cours ne sera pas enregistré.")
        dialog.add_response("cancel", "Continuer")
        dialog.add_response("quit", "Arrêter et quitter")
        dialog.set_response_appearance("quit", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")

        def on_response(_d, resp):
            if resp == "quit":
                if self.process is not None:
                    try:
                        self.process.terminate()
                    except Exception:
                        pass
                self.get_application().quit()
        dialog.connect("response", on_response)
        dialog.present(self)
        return True

    def show_about(self):
        about = Adw.AboutDialog(
            application_name="RipDvD",
            application_icon="ripdvd",
            developer_name="Pixel's ASBL",
            version=VERSION,
            comments="Vos DVD, sauvés en un clic.\n"
                     "Numérise le film principal d'un DVD en fichier MKV, "
                     "avec son son d'origine et ses chapitres.",
            website="https://github.com/asblPixels/ripdvd",
            issue_url="https://github.com/asblPixels/ripdvd/issues",
            license_type=Gtk.License.MIT_X11,
            copyright="© 2026 Pixel's ASBL — Boussu",
        )
        about.add_credit_section("Construit avec", [
            "HandBrake https://handbrake.fr",
            "libdvdcss (VideoLAN) https://www.videolan.org",
            "GTK 4 et libadwaita https://gnome.org",
        ])
        about.add_legal_section(
            "Vie privée", None, Gtk.License.CUSTOM,
            "Aucune donnée n'est collectée ni transmise : tout se passe sur votre ordinateur.")
        about.add_legal_section(
            "Usage", None, Gtk.License.CUSTOM,
            "RipDvD sert à copier des DVD que vous possédez, pour votre foyer. "
            "Le déchiffrement des disques protégés peut être restreint dans votre pays.")
        about.set_debug_info(f"HandBrake : {self.hb_source or 'introuvable'}\n"
                             f"Journal : {DEBUG_LOG}\nSortie : {OUT_DIR}")
        about.present(self)

    @staticmethod
    def _human_size(n):
        for unit in ("o", "Ko", "Mo", "Go"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} To"


class RipdvdApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_startup(self):
        Adw.Application.do_startup(self)
        self.set_accels_for_action("win.quit", ["<Control>q"])
        self.set_accels_for_action("win.rescan", ["<Control>r"])
        self.set_accels_for_action("win.show-log", ["<Control>l"])

    def do_activate(self):
        install_theme()
        Gtk.Window.set_default_icon_name("ripdvd")
        win = self.props.active_window or RipdvdWindow(self)
        win.present()


def main():
    app = RipdvdApp()
    app.run()


if __name__ == "__main__":
    main()
