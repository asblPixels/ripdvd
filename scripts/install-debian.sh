#!/usr/bin/env bash
# install-ripdvd-debian.sh — installe ripdvd-gui sur Debian
set -e

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Mise à jour des paquets ==="
sudo apt update

echo "=== Installation des dépendances (apt) ==="
sudo apt install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \
    handbrake-cli zenity

echo "=== Vérification PyGObject ==="
python3 -c "import gi; print('PyGObject OK')" || { echo "❌ PyGObject manquant"; exit 1; }

echo "=== Installation libdvdcss ==="
if ! dpkg -l | grep -q libdvdcss; then
    sudo apt install -y libdvd-pkg 2>/dev/null || sudo apt install -y libdvdcss2 2>/dev/null || true
    echo "Si libdvdcss n'est pas disponible, compilez-le depuis :"
    echo "   https://www.videolan.org/developers/libdvdcss.html"
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
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')" && echo "Interface OK" || echo "GTK4/Adw manquant"
command -v HandBrakeCLI >/dev/null 2>&1 && echo "HandBrakeCLI OK" || echo "HandBrakeCLI absent"
echo ""
echo "=== Installation terminée ==="
echo "Lancez 'ripdvd' depuis le menu, ou : python3 ~/.local/bin/ripdvd-gui.py"
