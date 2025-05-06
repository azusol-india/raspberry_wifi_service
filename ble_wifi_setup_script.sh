#!/bin/bash

set -e

echo "[1/5] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-dbus python3-gi bluetooth bluez network-manager

echo "[2/5] Enabling NetworkManager..."
sudo systemctl enable NetworkManager
sudo systemctl restart NetworkManager

echo "[3/5] Copying service file..."
sudo cp ble-server.service /etc/systemd/system/ble-server.service

echo "[4/5] Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable ble-server.service
sudo systemctl start ble-server.service

echo "[5/5] Setup complete! Device will advertise as 'ArrestoAICamera'"
echo "Run this to monitor: sudo journalctl -u ble-server.service -f"
