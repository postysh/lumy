# Lumy Setup Guide

## Hardware
- Raspberry Pi Zero 2 W
- Waveshare 7.3inch e-Paper HAT (E)
- MicroSD card (16GB+ recommended)

## Installation

### 1. Flash SD Card
1. Download Raspberry Pi Imager
2. Flash **Raspberry Pi OS Lite (64-bit)**
3. In settings (gear icon):
   - Enable SSH
   - Set username: `lumy`
   - Set password
   - Configure WiFi (your home network)

### 2. Boot and Install
```bash
# SSH into Pi
ssh lumy@lumy.local

# Clone repository
git clone https://github.com/postysh/lumy.git
cd lumy

# Run installer
sudo bash scripts/install.sh
```

Installation takes ~10 minutes, then auto-reboots.

### 3. Customer Setup
After reboot, the device is ready for a customer:

1. **Display shows:** "Connect to WiFi: Lumy-Setup"
2. **Customer connects** to `Lumy-Setup` WiFi network (open, no password)
3. **Browser opens** automatically (captive portal) or go to `192.168.4.1`
4. **Select WiFi** network and enter password
5. **Device reboots** and connects to home WiFi
6. **Display shows** registration code
7. **Customer registers** at `lumy-beta.vercel.app`

## What This Installs

- **Minimal packages:** Python, PIL, NumPy, GPIO, SPI
- **Waveshare library:** Only 3 files for 7.3" display (~30 KB)
- **WiFi AP mode:** hostapd + dnsmasq
- **Web server:** Simple WiFi configuration page
- **Display service:** Shows connection instructions

## Troubleshooting

```bash
# Check services
sudo systemctl status lumy
sudo systemctl status lumy-wifi-setup
sudo systemctl status hostapd
sudo systemctl status dnsmasq

# View logs
sudo journalctl -u lumy -f
sudo journalctl -u lumy-wifi-setup -f

# Restart services
sudo systemctl restart lumy
sudo systemctl restart lumy-wifi-setup
```

## Files

- `scripts/install.sh` - Installation script
- `backend/main.py` - Display service
- `backend/wifi_setup.py` - WiFi configuration server

## Notes

- **No password on AP** - Simple for customers, secure after WiFi configured
- **Minimal storage** - Only downloads what's needed
- **Auto-configures** - Customer just needs to enter WiFi password
- **Works on all devices** - iPhone, Android, laptop, tablet
