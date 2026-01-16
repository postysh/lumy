#!/bin/bash
# Lumy Installation Script for Raspberry Pi

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LUMY_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "==================================="
echo "  Lumy Installation Script"
echo "==================================="
echo ""
echo "Installing from: $LUMY_DIR"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python dependencies
echo "Installing Python and dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y python3-pil python3-numpy
sudo apt-get install -y libopenjp2-7 libtiff6 || sudo apt-get install -y libtiff5 || true

# Install system dependencies for Bluetooth
echo "Installing Bluetooth dependencies..."
sudo apt-get install -y bluetooth bluez libbluetooth-dev
sudo apt-get install -y libglib2.0-dev libdbus-1-dev pkg-config

# Enable SPI interface (required for E-Paper)
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Setup WiFi AP mode
echo "Setting up WiFi AP mode for initial configuration..."
bash "$LUMY_DIR/scripts/setup-ap-mode.sh"

# Determine the correct lumy directory path
if [ -d "$HOME/lumy" ]; then
    LUMY_DIR="$HOME/lumy"
elif [ -d "/home/$SUDO_USER/lumy" ]; then
    LUMY_DIR="/home/$SUDO_USER/lumy"
else
    echo "Error: Cannot find lumy directory"
    exit 1
fi

echo "Using Lumy directory: $LUMY_DIR"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
cd "$LUMY_DIR/backend"
python3 -m venv venv
source venv/bin/activate

# Install Python requirements (optimized for Pi)
echo "Installing Python packages (this may take 5-10 minutes on Pi Zero)..."
pip install --upgrade pip

# Install packages one by one for better progress visibility
echo "  • Installing core packages..."
pip install RPi.GPIO spidev Pillow

echo "  • Installing Bluetooth packages..."
pip install bleak

echo "  • Installing web framework..."
pip install fastapi uvicorn pydantic

echo "  • Installing utilities..."
pip install pyyaml aiohttp psutil python-dotenv

echo "✓ All Python packages installed"

# Install Waveshare E-Paper library into venv
echo "Installing Waveshare E-Paper library..."
TMP_DIR="/tmp/waveshare_install_$$"
mkdir -p "$TMP_DIR/waveshare_epd"
cd "$TMP_DIR"

BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python"
wget -q "$BASE_URL/lib/waveshare_epd/__init__.py" -O waveshare_epd/__init__.py
wget -q "$BASE_URL/lib/waveshare_epd/epdconfig.py" -O waveshare_epd/epdconfig.py
wget -q "$BASE_URL/lib/waveshare_epd/epd7in3e.py" -O waveshare_epd/epd7in3e.py

# Copy directly into venv site-packages
VENV_SITE_PACKAGES="$LUMY_DIR/backend/venv/lib/python*/site-packages"
cp -r waveshare_epd $VENV_SITE_PACKAGES/

cd /tmp
rm -rf "$TMP_DIR"

echo "✓ Waveshare library installed"

# Return to backend directory and deactivate venv
cd "$LUMY_DIR/backend"
deactivate

# Get the actual user (not root if using sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/lumy.service > /dev/null <<EOF
[Unit]
Description=Lumy E-Paper Display Service
After=network.target bluetooth.target

[Service]
Type=simple
User=root
WorkingDirectory=$LUMY_DIR/backend
Environment="PATH=$LUMY_DIR/backend/venv/bin:/usr/bin"
ExecStart=$LUMY_DIR/backend/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create .env file with production defaults (no user input needed)
echo ""
echo "==================================="
echo "  Configuration"
echo "==================================="
echo ""

# Use production API URL by default
PRODUCTION_API_URL="https://lumy-beta.vercel.app/api"
PRODUCTION_API_KEY="ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv"

echo "Using production configuration:"
echo "  API URL: $PRODUCTION_API_URL"
echo ""

# Create .env file in the correct location
cat > "$LUMY_DIR/backend/.env" << EOFENV
# Lumy Production Configuration
# This device will auto-register on first boot
LUMY_API_URL=$PRODUCTION_API_URL
LUMY_API_KEY=$PRODUCTION_API_KEY

# Device ID will be auto-generated on first run
# LUMY_DEVICE_ID=
# LUMY_USER_ID=
EOFENV

# Change ownership to actual user
sudo chown -R $ACTUAL_USER:$ACTUAL_USER "$LUMY_DIR"

echo "✓ Production configuration saved"

# Enable and start service
echo ""
echo "Enabling Lumy service..."
sudo systemctl daemon-reload
sudo systemctl enable lumy.service
sudo systemctl start lumy.service

echo ""
echo "==================================="
echo "  Installation Complete!"
echo "==================================="
echo ""
echo "✓ Lumy is now running as a system service"
echo "✓ It will auto-start on every reboot"
echo "✓ Display will show registration code on first boot"
echo ""
echo "DEVICE SETUP FOR CUSTOMER:"
echo "─────────────────────────────────────────"
echo "1. Ship this device to your customer"
echo "2. Customer powers on the device"
echo "3. Display shows: 'Welcome to Lumy' + Code"
echo "4. Customer visits: https://lumy-beta.vercel.app"
echo "5. Customer signs in and clicks 'Add Device'"
echo "6. Customer enters the code"
echo "7. Done! Device is now registered to them"
echo ""
echo "Useful commands:"
echo "  • View logs:      journalctl -u lumy -f"
echo "  • Check status:   sudo systemctl status lumy"
echo "  • Restart:        sudo systemctl restart lumy"
echo "  • Factory reset:  sudo bash scripts/factory-reset.sh"
echo ""
