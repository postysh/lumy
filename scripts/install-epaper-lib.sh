#!/bin/bash
# Standalone script to install Waveshare E-Paper library
# Run this if the main installation failed to install the library

set -e

echo "Installing Waveshare E-Paper Library"
echo "====================================="

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy
sudo apt-get install -y libopenjp2-7 libtiff6 || sudo apt-get install -y libtiff5 || true
sudo apt-get install -y python3-spidev

# Install library
echo "Cloning Waveshare repository..."
cd /tmp
if [ -d "e-Paper" ]; then
    rm -rf e-Paper
fi
git clone https://github.com/waveshare/e-Paper.git

echo "Installing library..."
cd e-Paper/RaspberryPi_JetsonNano/python

# Try pip install first
sudo pip3 install . || {
    echo "pip install failed, trying setup.py..."
    sudo python3 setup.py install
}

# Verify
echo ""
echo "Verifying installation..."
if python3 -c "import waveshare_epd.epd7in3e" 2>/dev/null; then
    echo "✓ Waveshare library installed successfully!"
    echo ""
    echo "You can now run:"
    echo "  cd ~/lumy"
    echo "  python3 scripts/test-display.py"
else
    echo "✗ Installation verification failed"
    echo ""
    echo "Please check the errors above and try:"
    echo "  1. Make sure SPI is enabled: sudo raspi-config"
    echo "  2. Reboot: sudo reboot"
    echo "  3. Try this script again"
fi

cd ~
