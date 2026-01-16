# Lumy Troubleshooting Guide

Common issues and solutions for Lumy installation and operation.

## Installation Issues

### Error: `Unable to locate package libtiff5`

**Problem:** Newer Raspberry Pi OS versions use `libtiff6` instead of `libtiff5`.

**Solution:**
```bash
sudo apt-get install -y libtiff6
```

The updated install script handles this automatically.

---

### Error: `Waveshare library not found`

**Problem:** The Waveshare E-Paper library didn't install correctly.

**Solution 1 - Run standalone installer:**
```bash
cd ~/lumy
chmod +x scripts/install-epaper-lib.sh
./scripts/install-epaper-lib.sh
```

**Solution 2 - Manual installation:**
```bash
# Install dependencies
sudo apt-get install -y python3-pip python3-pil python3-numpy python3-spidev
sudo apt-get install -y libopenjp2-7 libtiff6

# Clone and install
cd /tmp
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo pip3 install .

# Verify
python3 -c "import waveshare_epd.epd7in3e; print('Success!')"
```

**Solution 3 - Check SPI is enabled:**
```bash
# Enable SPI
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable

# Or command line:
sudo raspi-config nonint do_spi 0

# Verify SPI is loaded
lsmod | grep spi
# Should show: spi_bcm2835

# Reboot
sudo reboot
```

---

### Error: `ModuleNotFoundError: No module named 'spidev'`

**Problem:** SPI development library is missing.

**Solution:**
```bash
sudo apt-get install -y python3-spidev
# Or
sudo pip3 install spidev
```

---

## Display Issues

### Display shows nothing / blank screen

**Check 1 - Hardware connections:**
- Verify E-Paper HAT is properly seated on GPIO pins
- Check ribbon cable is firmly connected to both HAT and display
- Blue side of ribbon cable should face up

**Check 2 - SPI enabled:**
```bash
lsmod | grep spi
# Should show: spi_bcm2835
```

**Check 3 - Run test:**
```bash
cd ~/lumy
python3 scripts/test-display.py
```

**Check 4 - Check permissions:**
```bash
ls -l /dev/spidev0.0
# Should show: crw-rw---- 1 root spi
sudo usermod -a -G spi $USER
# Logout and login again
```

---

### Display refresh is very slow

**This is normal!** E-Paper displays are slow by design:
- Full refresh: ~15-20 seconds
- Partial refresh: ~5 seconds (if supported)

The 7.3" display has high resolution (1872×1404) which takes longer.

---

### Display shows "ghost" images / afterimage

**Solution:**
- Run a full clear: `python3 -c "from waveshare_epd import epd7in3e; epd = epd7in3e.EPD(); epd.init(); epd.Clear(); epd.sleep()"`
- Perform multiple full refreshes
- Keep display at room temperature (15-35°C)
- Ensure `sleep_after_refresh: true` in config

---

### Display shows incorrect colors

**Problem:** 7.3" E-Paper (E) model supports 7 colors but color representation varies.

**Solution:**
- Use RGB values close to primary colors
- Avoid gradients and subtle color differences
- Test with `scripts/test-display.py` to see color palette

---

## Bluetooth Issues

### Bluetooth not discoverable

**Solution:**
```bash
# Check Bluetooth status
sudo systemctl status bluetooth

# Make discoverable
sudo bluetoothctl
power on
discoverable on
pairable on
agent on
exit

# Run setup script
cd ~/lumy
./scripts/setup-bluetooth.sh
```

---

### Can't connect from iPhone

**Check 1 - Bluetooth enabled on Pi:**
```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

**Check 2 - Check range:**
- Bluetooth LE range is ~10 meters
- Move closer to Pi

**Check 3 - Reset pairing:**
```bash
sudo bluetoothctl
remove [DEVICE_MAC]
```

---

## Service Issues

### Lumy service won't start

**Check logs:**
```bash
sudo systemctl status lumy
journalctl -u lumy -n 50 --no-pager
```

**Common causes:**

1. **Python virtual environment issue:**
```bash
cd ~/lumy/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart lumy
```

2. **Permission issues:**
```bash
sudo chown -R $USER:$USER ~/lumy
sudo usermod -a -G gpio,spi,i2c $USER
```

3. **Port already in use:**
```bash
sudo lsof -i :8000
# Kill the process if needed
sudo kill [PID]
```

---

### Web dashboard not accessible

**Check 1 - Service running:**
```bash
sudo systemctl status lumy
```

**Check 2 - Find Pi's IP:**
```bash
hostname -I
# Or
ip addr show | grep inet
```

**Check 3 - Firewall:**
```bash
sudo ufw status
# If active, allow port 8000
sudo ufw allow 8000
```

**Check 4 - Try localhost on Pi:**
```bash
curl http://localhost:8000
# Should return HTML/JSON
```

---

## Performance Issues

### High CPU usage

**Solution:**
```bash
# Increase refresh interval in config
nano ~/lumy/backend/config.yaml
# Set refresh_interval: 600  # 10 minutes

sudo systemctl restart lumy
```

---

### Out of memory

**Problem:** Raspberry Pi Zero 2 W has limited RAM (512MB).

**Solution:**
```bash
# Reduce widget count
nano ~/lumy/backend/config.yaml
# Keep only essential widgets

# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## Python Errors

### ImportError / ModuleNotFoundError

**Solution:**
```bash
cd ~/lumy/backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Permission denied on /dev/spidev0.0

**Solution:**
```bash
sudo usermod -a -G spi,gpio $USER
# Logout and login, or:
sudo reboot
```

---

## Network Issues

### Can't SSH to Pi

**Solution 1 - Enable SSH:**
```bash
# If you have physical access:
sudo raspi-config
# Interface Options → SSH → Enable

# Or create empty 'ssh' file in boot partition
```

**Solution 2 - Find Pi's IP:**
```bash
# On your Mac:
sudo nmap -sn 192.168.1.0/24 | grep -i raspberry

# Or check your router's DHCP table
```

**Solution 3 - Use USB serial connection:**
- Connect micro USB to Pi's USB port (not power port)
- Use `screen` or `minicom` on Mac

---

### Pi not connecting to WiFi

**Edit WiFi config (before first boot):**
```bash
# In boot partition, create: wpa_supplicant.conf
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_WIFI_NAME"
    psk="YOUR_WIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
```

---

## Getting More Help

### Collect debug information

```bash
# System info
uname -a
cat /etc/os-release

# Check SPI
lsmod | grep spi
ls -l /dev/spidev*

# Check Python modules
pip3 list | grep -i waveshare

# Lumy logs
journalctl -u lumy -n 100 --no-pager > ~/lumy-debug.log

# Test display
cd ~/lumy
python3 scripts/test-display.py 2>&1 | tee ~/display-test.log
```

### Useful commands

```bash
# Restart everything
sudo systemctl restart lumy
sudo systemctl restart bluetooth

# Reset display
python3 -c "from waveshare_epd import epd7in3e; epd = epd7in3e.EPD(); epd.init(); epd.Clear(); epd.sleep()"

# Check temperature (E-Paper is temperature sensitive)
vcgencmd measure_temp

# Monitor resources
htop

# Test API
curl http://localhost:8000/status
```

---

## Still Having Issues?

1. **Check documentation:**
   - [Installation Guide](INSTALLATION.md)
   - [Quick Start](QUICK_START.md)
   - [Waveshare Wiki](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual)

2. **GitHub Issues:**
   - Search existing issues
   - Create new issue with debug logs

3. **Community Help:**
   - Raspberry Pi Forums
   - Reddit: r/RASPBERRY_PI_PROJECTS

## Quick Reset

If all else fails, start fresh:

```bash
# Stop service
sudo systemctl stop lumy
sudo systemctl disable lumy

# Remove installation
rm -rf ~/lumy
sudo rm /etc/systemd/system/lumy.service

# Reinstall
cd ~ && git clone https://github.com/postysh/lumy.git
cd lumy && ./scripts/install.sh
```
