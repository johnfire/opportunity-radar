#!/usr/bin/env bash
# Installs the radar's systemd USER timers (no root needed). Usage: systemd/install_timers.sh [weekly|twice-monthly ...]
# Default installs only "weekly". Undo with systemd/uninstall_timers.sh.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
radar_dir="$(dirname "$here")"
target="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$target"
groups=("$@"); [ ${#groups[@]} -eq 0 ] && groups=(weekly)
for group in "${groups[@]}"; do
  for kind in service timer; do
    sed "s#@RADAR_DIR@#${radar_dir}#g" "$here/radar-${group}.${kind}.template" > "$target/radar-${group}.${kind}"
  done
done
systemctl --user daemon-reload
for group in "${groups[@]}"; do
  systemctl --user enable --now "radar-${group}.timer"
done
systemctl --user list-timers 'radar-*' --no-pager
