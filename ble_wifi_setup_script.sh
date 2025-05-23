#!/bin/bash

set -e

echo "[1/6] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-dbus python3-gi bluetooth bluez network-manager

echo "[2/6] Enabling NetworkManager..."
sudo systemctl enable NetworkManager
sudo systemctl restart NetworkManager

echo "[3/6] Copying service file..."
sudo cp ble-server.service /etc/systemd/system/ble-server.service

echo "[4/6] Making start script executable..."
chmod +x $HOME/raspberry_wifi_service/start_ble_server.sh

echo "[5/6] Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable ble-server.service
sudo systemctl start ble-server.service

echo "[6/6] Setup complete! Device will advertise as 'ArrestoAICamera'"
echo "Run this to monitor: sudo journalctl -u ble-server.service -f"
