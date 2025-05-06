#!/bin/bash

set -e

echo "[1/4] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-dbus python3-gi bluetooth bluez network-manager

echo "[2/4] Enabling NetworkManager..."
sudo systemctl enable NetworkManager
sudo systemctl restart NetworkManager

echo "[3/4] Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable ble-server.service
sudo systemctl start ble-server.service

echo "[4/4] Setup complete! Device will advertise as 'ArrestoAICamera'"
echo "Run this to monitor: sudo journalctl -u ble-server.service -f"
