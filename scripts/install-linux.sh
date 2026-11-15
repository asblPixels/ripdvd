#!/usr/bin/env bash
# install-linux.sh — Universal one-line installer for ripdvd on Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/asblPixels/ripdvd/main/scripts/install-linux.sh | bash
set -e

echo "============================================"
echo "  RipDvD — Universal Linux Installer"
echo "  From disc to digital — effortlessly"
echo "============================================"
echo ""

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO="$ID"
else
    echo "Cannot detect distribution. /etc/os-release not found."
    exit 1
fi

echo "Detected distribution: $DISTRO"
echo ""

SRC_DIR="$(mktemp -d)"
trap 'rm -rf "$SRC_DIR"' EXIT

# Clone the appropriate branch
case "$DISTRO" in
    fedora)
        BRANCH="main"
        ;;
    arch|manjaro)
        BRANCH="arch"
        ;;
    ubuntu|linuxmint|pop)
        BRANCH="ubuntu"
        ;;
    debian)
        BRANCH="debian"
        ;;
    *)
        echo "Unsupported distribution: $DISTRO"
        echo "Supported: Fedora, Arch, Ubuntu, Debian (and derivatives)"
        echo "Trying Fedora installer as fallback..."
        BRANCH="main"
        ;;
esac

echo "Cloning branch: $BRANCH"
git clone -b "$BRANCH" --depth 1 https://github.com/asblPixels/ripdvd.git "$SRC_DIR/ripdvd" 2>&1 | tail -2
cd "$SRC_DIR/ripdvd"

echo ""
echo "Running installer for $DISTRO..."
echo ""

# Run the appropriate installer
case "$DISTRO" in
    fedora)
        bash scripts/install.sh
        ;;
    arch|manjaro)
        bash scripts/install-arch.sh
        ;;
    ubuntu|linuxmint|pop)
        bash scripts/install-ubuntu.sh
        ;;
    debian)
        bash scripts/install-debian.sh
        ;;
    *)
        bash scripts/install.sh
        ;;
esac

echo ""
echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo ""
echo "Launch RipDvD from your application menu, or run:"
echo "  python3 ~/.local/bin/ripdvd-gui.py"
echo ""
echo "For encrypted DVDs, make sure libdvdcss is installed."
echo "See: https://github.com/asblPixels/ripdvd#installation"
