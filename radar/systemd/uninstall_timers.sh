#!/usr/bin/env bash
# Removes the radar's systemd user timers and service files.
set -euo pipefail
target="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
for group in weekly twice-monthly; do
  systemctl --user disable --now "radar-${group}.timer" 2>/dev/null || true
  rm -f "$target/radar-${group}.timer" "$target/radar-${group}.service"
done
systemctl --user daemon-reload
echo "radar timers removed"
