# Raspberry Pi Setup Guide

This guide will help you set up your Raspberry Pi Zero 2 W with the Waveshare 7.3inch e-Paper HAT (E) for Lumy.

## Prerequisites

- Raspberry Pi Zero 2 W
- Waveshare 7.3inch e-Paper HAT (E) - 800x480
- MicroSD card (8GB or larger) with Raspberry Pi OS Lite 64-bit
- WiFi configured and working

## Hardware Setup

1. **Connect the e-Paper HAT to your Raspberry Pi:**
   - Align the 40-pin header on the HAT with the GPIO pins on the Pi
   - Press down gently but firmly to ensure a solid connection
   - The display should sit directly on top of the Pi

2. **Power on the Raspberry Pi:**
   - Connect the power supply
   - Wait for the system to boot (LED will blink)

## Software Installation

### Method 1: Automated Setup (Recommended)

1. **SSH into your Raspberry Pi:**
   ```bash
   ssh pi@raspberrypi.local
   # Default password: raspberry (change this!)
   ```

2. **Clone the Lumy repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/lumy.git lumy-repo
   cd lumy-repo
   ```

3. **Run the installation script:**
   ```bash
   sudo bash scripts/install.sh
   ```

4. **Reboot when prompted:**
   ```bash
   sudo reboot
   ```

5. **After reboot, start the Lumy service:**
   ```bash
   sudo systemctl start lumy
   ```

6. **Check if it's running:**
   ```bash
   sudo systemctl status lumy
   ```

### Method 2: Manual Setup

If you prefer to set things up manually:

1. **Enable SPI:**
   ```bash
   sudo raspi-config nonint do_spi 0
   ```

2. **Install dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-pil python3-numpy python3-rpi.gpio python3-spidev git
   ```

3. **Create application directory:**
   ```bash
   mkdir -p /home/pi/lumy/lib
   cd /home/pi/lumy
   ```

4. **Download Waveshare library:**
   ```bash
   BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd"
   mkdir -p lib/waveshare_epd
   wget -O lib/waveshare_epd/__init__.py "$BASE_URL/__init__.py"
   wget -O lib/waveshare_epd/epd7in3e.py "$BASE_URL/epd7in3e.py"
   wget -O lib/waveshare_epd/epdconfig.py "$BASE_URL/epdconfig.py"
   ```

5. **Copy the Python files:**
   ```bash
   cp ~/lumy-repo/backend/*.py /home/pi/lumy/
   ```

6. **Test the display:**
   ```bash
   cd /home/pi/lumy
   python3 main.py
   ```

## Testing

To test if the display is working:

```bash
cd /home/pi/lumy
python3 ../lumy-repo/scripts/test-display.py
```

You should see a test pattern with "Lumy Test Display" text.

## Service Management

The Lumy application runs as a systemd service:

```bash
# Start the service
sudo systemctl start lumy

# Stop the service
sudo systemctl stop lumy

# Restart the service
sudo systemctl restart lumy

# Check status
sudo systemctl status lumy

# View logs
sudo journalctl -u lumy -f

# Enable auto-start on boot (already done by install script)
sudo systemctl enable lumy

# Disable auto-start
sudo systemctl disable lumy
```

## Troubleshooting

### Display not updating

1. **Check SPI is enabled:**
   ```bash
   ls /dev/spi*
   # Should show: /dev/spidev0.0  /dev/spidev0.1
   ```

2. **Check GPIO permissions:**
   ```bash
   ls -l /dev/gpiomem
   # Should be accessible by 'gpio' group
   ```

3. **Check the service logs:**
   ```bash
   sudo journalctl -u lumy -n 50
   ```

### Import errors

If you get "No module named 'waveshare_epd'":

```bash
cd /home/pi/lumy
ls -la lib/waveshare_epd/
# Should show: __init__.py, epd7in3e.py, epdconfig.py
```

### Permission denied errors

```bash
sudo usermod -a -G spi,gpio pi
sudo reboot
```

## Hardware Connections

The Waveshare e-Paper HAT uses the following GPIO pins:

- **VCC** - 3.3V power
- **GND** - Ground
- **DIN** - GPIO 10 (SPI0 MOSI)
- **CLK** - GPIO 11 (SPI0 SCLK)
- **CS** - GPIO 8 (SPI0 CE0)
- **DC** - GPIO 25
- **RST** - GPIO 17
- **BUSY** - GPIO 24

These are automatically configured by the Waveshare library.

## Next Steps

Once your display is working:

1. Configure API endpoint in the backend to register the device
2. Implement WiFi provisioning (if needed)
3. Add widget support for displaying custom content

## Support

For issues, check:
- [Waveshare Wiki](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E))
- [Lumy Documentation](../README.md)
- [GitHub Issues](https://github.com/YOUR_USERNAME/lumy/issues)
