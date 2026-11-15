#!/usr/bin/env bash
# install-ripdvd-arch.sh — installe ripdvd-gui sur Arch Linux
set -e

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Installation des dépendances (pacman) ==="
sudo pacman -Sy --needed --noconfirm python python-gobject gtk4 libadwaita zenity handbrake

echo "=== Vérification PyGObject ==="
python3 -c "import gi; print('PyGObject OK')" || { echo "❌ PyGObject manquant"; exit 1; }

echo "=== Installation libdvdcss (AUR) ==="
if ! pacman -Q libdvdcss >/dev/null 2>&1; then
    echo "⚠ libdvdcss non trouvé. Installez-le depuis l'AUR :"
    echo "   yay -S libdvdcss   # ou paru -S libdvdcss"
    echo "   (ou compilez depuis https://www.videolan.org/developers/libdvdcss.html)"
fi

echo "=== Installation de l'application ==="
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
cp "$SRC_DIR/src/ripdvd.py" "$HOME/.local/bin/ripdvd-gui.py"
chmod +x "$HOME/.local/bin/ripdvd-gui.py"

sed "s|Exec=.*|Exec=python3 $HOME/.local/bin/ripdvd-gui.py|" \
    "$SRC_DIR/data/ripdvd.desktop" > "$HOME/.local/share/applications/ripdvd.desktop"

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "=== Vérification finale ==="
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')" && echo "✅ Interface OK" || echo "❌ GTK4/Adw manquant"
command -v HandBrakeCLI >/dev/null 2>&1 && echo "✅ HandBrakeCLI OK" || echo "⚠ HandBrakeCLI absent"
echo ""
echo "=== Installation terminée ==="
echo "Lancez 'ripdvd' depuis le menu, ou : python3 ~/.local/bin/ripdvd-gui.py"
