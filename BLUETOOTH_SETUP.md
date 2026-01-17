# Lumy Bluetooth Setup

## Overview
Lumy uses Bluetooth LE for initial WiFi configuration. No complex AP mode, no WiFi conflicts - just simple Bluetooth pairing.

---

## Hardware
- Raspberry Pi Zero 2 W (has Bluetooth 5.0)
- Waveshare 7.3inch e-Paper HAT (E)
- MicroSD card (16GB+)
- Mac for setup (macOS app included)

---

## Installation

### 1. Prepare SD Card
1. Flash **Raspberry Pi OS Lite 64-bit**
2. **DO NOT configure WiFi** in Imager
3. Only set: username (`lumy`), password, enable SSH
4. Insert SD, boot Pi

### 2. Initial Setup (via Ethernet or USB)
Since there's no WiFi yet, you need wired access:

**Option A: Ethernet (if you have USB-Ethernet adapter)**
```bash
ssh lumy@lumy.local
```

**Option B: USB Direct Connect**
- Add `dtoverlay=dwc2` to `/boot/config.txt`
- Add `modules-load=dwc2,g_ether` to `/boot/cmdline.txt`
- Connect via USB data port
- SSH to `lumy@raspberrypi.local`

### 3. Run Installer
```bash
cd ~
git clone https://github.com/postysh/lumy.git
cd lumy
sudo bash scripts/install.sh
```

Installation takes ~10 minutes, then auto-reboots.

---

## Using the macOS App

### 1. Open Xcode Project
```bash
open "/Users/evan/Desktop/lumy/Lumy Desktop/Lumy Desktop.xcodeproj"
```

### 2. Add BluetoothManager.swift
- In Xcode, right-click on "Lumy Desktop" folder
- Add Files to "Lumy Desktop"
- Select `BluetoothManager.swift`

### 3. Run the App
- Press ⌘R or click Run
- App will open on your Mac

### 4. Setup Flow
1. **Scan** for devices (click "Scan" button)
2. **Select** your Lumy device (shows as "Lumy-Setup")
3. **Enter** WiFi SSID and password
4. **Send** credentials
5. Device reboots and connects to WiFi
6. Display shows registration code

---

## What Happens

### Before WiFi Configuration:
- Pi boots without WiFi
- BLE server starts (`lumy-ble` service)
- Advertises as "Lumy-Setup"
- Waits for macOS app to connect

### After WiFi Configuration:
- Receives credentials via Bluetooth
- Writes `wpa_supplicant.conf`
- Reboots
- Connects to WiFi
- BLE server stops
- Display service starts
- Shows registration code

---

## Troubleshooting

### Pi Not Showing Up in Scan
```bash
# Check Bluetooth
sudo systemctl status bluetooth
sudo hciconfig hci0 piscan

# Check BLE service
sudo systemctl status lumy-ble
sudo journalctl -u lumy-ble -f
```

### Can't Connect to Device
```bash
# Restart Bluetooth
sudo systemctl restart bluetooth
sudo systemctl restart lumy-ble
```

### WiFi Not Connecting After Setup
```bash
# Check wpa_supplicant.conf
cat /etc/wpa_supplicant/wpa_supplicant.conf

# Check WiFi status
iwconfig wlan0
```

### Display Not Showing
```bash
# Check display service
sudo systemctl status lumy-display
sudo journalctl -u lumy-display -f

# Run manually
cd ~/lumy/backend
sudo python3 main.py
```

---

## Technical Details

### BLE UUIDs
- Service: `12345678-1234-5678-1234-56789abcdef0`
- WiFi Credential Char: `12345678-1234-5678-1234-56789abcdef1` (Write)
- Status Char: `12345678-1234-5678-1234-56789abcdef2` (Read, Notify)

### Credential Format
JSON over BLE:
```json
{
  "ssid": "YourWiFiNetwork",
  "password": "YourPassword"
}
```

### Services
- `lumy-ble.service` - BLE server (runs until WiFi configured)
- `lumy-display.service` - Display service (runs after WiFi connected)

---

## Files

- `Lumy Desktop/` - macOS SwiftUI app
  - `BluetoothManager.swift` - CoreBluetooth manager
  - `ContentView.swift` - UI
- `backend/`
  - `ble_server.py` - Python BLE server
  - `main.py` - Display service
- `scripts/install.sh` - Installation script

---

## Advantages Over WiFi AP

✅ **Simple** - No complex networking config  
✅ **Reliable** - Bluetooth is more stable than Pi Zero WiFi AP  
✅ **Cross-platform** - Works on Mac, iPhone, iPad  
✅ **No Conflicts** - Doesn't interfere with WiFi  
✅ **Secure** - BLE encryption built-in  
✅ **Good Range** - 10-30 meters

---

## Next Steps

After WiFi is configured:
1. Display shows registration code
2. Customer goes to `lumy-beta.vercel.app`
3. Enters registration code
4. Device is registered and ready to use
