# Lumy Installation Guide v3.0

## Hardware Requirements
- **Raspberry Pi Zero 2 W**
- **Waveshare 7.3inch e-Paper HAT (E)** - [Product Page](https://www.waveshare.com/7.3inch-e-paper-hat-e.htm)
- MicroSD card (8GB minimum, 16GB recommended)
- Power supply (5V 2.5A recommended)

## Software Requirements
- **Raspberry Pi OS Lite (64-bit)** - Bookworm release

---

## Installation Steps

### 1. Prepare SD Card

1. Download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Flash **Raspberry Pi OS Lite (64-bit)**
3. **IMPORTANT:** In Imager settings (gear icon):
   - Enable SSH
   - Set username: `lumy` (or your choice)
   - Set WiFi credentials (your home network)
   - Set locale/timezone

### 2. Boot and Connect

1. Insert SD card into Pi
2. Power on
3. Wait 2-3 minutes for first boot
4. Find Pi's IP address:
   ```bash
   # On your computer
   ping lumy.local
   # Or check your router's DHCP list
   ```
5. SSH into Pi:
   ```bash
   ssh lumy@lumy.local
   # Or: ssh lumy@<IP_ADDRESS>
   ```

### 3. Install Lumy

```bash
# Clone repository
cd ~
git clone https://github.com/postysh/lumy.git
cd lumy

# Run installation script
sudo bash scripts/install.sh
```

The installer will:
- Install required system packages
- Install BCM2835 library
- Enable SPI interface
- Install Waveshare e-Paper library
- Install Lumy backend dependencies
- Test the display
- Create systemd service
- **Automatically reboot**

**Installation takes ~10-15 minutes** (Pi Zero 2 W is slow)

### 4. After Reboot

The display will automatically show:
```
Welcome to Lumy
Register at: lumy-beta.vercel.app
[REGISTRATION CODE]
Device: LUMY-XXXXXX
```

### 5. Register Device

1. Open browser to: **https://lumy-beta.vercel.app**
2. Sign up or log in
3. Click "Add Device"
4. Enter the **Registration Code** from the display
5. Device is now registered!

---

## Troubleshooting

### Display shows nothing
```bash
# Check service status
sudo systemctl status lumy

# View logs
sudo journalctl -u lumy -f

# Restart service
sudo systemctl restart lumy
```

### SPI not enabled
```bash
# Check if SPI is enabled
lsmod | grep spi

# Manually enable
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable

# Reboot
sudo reboot
```

### Check display test
```bash
cd /tmp
sudo python3 test_display.py
```

### Python library not found
```bash
# Check library installation
ls -la /usr/local/lib/python3.11/dist-packages/waveshare_epd/

# Reinstall if needed
cd /tmp/e-Paper/RaspberryPi_JetsonNano/python
sudo cp -r lib/waveshare_epd/* /usr/local/lib/python3.11/dist-packages/waveshare_epd/
```

---

## Service Management

```bash
# Start service
sudo systemctl start lumy

# Stop service
sudo systemctl stop lumy

# Restart service
sudo systemctl restart lumy

# Enable auto-start
sudo systemctl enable lumy

# Disable auto-start
sudo systemctl disable lumy

# View logs
sudo journalctl -u lumy -f
```

---

## Uninstall

```bash
# Stop and disable service
sudo systemctl stop lumy
sudo systemctl disable lumy
sudo rm /etc/systemd/system/lumy.service

# Remove Lumy files
rm -rf ~/lumy

# Remove libraries (optional)
sudo rm -rf /usr/local/lib/python3.11/dist-packages/waveshare_epd
```

---

## What's Next?

After successful installation, you can:
- View device status on the web dashboard
- (Coming soon) Configure widgets
- (Coming soon) WiFi AP mode for customer setup

---

## Support

- **Documentation**: https://github.com/postysh/lumy
- **Web Dashboard**: https://lumy-beta.vercel.app
- **Waveshare Manual**: https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual
