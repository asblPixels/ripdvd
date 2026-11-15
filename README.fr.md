<div align="center">

# 🎬 RipDvD

### Du disque au numérique — sans effort.

**Un rippeur de DVD minimaliste et open source pour Linux (Fedora / GNOME)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%26%20Windows-blue.svg)](https://github.com/asblPixels/ripdvd)
[![Desktop](https://img.shields.io/badge/desktop-GNOME%2049-green.svg)](https://gnome.org/)
[![GUI](https://img.shields.io/badge/GUI-GTK4%20%2F%20libadwaita-teal.svg)](https://gnome.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Backend](https://img.shields.io/badge/backend-HandBrakeCLI-orange.svg)](https://handbrake.fr/)
[![Release](https://img.shields.io/github/v/release/asblPixels/ripdvd.svg)](https://github.com/asblPixels/ripdvd/releases)

<br>

[🇬🇧 English](README.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇷🇺 Русский](README.ru.md) · [🇨🇳 中文](README.zh.md) · [🇯🇵 日本語](README.ja.md)

</div>

---

## 📖 À propos

**RipDvD** est une application gratuite et open source de rippage de DVD pour Linux et Windows.
Elle offre une interface graphique native (GTK4 / libadwaita sous Linux, tkinter sous Windows) par-dessus
[HandBrakeCLI](https://handbrake.fr/), transformant votre collection de DVD en fichiers MKV
de haute qualité prêts pour votre serveur multimédia (Jellyfin, Kodi, Plex).

> **Origine** : Ce projet est créé et maintenu par **[asblPixels](https://github.com/asblPixels)**
> dans le cadre de son initiative logicielle open source. Il est publié sous licence MIT
> et est libre d'utilisation, de modification et de distribution.

### ✨ Pourquoi RipDvD ?

La plupart des rippeurs de DVD sont soit en ligne de commande uniquement, soit trop complexes,
soit verrouillés à une plateforme, soit réservés à Windows.
RipDvD vise à être **l'outil le plus simple possible** qui fonctionne partout : insérez un disque, cliquez sur un bouton,
obtenez un MKV parfait. Aucune configuration requise, mais un contrôle total si vous le souhaitez.
Il fonctionne sur **Fedora, Arch, Ubuntu, Debian** (Linux) et **Windows 10/11**.

## 🎯 Fonctionnalités

- 🖱️ **Rippage en un clic** — insérez un DVD, cliquez sur *Rip DVD*, obtenez un MKV prêt à streamer.
- 🔍 **Détection automatique du titre** — sélectionne le titre le plus long (le film principal).
- 🌍 **Audio multilingue** — détecte toutes les pistes audio ; français par défaut, puis anglais.
- 💬 **Sous-titres** — passthrough optionnel de toute piste de sous-titres (VobSub), ou aucun.
- 📑 **Marqueurs de chapitres** — préservés dans le MKV pour une navigation facile dans Jellyfin/Kodi.
- 📺 **Fenêtre de sortie en direct** — log HandBrakeCLI en temps réel avec auto-scroll.
- 📊 **Barre de progression** — pourcentage mis à jour en direct pendant l'encodage.
- ⏸️ **Bouton Arrêter** — annule un encodage en cours à tout moment.
- 🔄 **Bouton Reprendre** — relance le dernier encodage avec les mêmes paramètres.
- 🚪 **Bouton Quitter** — ferme l'application proprement (arrête tout encodage en cours).
- 🔄 **Bouton Rescanner** — ré-analyse le disque sans redémarrer l'application.
- 🧹 **Effacer le log** — vide la fenêtre de sortie en direct.
- 🎨 **Apparence GNOME native** — GTK4 + libadwaita, s'intègre parfaitement à Fedora Workstation.
- 🧵 **Thread-safe** — toutes les mises à jour de l'interface sont envoyées au thread principal GTK.
- 🐛 **Log de debug** — sortie complète sauvegardée dans `~/.ripdvd-debug.log`.

## 📋 Profil de sortie par défaut

| Paramètre | Valeur |
|---|---|
| Conteneur | MKV (Matroska) |
| Codec vidéo | H.264 (x264), RF 20, preset `medium` |
| Résolution | Native DVD (480p NTSC / 576p PAL) — pas d'upscaling |
| Framerate | Source (25 / 29,97 fps) |
| Audio | Passthrough (copie) — conserve le 5.1 original si présent |
| Sous-titres | Passthrough (optionnel) |
| Chapitres | Préservés |
| Taille typique | ~1,0 – 1,5 Go par film de 2 heures |

> 💡 Les DVD sont des sources SD. Conserver la résolution native évite l'upscaling artificiel et garde
> les fichiers légers tout en restant beaux sur n'importe quelle TV.

## 🖥️ Systèmes supportés

| Composant | Prérequis |
|---|---|
| **Système d'exploitation** | Fedora 43+ (testé sur Fedora 45). Toute distribution récente basée sur Fedora/RHEL devrait fonctionner. |
| **Bureau** | GNOME (GTK4/libadwaita). Fonctionne sur X11 et Wayland. |
| **Architecture** | x86_64 |
| **CPU** | Tout x86_64 (encodage logiciel via x264). Aucun GPU requis. |
| **RAM** | 2 Go minimum, 4 Go recommandés |
| **Disque** | ~1,5 Go libre par film (sortie) + ~8 Go temp pendant l'encodage |
| **Lecteur optique** | Lecteur DVD interne ou USB (apparaît comme `/dev/sr0`) |

### Distributions supportées

Ce dépôt fournit des branches par distribution avec des installateurs adaptés :

| Branche | Distribution | Script d'installation |
|---|---|---|
| `main` / `fedora` | Fedora 43+ | `scripts/install.sh` |
| `arch` | Arch Linux | `scripts/install-arch.sh` |
| `ubuntu` | Ubuntu 22.04+ | `scripts/install-ubuntu.sh` |
| `debian` | Debian 12+ | `scripts/install-debian.sh` |
| `windows` | Windows 10/11 | `scripts/install-windows.ps1` |

Pour utiliser une branche spécifique :

```bash
git clone -b <branche> https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install-<distro>.sh   # ou .ps1 sous Windows
```

## 🚀 Installation

### Étape 1 — Téléchargement

```bash
git clone https://github.com/asblPixels/ripdvd.git
cd ripdvd
```

> Pas de `git` ? Téléchargez le ZIP depuis
> https://github.com/asblPixels/ripdvd/archive/refs/heads/main.zip et extrayez-le.

### Étape 2 — Installer les dépendances

```bash
sudo dnf install -y python3 python3-gobject gtk4 libadwaita zenity HandBrake HandBrake-cli
```

Pour les DVD commerciaux chiffrés, installez aussi `libdvdcss` :

```bash
sudo dnf install -y rpmfusion-free-release-tainted
sudo dnf install -y libdvdcss
```

### Étape 3 — Lancer l'installateur

```bash
bash scripts/install.sh
```

L'installateur va :
1. Vérifier les dépendances Python/GTK.
2. Installer HandBrake (natif, avec secours Flatpak si le natif est indisponible).
3. Copier l'application dans `~/.local/bin/ripdvd-gui.py`.
4. Enregistrer une entrée de menu GNOME (`ripdvd`).

### Étape 4 — Lancer

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

Ou cherchez **RipDvD** dans le menu d'applications GNOME.

### Windows

**Aucune connaissance technique requise !** Seulement 3 étapes :

1. **Téléchargez** le ZIP : https://github.com/asblPixels/ripdvd/archive/refs/heads/windows.zip
2. **Extrayez-le** dans un dossier (ex. votre Bureau).
3. **Double-cliquez** sur `install-windows.bat` et suivez les instructions à l'écran.

C'est tout ! Un raccourci **RipDvD** apparaîtra sur votre Bureau. Double-cliquez dessus pour commencer à ripper vos DVD.

> L'installateur vérifie automatiquement Python et HandBrake, et vous guide si quelque chose manque.

#### Étapes manuelles (si l'installateur ne fonctionne pas)

1. **Installer Python** : Téléchargez depuis https://www.python.org/downloads/ — cochez "Add Python to PATH".
2. **Installer HandBrake** : Téléchargez depuis https://handbrake.fr/downloads.php
3. **Lancer l'app** : `python ripdvd-win.py`

#### Notes Windows

- La version Windows utilise **tkinter** (intégré à Python) au lieu de GTK4.
- La détection du lecteur DVD est automatique. Si non détecté, entrez la lettre du lecteur manuellement (ex. `D:\`).
- libdvdcss est inclus avec HandBrake pour Windows.
- Les fichiers de sortie sont sauvegardés dans `%USERPROFILE%\Videos\Rips\`.

### Vérifier que tout fonctionne (toutes plateformes)

```bash
# Linux
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')"
command -v HandBrakeCLI && echo "HandBrakeCLI OK"

# Windows (PowerShell)
python -c "import tkinter; print('tkinter OK')"
Get-Command HandBrakeCLI
```

Les deux doivent afficher `OK`.

## 🎬 Utilisation

1. Insérez un DVD dans votre lecteur.
2. Lancez **RipDvD** depuis le menu GNOME (ou `python3 ~/.local/bin/ripdvd-gui.py`).
3. L'application scanne le disque automatiquement et détecte le film principal (titre le plus long).
4. Choisissez la **langue audio** et les **sous-titres** optionnels dans les listes déroulantes.
5. Cliquez sur **Rip DVD**.
6. Suivez la progression en direct dans la fenêtre de log.
7. Le MKV final se trouve dans `~/Vidéos/Rips/` (ou `~/Videos/Rips/`).

### Boutons

| Bouton | Action |
|---|---|
| **Rip DVD** | Démarre l'encodage du titre sélectionné. |
| **Arrêter** | Annule l'encodage en cours. |
| **Reprendre** | Relance le dernier encodage avec les mêmes paramètres. |
| **Quitter** | Ferme l'application (arrête tout encodage en cours). |
| **Rescanner** | Ré-analyse le disque (utile après avoir changé de DVD). |
| **Effacer log** | Vide la fenêtre de sortie en direct. |

### Version CLI

Un script bash headless est aussi fourni pour l'automatisation :

```bash
bash src/ripdvd-cli.sh
```

Il détecte automatiquement le titre le plus long et le rippe avec les mêmes paramètres par défaut, en affichant la progression via `zenity`.

## 🗂️ Structure du projet

```
ripdvd/
├── src/
│   ├── ripdvd.py          # Application GUI GTK4/libadwaita
│   └── ripdvd-cli.sh      # Ripper CLI headless
├── scripts/
│   └── install.sh         # Installateur Fedora
├── data/
│   └── ripdvd.desktop     # Entrée de menu GNOME
├── docs/
│   └── screenshot-main.png
├── .github/
│   ├── workflows/         # CI (vérifications de syntaxe)
│   └── ISSUE_TEMPLATE/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

## 🐛 Dépannage

### L'application ne démarre pas — `ModuleNotFoundError: No module named 'gi'`
Installez PyGObject : `sudo dnf install python3-gobject gtk4 libadwaita`

### Segfault / crash au démarrage
Assurez-vous d'être sur la dernière version (mises à jour thread-safe de l'interface). Relancez `bash scripts/install.sh`.

### DVD non détecté (`/dev/sr0` introuvable)
- Vérifiez que le lecteur est connecté : `lsblk | grep sr`
- Certains lecteurs USB ont besoin d'un moment après l'insertion ; cliquez sur **Rescanner**.

### Écran noir / "cannot read disc" sur les DVD chiffrés
Installez `libdvdcss` :
```bash
sudo dnf install rpmfusion-free-release-tainted
sudo dnf install libdvdcss
```

### Fichier de sortie vide
Ouvrez le log de debug (`~/.ripdvd-debug.log`) ou cliquez sur **Voir le log de debug**. Les dernières lignes montrent l'erreur HandBrake. Causes courantes :
- `libdvdcss` manquant pour les disques chiffrés.
- HandBrake Flatpak sans `--device=all` (corrigé dans la version actuelle).
- Espace disque insuffisant dans `~/Vidéos/Rips/`.

### Encodage lent sur les vieux CPU
C'est normal — l'encodage logiciel x264 sur un i3 Sandy Bridge prend ~10-15 min par film. L'application utilise le preset `medium` pour un bon compromis qualité/vitesse. Pour des rips plus rapides, modifiez `--encoder-preset` en `fast` ou `veryfast` dans `src/ripdvd.py`.

## 🙏 Remerciements

Ce projet n'existerait pas sans le travail incroyable de :

- **[HandBrake](https://handbrake.fr/)** et son équipe — le moteur d'encodage qui fait tout fonctionner.
- **[libdvdcss](https://www.videolan.org/developers/libdvdcss.html)** (VideoLAN) — le déchiffrement de DVD.
- **[GNOME / GTK4 / libadwaita](https://gnome.org/)** — la boîte à outils d'interface.
- **[RPM Fusion](https://rpmfusion.org/)** — le packaging pour Fedora.
- **[Projet Fedora](https://fedoraproject.org/)** — le système d'exploitation.
- Tous les contributeurs open source et la communauté.

## 📚 Sources et références

- Documentation CLI HandBrake : https://handbrake.fr/docs/en/latest/cli/
- Documentation libdvdcss : https://www.videolan.org/developers/libdvdcss.html
- Documentation GTK4 / libadwaita : https://docs.gtk.org/gtk4/ et https://gnome.pages.gitlab.gnome.org/libadwaita/
- Documentation PyGObject : https://pygobject.readthedocs.io/
- Configuration RPM Fusion : https://rpmfusion.org/Configuration
- Guide multimédia Fedora : https://docs.fedoraproject.org/en-US/quick-docs/assembly_installing-plugins-for-playing-movies-and-music/

## 👨‍💻 Créateurs

**RipDvD** est créé et maintenu par **[asblPixels](https://github.com/asblPixels)**
dans le cadre de son initiative logicielle open source.

Les contributions, rapports de bugs et demandes de fonctionnalités sont les bienvenus !

## 📜 Licence

Ce projet est sous licence **MIT** — voir [LICENSE](LICENSE) pour les détails.

## ⚠️ Note légale

Cet outil est destiné à la sauvegarde de DVD que vous possédez pour un usage personnel.
Le déchiffrement de disques protégés par copie peut être restreint dans votre pays. Vérifiez la législation locale.

---

<div align="center">

Fait avec ❤️ par [asblPixels](https://github.com/asblPixels) · Open Source · Licence MIT

</div>
