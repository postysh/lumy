# Lumy Installation Guide

This guide will help you set up Lumy on your Raspberry Pi Zero 2 W with the Waveshare 7.3" E-Paper HAT (E).

## Hardware Setup

### Requirements
- Raspberry Pi Zero 2 W
- Waveshare 7.3" E-Paper HAT (E) - Model: epd7in3e
- MicroSD card (16GB+ recommended)
- Power supply (5V/2.5A minimum)
- iPhone for Bluetooth control

### Assembly

1. **Connect the E-Paper HAT to your Raspberry Pi:**
   - Carefully align the 40-pin header
   - Press down firmly to ensure good connection
   - The display should sit flush on top of the Pi

2. **Insert the ribbon cable:**
   - Connect the FPC cable to the E-Paper HAT
   - Ensure the blue side faces up
   - Lock the connector

## Software Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
cd ~
git clone https://github.com/yourusername/lumy.git
cd lumy

# Run installation script
chmod +x scripts/install.sh
./scripts/install.sh
```

This script will:
- Update system packages
- Install Python dependencies
- Install Waveshare E-Paper library
- Enable SPI interface
- Setup Bluetooth
- Create systemd service
- Install Node.js and web dashboard

### Option 2: Manual Installation

#### 1. System Update

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2. Enable SPI Interface

The E-Paper display requires SPI to be enabled:

```bash
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
```

Or use the command:

```bash
sudo raspi-config nonint do_spi 0
```

#### 3. Install System Dependencies

```bash
# Python and image libraries
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y python3-pil python3-numpy
sudo apt-get install -y libopenjp2-7 libtiff5

# Bluetooth
sudo apt-get install -y bluetooth bluez libbluetooth-dev
sudo apt-get install -y libglib2.0-dev
```

#### 4. Install Waveshare E-Paper Library

```bash
cd /tmp
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install
```

#### 5. Setup Python Backend

```bash
cd ~/lumy/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 6. Setup Bluetooth

```bash
chmod +x ~/lumy/scripts/setup-bluetooth.sh
~/lumy/scripts/setup-bluetooth.sh
```

#### 7. Install Node.js (for web dashboard)

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 8. Setup Web Dashboard

```bash
cd ~/lumy/web
npm install
```

## Configuration

### 1. Edit Configuration File

```bash
nano ~/lumy/backend/config.yaml
```

Key settings to configure:

```yaml
display:
  width: 1872
  height: 1404
  refresh_interval: 300  # Seconds between updates

bluetooth:
  enabled: true
  device_name: "Lumy Display"

widgets:
  weather:
    api_key: "YOUR_API_KEY_HERE"  # Get from OpenWeatherMap
    location: "Your City"
```

### 2. Test Your Display

Run the test script to verify everything is working:

```bash
cd ~/lumy
python3 scripts/test-display.py
```

You should see a test pattern on your display with:
- Title text
- Resolution information
- Color test boxes
- Current timestamp

## Running Lumy

### Manual Start

```bash
# Start backend
cd ~/lumy/backend
source venv/bin/activate
python3 main.py

# In another terminal, start web dashboard
cd ~/lumy/web
npm run dev
```

### Auto-Start on Boot (Systemd Service)

Create a systemd service to start Lumy automatically:

```bash
sudo systemctl enable lumy
sudo systemctl start lumy
```

Check status:

```bash
sudo systemctl status lumy
```

View logs:

```bash
journalctl -u lumy -f
```

## Connecting from iPhone

### Using Bluetooth

1. **Enable Bluetooth on Raspberry Pi:**
   ```bash
   sudo systemctl start bluetooth
   ```

2. **Make device discoverable:**
   - The device will appear as "Lumy Display"

3. **On your iPhone:**
   - Open Settings > Bluetooth
   - Look for "Lumy Display"
   - Pair with the device

4. **Use a Bluetooth app or build custom iOS app** to send commands

### Using Web Dashboard

1. **Find your Pi's IP address:**
   ```bash
   hostname -I
   ```

2. **Access from iPhone Safari:**
   ```
   http://YOUR_PI_IP:8000
   ```

## Troubleshooting

### Display Not Working

1. **Check SPI is enabled:**
   ```bash
   lsmod | grep spi
   ```
   Should show `spi_bcm2835`

2. **Check connections:**
   - Verify ribbon cable is properly connected
   - Ensure HAT is firmly seated on GPIO pins

3. **Run test script:**
   ```bash
   python3 scripts/test-display.py
   ```

### Bluetooth Not Connecting

1. **Check Bluetooth status:**
   ```bash
   sudo systemctl status bluetooth
   ```

2. **Make discoverable:**
   ```bash
   sudo bluetoothctl
   power on
   discoverable on
   pairable on
   ```

3. **Check permissions:**
   ```bash
   sudo usermod -a -G bluetooth $USER
   ```
   Then logout and login again.

### Performance Issues

1. **Reduce refresh rate:**
   - Edit `config.yaml` and increase `refresh_interval`

2. **Check temperature:**
   ```bash
   vcgencmd measure_temp
   ```
   E-Paper works best between 0-40°C

3. **Monitor resources:**
   ```bash
   htop
   ```

## Next Steps

- [Configuration Guide](CONFIGURATION.md)
- [Widget Development](WIDGET_DEVELOPMENT.md)
- [Bluetooth Protocol](BLUETOOTH_PROTOCOL.md)
- [API Documentation](API.md)

## Getting Help

- Check logs: `journalctl -u lumy -f`
- GitHub Issues: [github.com/yourusername/lumy/issues]
- Waveshare Wiki: [E-Paper HAT Manual](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual)
