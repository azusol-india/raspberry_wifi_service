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

## 🚀 One-Line Installation (Recommended for Production)

From a fresh Raspberry Pi:

```bash
git clone https://github.com/arresto-ai/ble-wifi-setup.git
cd ble-wifi-setup
chmod +x install_ble_wifi.sh
./install_ble_wifi.sh
```

This will:
- Install all required dependencies
- Create a Python virtual environment
- Copy all files to the correct system locations
- Enable and launch the BLE WiFi provisioning server on boot

---

## 📁 Folder Structure (in this repo)

| File                        | Purpose                                      |
|-----------------------------|----------------------------------------------|
| `wifi_ble_server_corrected.py` | Python BLE GATT server                     |
| `start_ble_server.sh`      | Script to bring up BLE + start GATT server  |
| `ble-server.service`       | systemd unit to launch on boot              |
| `install_ble_wifi.sh`      | 🔧 One-click installer script                |
| `README.md`                | This documentation                          |

---

## 🧠 What This Setup Does

- Advertises the BLE name `ArrestoAICamera` (visible in nRF Connect, Flutter, etc.)
- Hosts a BLE GATT server with:
  - `SSID` (read/write): to show and update current WiFi network
  - `Password` (write-only): to securely input WiFi password
- Connects to the specified WiFi using `nmcli`
- Does **not** reboot after connect (but can be enabled in code)
- Keeps BLE advertising active permanently

---

## 🟢 Managing the Service

To check status:
```bash
sudo systemctl status ble-server.service
```

To view logs:
```bash
sudo journalctl -u ble-server.service -f
```

To restart the service manually:
```bash
sudo systemctl restart ble-server.service
```

---

## 🧪 Testing Setup

### 1. Use nRF Connect (or your Flutter App) to scan
- Ensure Pi is powered on
- Scan for device `ArrestoAICamera`
- Look for advertised services (UUID: `12345678-1234-5678-1234-56789abcdef0`)

### 2. Connect and test read/write

#### ✅ Read SSID:
- Read `12345678-1234-5678-1234-56789abcdef1`
- Shows currently connected SSID

#### ✍️ Write new credentials:
- Write new SSID → `12345678-1234-5678-1234-56789abcdef1`
- Write password → `12345678-1234-5678-1234-56789abcdef2`
- Server will:
  - Remove all saved WiFi profiles except ethernet
  - Attempt connection to the new WiFi network
  - Print connection status to logs

#### 🔍 Validate WiFi:
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
| Name not visible in scan         | Ensure HCI name broadcast is working (via `hcitool`) |
| Multiple BLE records             | Avoid launching multiple services or duplicate scripts |
| WiFi not connecting              | Check logs: `sudo journalctl -u ble-server.service -n 100` |
| BLE drops after writing          | Ensure you write SSID *and* password in correct order |

---

## 🔁 Cloning to More Raspberry Pis

On any new Raspberry Pi:
```bash
git clone https://github.com/arresto-ai/ble-wifi-setup.git
cd ble-wifi-setup
chmod +x install_ble_wifi.sh
./install_ble_wifi.sh
```
Done! 🎉

---

## 👋 Author

Built as part of the **Arresto AI Camera** project for easy wireless provisioning via BLE. Contributions welcome!
