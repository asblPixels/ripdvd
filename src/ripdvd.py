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
from gi.repository import Gtk, Adw, GLib, Gio, Pango

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


class RipdvdWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="RipDvD — par asblPixels")
        self.set_default_size(500, 720)
        self.set_resizable(True)

        self.hb, self.is_flatpak, self.hb_source = find_handbrake()
        self.process = None
        self.encoding = False
        self.scanning = False
        self.audio_tracks = []
        self.sub_tracks = []
        self.best_title = 1
        self.best_dur_min = 0
        self.last_encode_params = None  # (title, audio_idx, sub_idx, outfile) for resume

        # ---------- Layout ----------
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_margin_top(16)
        box.set_margin_bottom(12)
        box.set_margin_start(20)
        box.set_margin_end(20)

        title = Gtk.Label(label="RipDvD")
        title.add_css_class("title-1")
        title.set_margin_bottom(2)
        box.append(title)

        subtitle = Gtk.Label(label="Du disque au numérique — sans effort.")
        subtitle.add_css_class("dim-label")
        subtitle.set_margin_bottom(6)
        box.append(subtitle)

        # ---- Branding : asblPixels bien visible ----
        brand_btn = Gtk.Button(label="asblPixels")
        brand_btn.add_css_class("pill")
        brand_btn.add_css_class("suggested-action")
        brand_btn.set_halign(Gtk.Align.CENTER)
        brand_btn.set_tooltip_text("RipDvD est développé par asblPixels — cliquez pour les crédits et la licence")
        brand_btn.connect("clicked", self.on_about_clicked)
        box.append(brand_btn)

        brand_caption = Gtk.Label(label="Un logiciel libre développé par asblPixels")
        brand_caption.add_css_class("caption")
        brand_caption.add_css_class("dim-label")
        brand_caption.set_halign(Gtk.Align.CENTER)
        brand_caption.set_margin_top(4)
        brand_caption.set_margin_bottom(10)
        box.append(brand_caption)

        src_text = f"HandBrake : {self.hb_source or 'NON TROUVÉ'}"
        self.src_label = Gtk.Label(label=src_text)
        self.src_label.add_css_class("caption")
        self.src_label.add_css_class("dim-label")
        self.src_label.set_margin_bottom(10)
        box.append(self.src_label)

        self.status = Gtk.Label(label="Insertion d'un DVD puis scan automatique…")
        self.status.add_css_class("dim-label")
        self.status.set_wrap(True)
        self.status.set_justify(Gtk.Justification.CENTER)
        self.status.set_margin_bottom(8)
        box.append(self.status)

        audio_row = Adw.ActionRow(title="Langue audio")
        self.audio_combo = Gtk.DropDown()
        self.audio_combo.set_valign(Gtk.Align.CENTER)
        audio_row.add_suffix(self.audio_combo)
        audio_row.set_activatable_widget(self.audio_combo)
        box.append(audio_row)

        sub_row = Adw.ActionRow(title="Sous-titres")
        self.sub_combo = Gtk.DropDown()
        self.sub_combo.set_valign(Gtk.Align.CENTER)
        sub_row.add_suffix(self.sub_combo)
        sub_row.set_activatable_widget(self.sub_combo)
        box.append(sub_row)

        self.progress = Gtk.ProgressBar()
        self.progress.set_show_text(True)
        self.progress.set_text("0 %")
        self.progress.set_margin_top(12)
        self.progress.set_margin_bottom(10)
        box.append(self.progress)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_halign(Gtk.Align.CENTER)

        self.btn_rip = Gtk.Button(label="Rip DVD")
        self.btn_rip.add_css_class("suggested-action")
        self.btn_rip.add_css_class("pill")
        self.btn_rip.set_size_request(130, 40)
        self.btn_rip.connect("clicked", self.on_rip_clicked)
        btn_box.append(self.btn_rip)

        self.btn_stop = Gtk.Button(label="Arrêter")
        self.btn_stop.add_css_class("destructive-action")
        self.btn_stop.add_css_class("pill")
        self.btn_stop.set_size_request(100, 40)
        self.btn_stop.set_sensitive(False)
        self.btn_stop.connect("clicked", self.on_stop_clicked)
        btn_box.append(self.btn_stop)

        self.btn_refresh = Gtk.Button(label="Rescanner")
        self.btn_refresh.add_css_class("flat")
        self.btn_refresh.set_size_request(100, 40)
        self.btn_refresh.connect("clicked", lambda _b: self.start_scan())
        btn_box.append(self.btn_refresh)

        self.btn_clear = Gtk.Button(label="Effacer log")
        self.btn_clear.add_css_class("flat")
        self.btn_clear.set_size_request(100, 40)
        self.btn_clear.connect("clicked", lambda _b: self._clear_log())
        btn_box.append(self.btn_clear)

        self.btn_about = Gtk.Button(label="À propos")
        self.btn_about.add_css_class("flat")
        self.btn_about.set_size_request(90, 40)
        self.btn_about.connect("clicked", self.on_about_clicked)
        btn_box.append(self.btn_about)

        self.btn_resume = Gtk.Button(label="Reprendre")
        self.btn_resume.add_css_class("pill")
        self.btn_resume.set_size_request(110, 40)
        self.btn_resume.set_sensitive(False)
        self.btn_resume.connect("clicked", self.on_resume_clicked)
        btn_box.append(self.btn_resume)

        self.btn_quit = Gtk.Button(label="Quitter")
        self.btn_quit.add_css_class("destructive-action")
        self.btn_quit.add_css_class("pill")
        self.btn_quit.set_size_request(90, 40)
        self.btn_quit.connect("clicked", self.on_quit_clicked)
        btn_box.append(self.btn_quit)

        box.append(btn_box)

        self.out_label = Gtk.Label(label="")
        self.out_label.add_css_class("caption")
        self.out_label.add_css_class("dim-label")
        self.out_label.set_wrap(True)
        self.out_label.set_justify(Gtk.Justification.CENTER)
        self.out_label.set_margin_top(8)
        box.append(self.out_label)

        log_label = Gtk.Label(label="Sortie en direct")
        log_label.add_css_class("heading")
        log_label.set_halign(Gtk.Align.START)
        log_label.set_margin_top(10)
        log_label.set_margin_bottom(4)
        box.append(log_label)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.set_monospace(True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_buffer = self.log_view.get_buffer()

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(180)
        scrolled.set_child(self.log_view)
        scrolled.add_css_class("card")
        box.append(scrolled)

        # Footer with credits
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        footer_box.set_halign(Gtk.Align.CENTER)
        footer_box.set_margin_top(8)
        footer = Gtk.Label(label="© 2026 asblPixels — Licence MIT — Open Source")
        footer.add_css_class("caption")
        footer.add_css_class("accent")
        footer.set_halign(Gtk.Align.CENTER)
        footer_box.append(footer)
        footer_link = Gtk.LinkButton(uri="https://github.com/asblPixels/ripdvd",
                                     label="github.com/asblPixels/ripdvd")
        footer_link.add_css_class("caption")
        footer_link.set_halign(Gtk.Align.CENTER)
        footer_box.append(footer_link)
        box.append(footer_box)
        self._set_combo_items(self.sub_combo, ["Aucun"])

        if os.path.exists("/dev/sr0"):
            GLib.idle_add(self.start_scan)
        else:
            self.status.set_label("Insérez un DVD puis cliquez sur Rescanner.")

    # ---------- Combo helpers ----------
    def _set_combo_items(self, combo, labels):
        model = Gtk.StringList.new(labels)
        combo.set_model(model)

    def _combo_index(self, combo):
        sel = combo.get_selected()
        return sel if sel != Gtk.INVALID_LIST_POSITION else 0

    # ---------- Log helpers ----------
    def _append_log(self, text):
        def _do():
            end = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end, text)
            mark = self.log_buffer.get_insert()
            self.log_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
            return False
        GLib.idle_add(_do)

    def _clear_log(self):
        def _do():
            self.log_buffer.set_text("")
            return False
        GLib.idle_add(_do)

    # ---------- Scanning ----------
    def start_scan(self):
        if self.scanning or self.encoding:
            return
        if self.hb is None:
            self.show_error("HandBrakeCLI introuvable.\n"
                            "Installez : sudo dnf install HandBrake HandBrake-cli")
            return
        if not os.path.exists("/dev/sr0"):
            self.show_error("Aucun lecteur DVD détecté (/dev/sr0).\nInsérez un DVD.")
            return

        self.scanning = True
        self.btn_rip.set_sensitive(False)
        self.btn_refresh.set_sensitive(False)
        self.btn_resume.set_sensitive(False)
        self.status.set_label("Analyse du DVD…")
        self.progress.set_fraction(0.0)
        self.progress.set_text("…")
        self.out_label.set_label("")
        self._clear_log()
        self._append_log("=== SCAN DU DVD ===\n")

        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        try:
            self._append_log(f"Lancement : {' '.join(self.hb)} -i /dev/sr0 --title 0\n")
            proc = subprocess.Popen(
                self.hb + ["-i", "/dev/sr0", "--title", "0"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            lines = []
            for line in proc.stdout:
                lines.append(line)
                self._append_log(line)
            proc.wait()
            scan0 = "".join(lines)

            best_title, best_ms = parse_title_scan(scan0)
            if best_ms == 0:
                with open(DEBUG_LOG, "w") as f:
                    f.write(scan0)
                GLib.idle_add(self._scan_failed,
                              "Impossible d'analyser le DVD.\n"
                              "Vérifiez libdvdcss (DVD chiffré) ou le lecteur.\n"
                              f"Log : {DEBUG_LOG}")
                return

            self.best_title = best_title
            self.best_dur_min = best_ms // 60000

            # Parse tracks from the same full scan
            audio, subs = parse_tracks_for_title(scan0, best_title)
            self.audio_tracks = audio
            self.sub_tracks = subs

            with open(DEBUG_LOG, "w") as f:
                f.write(f"=== TITLE {best_title} ({best_ms} ms) ===\n")
                f.write(scan0)
                f.write("\n\n=== AUDIO ===\n" + repr(audio))
                f.write("\n=== SUBS ===\n" + repr(subs))

            self._append_log(f"\n→ Titre principal : {best_title} ({best_ms // 60000} min)\n")
            self._append_log(f"→ {len(audio)} piste(s) audio, {len(subs)} piste(s) sous-titres.\n")
            GLib.idle_add(self._scan_done)
        except Exception as e:
            GLib.idle_add(self._scan_failed, f"Erreur de scan :\n{e}")

    def _scan_done(self):
        self.scanning = False
        self.btn_rip.set_sensitive(True)
        self.btn_refresh.set_sensitive(True)
        self.btn_resume.set_sensitive(True)

        labels = [a[1] for a in self.audio_tracks]
        self._set_combo_items(self.audio_combo, labels if labels else ["(aucune)"])

        default_idx = 0
        for i, (idx, label) in enumerate(self.audio_tracks):
            low = label.lower()
            if "fran" in low or "fra" in low:
                default_idx = i
                break
        else:
            for i, (idx, label) in enumerate(self.audio_tracks):
                if "english" in label.lower() or "eng" in label.lower():
                    default_idx = i
                    break
        if self.audio_tracks:
            self.audio_combo.set_selected(default_idx)

        sub_labels = ["Aucun"] + [s[1] for s in self.sub_tracks]
        self._set_combo_items(self.sub_combo, sub_labels)
        self.sub_combo.set_selected(0)

        self.status.set_label(f"Titre {self.best_title} détecté ({self.best_dur_min} min). Prêt.")
        self.progress.set_fraction(0.0)
        self.progress.set_text("0 %")

    def _scan_failed(self, msg):
        self.scanning = False
        self.btn_rip.set_sensitive(True)
        self.btn_refresh.set_sensitive(True)
        self.btn_resume.set_sensitive(True)
        self.status.set_label("Échec du scan.")
        self._append_log(f"\n❌ {msg}\n")
        self.show_error(msg)

    # ---------- Encoding ----------
    def on_rip_clicked(self, _btn):
        if self.encoding or self.scanning:
            return
        if self.hb is None:
            self.show_error("HandBrakeCLI introuvable.")
            return
        if not os.path.exists("/dev/sr0"):
            self.show_error("Aucun lecteur DVD détecté.")
            return
        if not self.audio_tracks:
            self.show_error("Aucune piste audio détectée.\nRescannez le DVD.")
            return

        self.encoding = True
        self.btn_rip.set_sensitive(False)
        self.btn_stop.set_sensitive(True)
        self.btn_refresh.set_sensitive(False)
        self.btn_resume.set_sensitive(False)
        self.status.set_label("Encodage en cours…")
        self.progress.set_fraction(0.0)
        self.progress.set_text("0 %")
        self.out_label.set_label("")
        self._clear_log()
        self._append_log("=== ENCODAGE ===\n")

        threading.Thread(target=self._encode_worker, daemon=True).start()

    def _encode_worker(self):
        audio_idx = self.audio_tracks[self._combo_index(self.audio_combo)][0]
        sub_sel = self._combo_index(self.sub_combo)
        sub_idx = None
        if sub_sel > 0 and self.sub_tracks:
            sub_idx = self.sub_tracks[sub_sel - 1][0]

        # Save params for resume
        self.last_encode_params = (self.best_title, audio_idx, sub_idx)

        name = f"DVD_{datetime.now():%Y%m%d_%H%M%S}"
        os.makedirs(OUT_DIR, exist_ok=True)
        outfile = os.path.join(OUT_DIR, f"{name}.mkv")

        cmd = self.hb + [
            "-i", "/dev/sr0",
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

        self._append_log("Commande : " + " ".join(cmd) + "\n\n")

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
        except Exception as e:
            GLib.idle_add(self._encode_failed, f"Échec du lancement :\n{e}")
            return

        tail = []
        for line in self.process.stdout:
            tail.append(line)
            if len(tail) > 50:
                tail.pop(0)
            self._append_log(line)
            m = re.search(r",\s*([\d.]+)\s*%", line)
            if m:
                pct = float(m.group(1))
                GLib.idle_add(self._update_progress, pct)

        self.process.wait()
        rc = self.process.returncode
        self.process = None

        with open(DEBUG_LOG, "a") as f:
            f.write(f"\n\n=== ENCODE (rc={rc}) ===\n")
            f.write("CMD: " + " ".join(cmd) + "\n")
            f.write("".join(tail))

        if rc != 0:
            tail_text = "".join(tail[-20:]).strip()
            GLib.idle_add(self._encode_failed,
                          f"Échec de l'encodage (code {rc}).\n\n"
                          f"Dernières lignes :\n{tail_text}\n\n"
                          f"Log complet : {DEBUG_LOG}")
            return
        if not os.path.isfile(outfile) or os.path.getsize(outfile) == 0:
            tail_text = "".join(tail[-20:]).strip()
            GLib.idle_add(self._encode_failed,
                          f"Fichier de sortie vide ou absent.\n\n"
                          f"Dernières lignes :\n{tail_text}\n\n"
                          f"Log complet : {DEBUG_LOG}")
            return

        size = self._human_size(os.path.getsize(outfile))
        GLib.idle_add(self._encode_ok, outfile, size)

    def on_stop_clicked(self, _btn):
        if self.process is not None:
            try:
                self.process.terminate()
                self._append_log("\n⚠ Arrêt demandé par l'utilisateur.\n")
            except Exception:
                pass
        self.status.set_label("Arrêt demandé…")

    def on_resume_clicked(self, _btn):
        """Resume/retry the last encode with the same parameters."""
        if self.encoding or self.scanning:
            return
        if self.hb is None:
            self.show_error("HandBrakeCLI introuvable.")
            return
        if not os.path.exists("/dev/sr0"):
            self.show_error("Aucun lecteur DVD détecté.\nInsérez un DVD puis rescanner.")
            return
        if self.last_encode_params is None:
            # No previous params: rescan first
            self.start_scan()
            return
        # Re-encode with same params
        self.encoding = True
        self.btn_rip.set_sensitive(False)
        self.btn_resume.set_sensitive(False)
        self.btn_stop.set_sensitive(True)
        self.btn_refresh.set_sensitive(False)
        self.status.set_label("Reprise de l'encodage…")
        self.progress.set_fraction(0.0)
        self.progress.set_text("0 %")
        self.out_label.set_label("")
        self._clear_log()
        self._append_log("=== REPRISE DE L'ENCODAGE ===\n")
        threading.Thread(target=self._resume_worker, daemon=True).start()

    def _resume_worker(self):
        title, audio_idx, sub_idx = self.last_encode_params
        name = f"DVD_{datetime.now():%Y%m%d_%H%M%S}_resume"
        os.makedirs(OUT_DIR, exist_ok=True)
        outfile = os.path.join(OUT_DIR, f"{name}.mkv")

        cmd = self.hb + [
            "-i", "/dev/sr0",
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

        self._append_log("Commande : " + " ".join(cmd) + "\n\n")

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
        except Exception as e:
            GLib.idle_add(self._encode_failed, f"Échec du lancement :\n{e}")
            return

        tail = []
        for line in self.process.stdout:
            tail.append(line)
            if len(tail) > 50:
                tail.pop(0)
            self._append_log(line)
            m = re.search(r",\s*([\d.]+)\s*%", line)
            if m:
                pct = float(m.group(1))
                GLib.idle_add(self._update_progress, pct)

        self.process.wait()
        rc = self.process.returncode
        self.process = None

        with open(DEBUG_LOG, "a") as f:
            f.write(f"\n\n=== RESUME (rc={rc}) ===\n")
            f.write("CMD: " + " ".join(cmd) + "\n")
            f.write("".join(tail))

        if rc != 0:
            tail_text = "".join(tail[-20:]).strip()
            GLib.idle_add(self._encode_failed,
                          f"Échec de la reprise (code {rc}).\n\n"
                          f"Dernières lignes :\n{tail_text}\n\n"
                          f"Log complet : {DEBUG_LOG}")
            return
        if not os.path.isfile(outfile) or os.path.getsize(outfile) == 0:
            tail_text = "".join(tail[-20:]).strip()
            GLib.idle_add(self._encode_failed,
                          f"Fichier de sortie vide ou absent.\n\n"
                          f"Dernières lignes :\n{tail_text}\n\n"
                          f"Log complet : {DEBUG_LOG}")
            return

        size = self._human_size(os.path.getsize(outfile))
        GLib.idle_add(self._encode_ok, outfile, size)

    def on_quit_clicked(self, _btn):
        if self.process is not None:
            try:
                self.process.terminate()
                self._append_log("\n⚠ Arrêt du processus en cours avant de quitter.\n")
            except Exception:
                pass
        self.get_application().quit()

    def on_about_clicked(self, _btn):
        dialog = Adw.AboutDialog.new()
        dialog.set_application_name("RipDvD")
        dialog.set_application_icon("media-optical")
        dialog.set_version("1.1.0")
        dialog.set_comments("From disc to digital — effortlessly.\n\nOne-click DVD ripper for Linux & Windows.")
        dialog.set_copyright("© 2026 asblPixels — All rights reserved.")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_developers(["asblPixels (https://github.com/asblPixels)"])
        dialog.set_website("https://github.com/asblPixels/ripdvd")
        dialog.set_website_label("github.com/asblPixels/ripdvd")
        dialog.set_issue_url("https://github.com/asblPixels/ripdvd/issues")
        # Credits
        dialog.add_credit_section("Acknowledgements", [
            "HandBrake (https://handbrake.fr/) — encoding engine",
            "libdvdcss (VideoLAN) — DVD decryption",
            "GNOME / GTK4 / libadwaita — UI toolkit",
            "RPM Fusion — Fedora packaging",
            "Fedora Project — operating system",
        ])
        dialog.add_credit_section("Legal", [
            "This software is provided under the MIT License.",
            "For personal use — backing up DVDs you own.",
            "Decrypting copy-protected discs may be restricted in your country.",
            "Check your local laws before use.",
        ])
        dialog.present(self)

    def _update_progress(self, pct):
        self.progress.set_fraction(pct / 100.0)
        self.progress.set_text(f"{pct:.1f} %")

    def _encode_ok(self, outfile, size):
        self.encoding = False
        self.btn_rip.set_sensitive(True)
        self.btn_stop.set_sensitive(False)
        self.btn_refresh.set_sensitive(True)
        self.btn_resume.set_sensitive(True)
        self.status.set_label("Terminé ✅")
        self.progress.set_fraction(1.0)
        self.progress.set_text("100 %")
        self.out_label.set_label(f"{outfile}\n({size})")
        self._append_log(f"\n✅ Terminé : {outfile} ({size})\n")
        notif = Gio.Notification.new("RipDvD")
        notif.set_body(f"Encodage terminé : {os.path.basename(outfile)} ({size})")
        self.get_application().send_notification("ripdvd-done", notif)

    def _encode_failed(self, msg):
        self.encoding = False
        self.btn_rip.set_sensitive(True)
        self.btn_stop.set_sensitive(False)
        self.btn_refresh.set_sensitive(True)
        self.btn_resume.set_sensitive(True)
        self.status.set_label("Erreur")
        self.progress.set_fraction(0.0)
        self.progress.set_text("0 %")
        self._append_log(f"\n❌ {msg}\n")
        self.show_error(msg)

    def show_error(self, msg):
        dialog = Adw.AlertDialog.new("Erreur", msg)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present(self)

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

    def do_activate(self):
        win = RipdvdWindow(self)
        win.present()


def main():
    app = RipdvdApp()
    app.run()


if __name__ == "__main__":
    main()
