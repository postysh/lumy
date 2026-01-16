#!/bin/bash
# Lumy Installation Script for Raspberry Pi

set -e

echo "==================================="
echo "  Lumy Installation Script"
echo "==================================="
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
sudo apt-get install -y libglib2.0-dev

# Enable SPI interface (required for E-Paper)
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Install Waveshare E-Paper library
echo "Installing Waveshare E-Paper library..."
cd /tmp
if [ -d "e-Paper" ]; then
    rm -rf e-Paper
fi
git clone --depth 1 https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo pip3 install .
cd ~

# Verify installation
echo "Verifying Waveshare library installation..."
python3 -c "import waveshare_epd.epd7in3e; print('✓ Waveshare library installed successfully')" || echo "⚠ Warning: Waveshare library may not be installed correctly"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
cd ~/lumy/backend
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js (for web dashboard)
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Setup web dashboard
echo "Setting up web dashboard..."
cd ~/lumy/web
npm install

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/lumy.service > /dev/null <<EOF
[Unit]
Description=Lumy E-Paper Display Service
After=network.target bluetooth.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/lumy/backend
Environment="PATH=/home/$USER/lumy/backend/venv/bin:/usr/bin"
ExecStart=/home/$USER/lumy/backend/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "Enabling Lumy service..."
sudo systemctl daemon-reload
sudo systemctl enable lumy.service

echo ""
echo "==================================="
echo "  Installation Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit configuration: nano ~/lumy/backend/config.yaml"
echo "2. Start Lumy: sudo systemctl start lumy"
echo "3. Check status: sudo systemctl status lumy"
echo "4. View logs: journalctl -u lumy -f"
echo ""
echo "Web dashboard: cd ~/lumy/web && npm run dev"
echo ""
