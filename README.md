# Arresto BLE WiFi Provisioning Setup for Raspberry Pi

This guide helps you configure a Raspberry Pi to act as a **BLE-configurable WiFi device**. It advertises itself as `ArrestoAICamera` and allows a mobile app (e.g. your Flutter app) to read current WiFi details and send new credentials securely over BLE.

---

## 📦 Requirements

- Raspberry Pi 3, 4, or 5 (with built-in Bluetooth)
- Raspberry Pi OS Lite or Full (Debian-based)
- Python 3.11+ installed
- NetworkManager enabled
- BlueZ 5.50+ (default in most recent Raspberry Pi OS)

---

## ⚙️ BLE GATT UUIDs Used

| Purpose              | UUID                                   | Access    |
|----------------------|----------------------------------------|-----------|
| BLE Service UUID     | `12345678-1234-5678-1234-56789abcdef0` | -         |
| SSID Characteristic  | `12345678-1234-5678-1234-56789abcdef1` | Read/Write|
| Password Characteristic | `12345678-1234-5678-1234-56789abcdef2` | Write Only|

---

## 🚀 Installation Steps (One-time per Pi)

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-dbus python3-gi bluetooth bluez network-manager
sudo systemctl enable NetworkManager
sudo systemctl restart NetworkManager
```

### 2. Create virtual environment

```bash
python3 -m venv ~/ble-env
source ~/ble-env/bin/activate
pip install pydbus
```

---

## 📁 File Structure (Install these manually or via script)

| File                        | Target Path                             |
|-----------------------------|------------------------------------------|
| `wifi_ble_server_corrected.py` | `/home/arresto/wifi_ble_server_corrected.py` |
| `start_ble_server.sh`      | `/home/arresto/start_ble_server.sh`     |
| `ble-server.service`       | `/etc/systemd/system/ble-server.service`|

Make `start_ble_server.sh` executable:

```bash
chmod +x /home/arresto/start_ble_server.sh
```

---

## 🧠 What This Setup Does

- Advertises the BLE name `ArrestoAICamera` (visible in nRF Connect, Flutter, etc.)
- Hosts a BLE GATT server with:
  - `SSID` (read/write): to show and update current WiFi network
  - `Password` (write-only): to securely input WiFi password
- Connects to the specified WiFi using `nmcli`
- Does **not** reboot after connect
- Keeps BLE active even after WiFi is changed

---

## 🟢 Enable Service on Boot

```bash
sudo systemctl daemon-reload
sudo systemctl enable ble-server.service
sudo systemctl start ble-server.service
```

To check status:
```bash
sudo systemctl status ble-server.service
```

To view logs:
```bash
sudo journalctl -u ble-server.service -f
```

---

## 🧪 Testing Setup

### 1. Use nRF Connect (or your Flutter App) to scan

- Ensure Pi is powered on
- Scan for device `ArrestoAICamera`
- Look for advertised services (UUID: `12345678-1234-5678-1234-56789abcdef0`)

### 2. Connect and test read/write

#### ✅ Read SSID:
- Connect to the Pi over BLE
- Read characteristic: `12345678-1234-5678-1234-56789abcdef1`
- Output will show current connected SSID

#### ✍️ Write new credentials:
- Write new SSID to characteristic: `12345678-1234-5678-1234-56789abcdef1`
- Write password to: `12345678-1234-5678-1234-56789abcdef2`
- BLE script will:
  - Delete old WiFi configs (only `wifi`, not `ethernet`)
  - Connect to new network
  - Log results in system journal

### ✅ Validate Connection:

```bash
nmcli -t -f active,ssid dev wifi | grep yes:
```

or

```bash
hostname -I
```

---

## 🛠 Troubleshooting

| Problem                          | Solution                                      |
|----------------------------------|-----------------------------------------------|
| Device name not visible over BLE | Ensure hcitool command ran in `start_ble_server.sh` |
| BLE connection drops             | Confirm you wrote both SSID and password      |
| WiFi doesn't connect             | Check logs: `sudo journalctl -u ble-server.service -n 100` |
| Service not starting             | Run `sudo systemctl status ble-server.service` |

---

## 🔁 Cloning Setup to Other Raspberry Pis

1. Copy all three files to the same locations
2. Run the install/setup steps (dependency install + venv)
3. Enable and start the service
4. Done!

---

## 👋 Author

Built as part of the **Arresto AI Camera** project for easy wireless provisioning via BLE.