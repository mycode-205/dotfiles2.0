#!/usr/bin/env python3

import subprocess
import os
from typing import List, Optional
from dataclasses import dataclass

from utils import notify

# Icons
wifi_icon = "󰖩"
wifi_known = "󰆓"
shut_lock = ""
open_lock = ""
connect_icon = ""
forget_icon = "󰩹"
back_icon = "󰁍"

CONFIG_DIR = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
NOTIFY_TITLE = f"{wifi_icon} WiFi Manager"


@dataclass
class WifiNetwork:
    ssid: str
    security: Optional[str]
    saved: bool


# --------------------------------------------------
# Basic Helpers
# --------------------------------------------------

def is_wifi_enabled():
    result = subprocess.run(
        ["nmcli", "-fields", "WIFI", "g"],
        capture_output=True,
        text=True,
    )
    return "enabled" in result.stdout


def get_saved_networks() -> List[str]:
    result = subprocess.run(
        ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
        capture_output=True,
        text=True,
    )

    saved = []
    for line in result.stdout.splitlines():
        if line.endswith("wireless"):
            saved.append(line.split(":")[0])
    return saved


def list_wifi_networks() -> List[WifiNetwork]:
    saved_networks = get_saved_networks()

    result = subprocess.run(
        ["nmcli", "-t", "-f", "SECURITY,SSID", "device", "wifi", "list"],
        capture_output=True,
        text=True,
    )

    networks = []

    for line in result.stdout.splitlines():
        parts = line.split(":", 1)
        if len(parts) != 2:
            continue

        security, ssid = parts
        if not ssid:
            continue

        networks.append(
            WifiNetwork(
                ssid=ssid,
                security=security,
                saved=ssid in saved_networks,
            )
        )

    return networks


# --------------------------------------------------
# Password Prompt
# --------------------------------------------------

def prompt_password(ssid: str):
    return subprocess.run(
        [
            "rofi",
            "-dmenu",
            "-password",
            "-p",
            f"{shut_lock} Password for {ssid}",
            "-theme",
            f"{CONFIG_DIR}/rofi/password.rasi",
        ],
        capture_output=True,
        text=True,
    ).stdout.strip()


# --------------------------------------------------
# Connect / Forget Logic
# --------------------------------------------------

def connect_network(ssid: str, saved: bool):
    if saved:
        result = subprocess.run(
            ["nmcli", "connection", "up", "id", ssid],
            capture_output=True,
            text=True,
        )
    else:
        password = prompt_password(ssid)
        if not password:
            return

        result = subprocess.run(
            ["nmcli", "device", "wifi", "connect", ssid, "password", password],
            capture_output=True,
            text=True,
        )

    if "successfully" in result.stdout.lower():
        notify(NOTIFY_TITLE, f"{ssid} connected ✅")
    else:
        notify(NOTIFY_TITLE, f"Failed to connect to {ssid} ❌")


def forget_network(ssid: str):
    subprocess.run(["nmcli", "connection", "delete", ssid])
    notify(NOTIFY_TITLE, f"{ssid} removed 🗑️")


# --------------------------------------------------
# Submenu
# --------------------------------------------------

def show_network_menu(network: WifiNetwork):
    options = [f"{connect_icon} Connect"]

    if network.saved:
        options.append(f"{forget_icon} Forget Network")

    options.append(f"{back_icon} Back")

    action = subprocess.run(
        [
            "rofi",
            "-dmenu",
            "-i",
            "-p",
            f"{wifi_icon} {network.ssid}",
            "-theme",
            f"{CONFIG_DIR}/rofi/wifi.rasi",
        ],
        input="\n".join(options),
        capture_output=True,
        text=True,
    ).stdout.strip()

    if action.startswith(connect_icon):
        connect_network(network.ssid, network.saved)

    elif action.startswith(forget_icon):
        forget_network(network.ssid)

    elif action.startswith(back_icon):
        wifi_manager()


# --------------------------------------------------
# Main Menu
# --------------------------------------------------

def wifi_manager():
    if not is_wifi_enabled():
        subprocess.run(["nmcli", "radio", "wifi", "on"])
        notify(NOTIFY_TITLE, "WiFi Enabled")
        return

    networks = list_wifi_networks()

    options = []
    mapping = {}

    for net in networks:
        if net.saved:
            icon = wifi_known
        elif net.security:
            icon = shut_lock
        else:
            icon = open_lock

        label = f"{icon} {net.ssid}"
        options.append(label)
        mapping[label] = net

    selection = subprocess.run(
        [
            "rofi",
            "-dmenu",
            "-i",
            "-p",
            f"{wifi_icon} WiFi",
            "-theme",
            f"{CONFIG_DIR}/rofi/wifi.rasi",
        ],
        input="\n".join(options),
        capture_output=True,
        text=True,
    ).stdout.strip()

    if not selection:
        return

    if selection in mapping:
        show_network_menu(mapping[selection])
    else:
        # Manual SSID
        connect_network(selection, saved=False)


# --------------------------------------------------

if __name__ == "__main__":
    wifi_manager()
