#!/bin/bash

WALL_DIR="$HOME/Pictures/wallpapers"
CACHE_DIR="$HOME/.cache/wall-thumbs"
CONFIG="$HOME/.config/hypr/hyprpaper.conf"
ROFI_THEME="$HOME/.config/rofi/wallpaper.rasi"

mkdir -p "$CACHE_DIR"

for img in "$WALL_DIR"/*; do
    [ -f "$img" ] || continue
    filename=$(basename "$img")
    thumb="$CACHE_DIR/$filename"

    if [ ! -f "$thumb" ]; then
        magick "$img" -resize 500x300^ -gravity center -extent 500x300 "$thumb"
    fi
done

selected=$(
for img in "$WALL_DIR"/*; do
    [ -f "$img" ] || continue
    filename=$(basename "$img")
    echo -en "$filename\x00icon\x1f$CACHE_DIR/$filename\n"
done | rofi -dmenu -p "" -theme "$ROFI_THEME"
)

[ -z "$selected" ] && exit 0

FULL_PATH="$WALL_DIR/$selected"

echo "preload = $FULL_PATH" > "$CONFIG"
echo "wallpaper = ,$FULL_PATH" >> "$CONFIG"

hyprctl hyprpaper preload "$FULL_PATH"
hyprctl hyprpaper wallpaper ",$FULL_PATH"

notify-send "Wallpaper changed to $selected"
