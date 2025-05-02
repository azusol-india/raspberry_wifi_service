#!/bin/bash

# Step 1: Activate Python virtual environment
echo "[STEP 1] Activating Python virtual environment..."
source /home/arresto/ble-env/bin/activate

# Step 2: Start BLE Python GATT Server
echo "[STEP 2] Starting BLE Python GATT Server..."
sudo /home/arresto/ble-env/bin/python3 /home/arresto/wifi_ble_server_corrected.py
