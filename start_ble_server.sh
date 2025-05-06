#!/bin/bash

# Step 1: Activate Python virtual environment
echo "[STEP 1] Activating Python virtual environment..."
source $HOME/ble-env/bin/activate

# Step 2: Start BLE Python GATT Server
echo "[STEP 2] Starting BLE Python GATT Server..."
sudo $HOME/ble-env/bin/python3 $HOME/wifi_ble_server_corrected.py
