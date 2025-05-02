#!/bin/bash

set -e

echo "[1/7] Updating system packages..."
sudo apt update && sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-dbus \
  python3-gi \
  bluetooth \
  bluez \
  network-manager 

sudo systemctl enable NetworkManager
sudo systemctl restart NetworkManager

echo "[2/7] Creating virtual environment..."
python3 -m venv /home/arresto/ble-env
source /home/arresto/ble-env/bin/activate
pip install pydbus

echo "[3/7] Deploying Python BLE server script..."
cat << 'EOF' > /home/arresto/wifi_ble_server_corrected.py
[Final Python code inserted here. Due to character limits, this response will be split. Please proceed to the next message to see the continuation.]
EOF

echo "[4/7] Creating BLE start script..."
cat << 'EOF' > /home/arresto/start_ble_server.sh
#!/bin/bash

sudo hciconfig hci0 up
sudo hcitool -i hci0 cmd 0x08 0x000a 00
sudo hcitool -i hci0 cmd 0x08 0x0008 17 02 01 06 11 09 41 72 72 65 73 74 6F 41 49 43 61 6D 65 72 61
sudo hcitool -i hci0 cmd 0x08 0x000a 01
sleep 2
source /home/arresto/ble-env/bin/activate
sudo /home/arresto/ble-env/bin/python3 /home/arresto/wifi_ble_server_corrected.py
EOF

chmod +x /home/arresto/start_ble_server.sh

echo "[5/7] Creating systemd service..."
cat << 'EOF' | sudo tee /etc/systemd/system/ble-server.service > /dev/null
[Unit]
Description=Start BLE Advertising and GATT Server (ArrestoAICamera)
After=multi-user.target bluetooth.target
Wants=bluetooth.target

[Service]
Type=simple
ExecStart=/home/arresto/start_ble_server.sh
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "[6/7] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ble-server.service
sudo systemctl start ble-server.service

echo "[7/7] Setup Complete!"
echo "You can monitor logs with: sudo journalctl -u ble-server.service -f"
