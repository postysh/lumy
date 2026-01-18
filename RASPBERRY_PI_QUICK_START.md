# Raspberry Pi Quick Start Guide

## What We're Building

A simple Lumy display that shows:
- "Welcome to Lumy" 
- A 6-character registration code
- Instructions to go to lumy.io/setup

**No WiFi AP, no Bluetooth - just a clean display setup.**

---

## Step 1: Prepare Your Raspberry Pi

1. **Flash Raspberry Pi OS Lite (64-bit)** to your SD card
2. **Configure WiFi** during first boot (or use `raspi-config`)
3. **Enable SSH** (in boot config or `raspi-config`)
4. **Connect the e-Paper HAT** to the 40-pin GPIO header

---

## Step 2: SSH Into Your Pi

```bash
ssh pi@raspberrypi.local
# Password: raspberry (or whatever you set)
```

---

## Step 3: Clone and Run Install Script

On your **Raspberry Pi**, run:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/lumy.git lumy-repo
cd lumy-repo

# Run installation script
sudo bash scripts/install.sh
```

The script will:
- ✅ Update system packages
- ✅ Install Python dependencies
- ✅ Enable SPI interface
- ✅ Download Waveshare e-paper library (~30KB, not the full repo)
- ✅ Set up systemd service for auto-start
- ✅ Configure everything to run as the `pi` user

When it asks to reboot, say **yes**.

---

## Step 4: Start the Display

After reboot, SSH back in and start the service:

```bash
sudo systemctl start lumy
```

Check if it's running:

```bash
sudo systemctl status lumy
```

View logs:

```bash
sudo journalctl -u lumy -f
```

---

## What You Should See

The e-paper display should show:
- **"Welcome to Lumy"** (large text at top)
- **"Your Smart Display"** (subtitle)
- **"XXXXXX"** (random 6-character code in a box)
- **"Go to lumy.io/setup and enter this code"** (instructions at bottom)

---

## Useful Commands

```bash
# Start the service
sudo systemctl start lumy

# Stop the service
sudo systemctl stop lumy

# Restart the service
sudo systemctl restart lumy

# Check status
sudo systemctl status lumy

# View logs (live)
sudo journalctl -u lumy -f

# View last 50 log lines
sudo journalctl -u lumy -n 50

# Test display manually
cd /home/pi/lumy
python3 main.py
```

---

## File Locations

- **Application:** `/home/pi/lumy/`
- **Main script:** `/home/pi/lumy/main.py`
- **Display manager:** `/home/pi/lumy/display_manager.py`
- **Waveshare library:** `/home/pi/lumy/lib/waveshare_epd/`
- **Service file:** `/etc/systemd/system/lumy.service`

---

## Troubleshooting

### Display not updating?

1. **Check SPI is enabled:**
   ```bash
   ls /dev/spi*
   # Should show: /dev/spidev0.0  /dev/spidev0.1
   ```

2. **Check service logs:**
   ```bash
   sudo journalctl -u lumy -n 50
   ```

3. **Try manual test:**
   ```bash
   cd /home/pi/lumy-repo/scripts
   python3 test-display.py
   ```

### "No module named 'waveshare_epd'" error?

```bash
cd /home/pi/lumy
ls -la lib/waveshare_epd/
# Should show: __init__.py, epd7in3e.py, epdconfig.py
```

If files are missing, re-run the install script.

### Permission errors?

```bash
sudo usermod -a -G spi,gpio pi
sudo reboot
```

---

## Next Steps

Once the display is working:

1. **Connect to API** - Modify `main.py` to fetch registration code from your Vercel API
2. **Add WiFi Provisioning** - Implement captive portal or BLE setup (later)
3. **Widget System** - Add support for displaying custom widgets

---

## Need Help?

See the full setup guide: [docs/PI_SETUP.md](docs/PI_SETUP.md)
