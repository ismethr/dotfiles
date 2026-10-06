#!/usr/bin/env bash
set -euo pipefail
config_dir="$HOME/.config/noctalia"
mkdir -p "$config_dir"
exec 9>"$config_dir/.morandi.lock"
flock -n 9 || exit 0
wallpaper_path="$(noctalia msg wallpaper-get 2>/dev/null || true)"
if [[ -n "$wallpaper_path" && -f "$wallpaper_path" ]]; then
    temporary="$(mktemp "$config_dir/.colors.XXXXXX")"
    trap 'rm -f "$temporary"' EXIT
    noctalia theme "$wallpaper_path" --scheme muted --dark -o "$temporary"
    mv "$temporary" "$config_dir/colors.json"
fi
python3 "$config_dir/morandi-gen.py"
