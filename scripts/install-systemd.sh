#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer as root." >&2
    exit 1
fi

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
INSTALL_DIR="/opt/family-chalkboard"

install -d -m 0755 "$INSTALL_DIR"
install -m 0755 \
    "$PROJECT_DIR/src/chalkboard_server.py" \
    "$INSTALL_DIR/chalkboard_server.py"
install -m 0644 \
    "$PROJECT_DIR/src/index.html" \
    "$INSTALL_DIR/index.html"
install -m 0644 \
    "$PROJECT_DIR/systemd/family-chalkboard.service" \
    /etc/systemd/system/family-chalkboard.service

systemctl daemon-reload
systemctl enable --now family-chalkboard.service

echo "Family Chalkboard is running on port 8765."
