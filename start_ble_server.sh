#!/bin/bash

# Step 1: Start BLE Python GATT Server
echo "[STEP 1] Starting BLE Python GATT Server..."
sudo python3 $HOME/raspberry_wifi_service/ble_server_corrected.py
