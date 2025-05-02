#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
import dbus.service
import subprocess
import time
from gi.repository import GLib

BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_PATH = '/org/bluez/hci0'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
ADVERTISING_INTERFACE = 'org.bluez.LEAdvertisement1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHARACTERISTIC_IFACE = 'org.bluez.GattCharacteristic1'

# UUIDs
WIFICONFIG_SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
SSID_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1'
PASSWORD_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef2'

mainloop = None

def get_connected_ssid():
    try:
        ssid = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], encoding="utf-8")
        for line in ssid.splitlines():
            if line.startswith("yes:"):
                return line.split(":")[1]
        return "Not Connected"
    except Exception:
        return "Not Connected"

class BLEApplication(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for charac in service.characteristics:
                response[charac.get_path()] = charac.get_properties()
        return response

class BLEService(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array([c.get_path() for c in self.characteristics], signature='o')
            }
        }

class BLECharacteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.get_path() + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.value = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            GATT_CHARACTERISTIC_IFACE: {
                'UUID': self.uuid,
                'Service': self.service.get_path(),
                'Flags': dbus.Array(self.flags, signature='s')
            }
        }

    @dbus.service.method(GATT_CHARACTERISTIC_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        if self.uuid == SSID_CHARACTERISTIC_UUID:
            ssid = get_connected_ssid()
            print(f'Read current SSID: {ssid}')
            return dbus.ByteArray(ssid.encode())
        else:
            return self.value

    @dbus.service.method(GATT_CHARACTERISTIC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print(f'WriteValue on {self.uuid}: {bytes(value).decode()}')
        self.value = value

        if self.uuid == SSID_CHARACTERISTIC_UUID:
            with open("/tmp/ssid.txt", "wb") as f:
                f.write(bytearray(value))

        if self.uuid == PASSWORD_CHARACTERISTIC_UUID:
            with open("/tmp/password.txt", "wb") as f:
                f.write(bytearray(value))
            self.connect_to_wifi()

    def connect_to_wifi(self):
        try:
            with open('/tmp/ssid.txt', 'r') as f:
                ssid = f.read().strip()
            with open('/tmp/password.txt', 'r') as f:
                password = f.read().strip()

            print(f"Connecting to new SSID via nmcli: {ssid}")

            result = subprocess.run(['nmcli', '-f', 'NAME,TYPE', 'connection', 'show'], stdout=subprocess.PIPE, encoding='utf-8')
            for line in result.stdout.strip().split('\n'):
                if line.strip() == '' or line.startswith('NAME'):
                    continue
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                name, conn_type = ' '.join(parts[:-1]), parts[-1]
                if conn_type == 'wifi':
                    print(f"Deleting WiFi connection: {name}")
                    subprocess.run(['nmcli', 'connection', 'delete', name])

            subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], check=True)
            print(f"✅ Connected and saved to {ssid}")

            print("⏳ Waiting for WiFi to establish...")
            time.sleep(5)

            current_ssid = get_connected_ssid()
            if current_ssid == ssid:
                print(f"🔁 Successfully connected to {ssid}. (Reboot disabled)")
                # subprocess.run(['sudo', 'reboot'])
            else:
                print("❌ WiFi connection unsuccessful. No reboot.")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to connect to WiFi: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

class BLEAdvertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.local_name = 'ArrestoAICamera'
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            ADVERTISING_INTERFACE: {
                'Type': dbus.String(self.ad_type),
                'LocalName': dbus.String(self.local_name),
                'Includes': dbus.Array(['tx-power'], signature='s')
            }
        }

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        return self.get_properties()[interface]

    @dbus.service.method(ADVERTISING_INTERFACE, in_signature='', out_signature='')
    def Release(self):
        print('Advertisement released')


def main():
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter = bus.get_object(BLUEZ_SERVICE_NAME, ADAPTER_PATH)
    adapter_props = dbus.Interface(adapter, 'org.freedesktop.DBus.Properties')

    adapter_props.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))
    adapter_props.Set('org.bluez.Adapter1', 'Alias', dbus.String('ArrestoAICamera'))

    service_manager = dbus.Interface(adapter, GATT_MANAGER_IFACE)
    adv_manager = dbus.Interface(adapter, LE_ADVERTISING_MANAGER_IFACE)

    app = BLEApplication(bus)
    wifi_service = BLEService(bus, 0, WIFICONFIG_SERVICE_UUID, True)

    ssid_char = BLECharacteristic(bus, 0, SSID_CHARACTERISTIC_UUID, ['read', 'write'], wifi_service)
    password_char = BLECharacteristic(bus, 1, PASSWORD_CHARACTERISTIC_UUID, ['write'], wifi_service)

    wifi_service.add_characteristic(ssid_char)
    wifi_service.add_characteristic(password_char)
    app.add_service(wifi_service)

    service_manager.RegisterApplication(app.get_path(), {},
        reply_handler=lambda: print('GATT application registered'),
        error_handler=lambda error: print(f'Failed to register application: {error}'))

    adv = BLEAdvertisement(bus, 0, 'peripheral')

    adv_manager.RegisterAdvertisement(adv.get_path(), {},
        reply_handler=lambda: print('Advertisement registered'),
        error_handler=lambda error: print(f'Failed to register advertisement: {error}'))

    print('BLE advertising name "ArrestoAICamera"...')
    mainloop = GLib.MainLoop()
    mainloop.run()

if __name__ == '__main__':
    main()
