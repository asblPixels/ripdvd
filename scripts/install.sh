#!/usr/bin/env bash
# install-ripdvd.sh — installe ripdvd-gui sur Fedora/GNOME
set -e

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Installation des dépendances Python/GTK ==="
sudo dnf install -y python3 python3-gobject gtk4 libadwaita

echo "=== Vérification PyGObject ==="
python3 -c "import gi; print('PyGObject OK')" || { echo "❌ PyGObject manquant"; exit 1; }

echo "=== Installation HandBrake ==="
if ! command -v HandBrakeCLI >/dev/null 2>&1; then
    sudo dnf install -y HandBrake HandBrake-cli 2>&1 || true
fi
if ! command -v HandBrakeCLI >/dev/null 2>&1; then
    echo "⚠ HandBrakeCLI natif absent. Installation via flatpak..."
    if command -v flatpak >/dev/null 2>&1; then
        flatpak install -y flathub fr.handbrake.ghb
    fi
fi

echo "=== Installation zenity (pour messages d'erreur) ==="
sudo dnf install -y zenity 2>&1 || true

echo "=== Installation de l'application ==="
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
cp "$SRC_DIR/src/ripdvd.py" "$HOME/.local/bin/ripdvd-gui.py"
chmod +x "$HOME/.local/bin/ripdvd-gui.py"

sed "s|Exec=.*|Exec=python3 $HOME/.local/bin/ripdvd-gui.py|" \
    "$SRC_DIR/data/ripdvd.desktop" > "$HOME/.local/share/applications/ripdvd.desktop"

mkdir -p "$HOME/.local/share/icons/hicolor/scalable/apps"
cp "$SRC_DIR/data/ripdvd.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/ripdvd.svg"
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "=== Vérification finale ==="
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')" && echo "✅ Interface OK" || echo "❌ GTK4/Adw manquant"
command -v HandBrakeCLI >/dev/null 2>&1 && echo "✅ HandBrakeCLI natif OK" || echo "⚠ HandBrakeCLI natif absent (flatpak sera utilisé)"
echo ""
echo "=== Installation terminée ==="
echo "Lancez 'ripdvd' depuis le menu GNOME, ou :"
echo "  python3 ~/.local/bin/ripdvd-gui.py"
echo ""
echo "Prérequis DVD chiffrés :"
echo "  sudo dnf install rpmfusion-free-release-tainted"
echo "  sudo dnf install libdvdcss"
