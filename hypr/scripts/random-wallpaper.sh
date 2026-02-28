#!/bin/bash

WALL_DIR="$HOME/Pictures/wallpapers"
CONFIG="$HOME/.config/hypr/hyprpaper.conf"

sleep 2

RANDOM_WALL=$(find "$WALL_DIR" -type f | shuf -n 1)
[ -z "$RANDOM_WALL" ] && exit 0

echo "preload = $RANDOM_WALL" > "$CONFIG"
echo "wallpaper = ,$RANDOM_WALL" >> "$CONFIG"

hyprctl hyprpaper preload "$RANDOM_WALL"
hyprctl hyprpaper wallpaper ",$RANDOM_WALL"
