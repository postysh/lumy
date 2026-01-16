# Lumy Quick Start Guide

Get your Lumy E-Paper display up and running in minutes!

## Prerequisites

- Raspberry Pi Zero 2 W with Raspberry Pi OS installed
- Waveshare 7.3" E-Paper HAT (E) connected
- Internet connection
- SSH access to your Pi

## Quick Installation

### 1. Connect to Your Raspberry Pi

```bash
ssh pi@raspberrypi.local
```

### 2. Clone and Install

```bash
cd ~
git clone https://github.com/yourusername/lumy.git
cd lumy
chmod +x scripts/install.sh
./scripts/install.sh
```

The installation takes about 10-15 minutes. It will:
- Install all dependencies
- Setup Python environment
- Configure Bluetooth
- Enable SPI for E-Paper
- Create systemd service

### 3. Test Your Display

```bash
python3 scripts/test-display.py
```

You should see a test pattern appear on your E-Paper display!

### 4. Configure (Optional)

Edit the configuration file to customize:

```bash
nano backend/config.yaml
```

Key settings:
- `display.refresh_interval`: How often to update (seconds)
- `widgets.default_widgets`: Which widgets to display
- `bluetooth.device_name`: Name visible to iPhone

### 5. Start Lumy

```bash
sudo systemctl start lumy
sudo systemctl status lumy
```

### 6. Access Web Dashboard

Find your Pi's IP address:

```bash
hostname -I
```

Open in your browser (or iPhone Safari):
```
http://YOUR_PI_IP:8000
```

## Your First Widget

The default setup includes three widgets:
- **Clock**: Shows current time and date
- **Weather**: Displays weather (needs API key)
- **Calendar**: Shows upcoming events

## Connect from iPhone

### Option 1: Web Dashboard

1. Open Safari on iPhone
2. Navigate to `http://YOUR_PI_IP:8000`
3. Bookmark for easy access
4. Use Quick Actions to refresh display

### Option 2: Bluetooth (Coming Soon)

1. Enable Bluetooth on iPhone
2. Look for "Lumy Display" in Bluetooth settings
3. Pair with device
4. Use custom iOS app (under development)

## Common Commands

### Start/Stop Lumy

```bash
sudo systemctl start lumy   # Start
sudo systemctl stop lumy    # Stop
sudo systemctl restart lumy # Restart
```

### View Logs

```bash
journalctl -u lumy -f
```

### Manual Run (for debugging)

```bash
cd ~/lumy/backend
source venv/bin/activate
python3 main.py
```

## Troubleshooting

### Display shows nothing
- Check connections: ribbon cable and HAT seating
- Verify SPI is enabled: `lsmod | grep spi`
- Run test script: `python3 scripts/test-display.py`

### Can't access web dashboard
- Check Lumy is running: `sudo systemctl status lumy`
- Verify IP address: `hostname -I`
- Check firewall: `sudo ufw status`

### Bluetooth not working
- Run setup: `./scripts/setup-bluetooth.sh`
- Check status: `sudo systemctl status bluetooth`
- Make discoverable: `sudo bluetoothctl` then `discoverable on`

## Next Steps

1. **Customize widgets:** [Widget Development Guide](WIDGET_DEVELOPMENT.md)
2. **Add weather API:** Get free key from [OpenWeatherMap](https://openweathermap.org/api)
3. **Build iOS app:** [Bluetooth Protocol](BLUETOOTH_PROTOCOL.md)
4. **Advanced config:** [Configuration Guide](CONFIGURATION.md)

## Get Help

- **Documentation:** `/docs` folder
- **Issues:** GitHub Issues
- **Logs:** `journalctl -u lumy -f`
- **Test display:** `python3 scripts/test-display.py`

## Tips

- **Reduce power:** Set longer `refresh_interval` to save battery
- **Better weather:** Add OpenWeatherMap API key for live data
- **Custom widgets:** Copy `clock_widget.py` as template
- **Auto-start:** Service starts automatically on boot
- **Remote access:** Use ngrok or tailscale for external access

Enjoy your Lumy display! 🎨✨
