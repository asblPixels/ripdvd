#!/usr/bin/env bash
# ripdvd — "One button to rule them all" DVD ripper
# Détecte le DVD, sélectionne le titre le plus long, encode en MKV H.264 RF20 (résolution native).
# Dépendances : HandBrakeCLI (ou flatpak fr.handbrake.ghb), zenity, libdvdcss

set -u

# ---- Localisation de HandBrakeCLI ----
if command -v HandBrakeCLI >/dev/null 2>&1; then
    HB=(HandBrakeCLI)
elif [ -x /app/bin/HandBrakeCLI ]; then
    HB=(/app/bin/HandBrakeCLI)
elif flatpak run --command=HandBrakeCLI fr.handbrake.ghb --version >/dev/null 2>&1; then
    HB=(flatpak run --command=HandBrakeCLI fr.handbrake.ghb)
else
    zenity --error --title="ripdvd" --text="HandBrakeCLI introuvable.\nInstallez-le via :\n  sudo dnf install HandBrake HandBrake-cli\nou via Flatpak (fr.handbrake.ghb)."
    exit 1
fi

DVD_DEV="/dev/sr0"
OUT_DIR="${HOME}/Vidéos/Rips"
mkdir -p "$OUT_DIR"

# ---- Vérification du lecteur ----
if [ ! -b "$DVD_DEV" ]; then
    zenity --error --title="ripdvd" --text="Aucun lecteur DVD détecté ($DVD_DEV).\nInsérez un DVD puis réessayez."
    exit 1
fi

# ---- Scan des titres ----
zenity --info --title="ripdvd" --text="Analyse du DVD en cours..." --timeout=3 &
INFO_PID=$!

SCAN=$("${HB[@]}" -i "$DVD_DEV" --title 0 2>&1)
kill $INFO_PID 2>/dev/null

# Trouver le titre avec la plus grande durée (en ms)
BEST=$(echo "$SCAN" | awk '
    /scanning title/ { t=$NF }
    /duration is/ {
        ms=$5; gsub(/[^0-9]/,"",ms);
        if (ms+0 > bestms+0) { bestms=ms; bestt=t }
    }
    END { if (bestt=="") bestt=1; print bestt, bestms }
')
TITLE=$(echo "$BEST" | awk '{print $1}')
DUR_MS=$(echo "$BEST" | awk '{print $2}')
DUR_MIN=$(( DUR_MS / 60000 ))

if [ -z "$TITLE" ]; then
    zenity --error --title="ripdvd" --text="Impossible d'analyser le DVD.\nVérifiez libdvdcss (DVD chiffré)."
    exit 1
fi

# ---- Nom de sortie ----
DEFAULT_NAME="DVD_$(date +%Y%m%d_%H%M%S)"
NAME=$(zenity --entry --title="ripdvd" \
    --text="Titre principal détecté : titre $TITLE (${DUR_MIN} min)\nNom du fichier de sortie :" \
    --entry-text="$DEFAULT_NAME")
[ -z "$NAME" ] && exit 0

# Nettoyage du nom (espaces -> underscores, suppression caractères dangereux)
SAFE_NAME=$(echo "$NAME" | tr ' ' '_' | tr -cd 'A-Za-z0-9_.-')
[ -z "$SAFE_NAME" ] && SAFE_NAME="$DEFAULT_NAME"
OUTFILE="$OUT_DIR/${SAFE_NAME}.mkv"

if [ -e "$OUTFILE" ]; then
    zenity --question --title="ripdvd" --text="Le fichier existe déjà :\n$OUTFILE\nÉcraser ?" || exit 0
fi

# ---- Encodage avec barre de progression ----
(
    "${HB[@]}" -i "$DVD_DEV" -t "$TITLE" -o "$OUTFILE" \
        --preset "Fast 480p30" \
        --encoder x264 --quality 20 --encoder-preset medium \
        --aencoder copy --audio 1 \
        --subtitle 1,2,3,4,5,6,7,8,9,10 \
        --chapters \
        2>&1 | stdbuf -oL grep --line-buffered "Encoding:" | \
        while IFS= read -r line; do
            pct=$(echo "$line" | sed -n 's/.*,\s*\([0-9.]*\) %.*/\1/p')
            [ -n "$pct" ] && echo "$pct"
        done
) | zenity --progress --title="ripdvd — encodage" \
    --text="Encodage du titre $TITLE (${DUR_MIN} min) → $OUTFILE" \
    --percentage=0 --auto-close

RC=${PIPESTATUS[0]}
if [ "$RC" -ne 0 ]; then
    zenity --error --title="ripdvd" --text="Échec de l'encodage (code $RC).\nConsultez les logs HandBrake."
    exit 1
fi

# Vérification que le fichier a bien été créé
if [ -s "$OUTFILE" ]; then
    SIZE=$(du -h "$OUTFILE" | cut -f1)
    zenity --info --title="ripdvd" --text="Terminé ✅\n\nFichier : $OUTFILE\nTaille : $SIZE\n\nPrêt pour Jellyfin/Kodi."
else
    zenity --error --title="ripdvd" --text="Le fichier de sortie est vide ou absent."
    exit 1
fi
