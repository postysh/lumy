#!/bin/bash
# Standalone script to install Waveshare E-Paper library
# Run this if the main installation failed to install the library
# Optimized for Raspberry Pi Zero 2 W (low memory)

set -e

echo "Installing Waveshare E-Paper Library"
echo "====================================="
echo "Using direct file download (optimized for Pi Zero)"
echo ""

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy
sudo apt-get install -y libopenjp2-7 libtiff6 || sudo apt-get install -y libtiff5 || true
sudo apt-get install -y python3-spidev

# Create temporary directory
echo "Setting up installation directory..."
TMP_DIR="/tmp/waveshare_install_$$"
mkdir -p "$TMP_DIR/waveshare_epd"
cd "$TMP_DIR"

# Base URL for raw files
BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python"

# Download only the files we need
echo "Downloading library files..."
echo "  - setup.py"
wget -q "$BASE_URL/setup.py" -O setup.py || {
    echo "Failed to download setup.py"
    exit 1
}

echo "  - README.md"
wget -q "$BASE_URL/README.md" -O README.md || true

echo "  - waveshare_epd/__init__.py"
wget -q "$BASE_URL/lib/waveshare_epd/__init__.py" -O waveshare_epd/__init__.py || {
    echo "Failed to download __init__.py"
    exit 1
}

echo "  - waveshare_epd/epdconfig.py"
wget -q "$BASE_URL/lib/waveshare_epd/epdconfig.py" -O waveshare_epd/epdconfig.py || {
    echo "Failed to download epdconfig.py"
    exit 1
}

echo "  - waveshare_epd/epd7in3e.py"
wget -q "$BASE_URL/lib/waveshare_epd/epd7in3e.py" -O waveshare_epd/epd7in3e.py || {
    echo "Failed to download epd7in3e.py"
    exit 1
}

# Create a minimal setup.py if download failed
if [ ! -f setup.py ]; then
    echo "Creating minimal setup.py..."
    cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name='waveshare-epd',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'RPi.GPIO',
        'spidev',
    ],
    description='Waveshare E-Paper Display Library',
)
EOF
fi

echo ""
echo "Installing library..."
# Try pip install
sudo pip3 install . --break-system-packages 2>/dev/null || sudo pip3 install . || {
    echo "pip install failed, trying direct copy..."
    # Fallback: copy directly to site-packages
    SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
    sudo cp -r waveshare_epd "$SITE_PACKAGES/"
    echo "Copied to $SITE_PACKAGES"
}

# Cleanup
cd /tmp
rm -rf "$TMP_DIR"

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
    echo "Trying to diagnose the issue..."
    python3 -c "import waveshare_epd.epd7in3e" 2>&1 || true
    echo ""
    echo "Please check the errors above and try:"
    echo "  1. Make sure SPI is enabled: sudo raspi-config"
    echo "  2. Reboot: sudo reboot"
    echo "  3. Try this script again"
fi

cd ~
