#!/bin/bash
set -e

echo "==========================================="
echo "Lumy Installation Script v3.0"
echo "For: Raspberry Pi Zero 2 W + Waveshare 7.3\" e-Paper HAT (E)"
echo "==========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

INSTALL_USER="${SUDO_USER:-$USER}"
INSTALL_DIR="/home/$INSTALL_USER/lumy"

echo "Installing for user: $INSTALL_USER"
echo "Installation directory: $INSTALL_DIR"
echo ""

#===========================================
# Step 1: System Packages
#===========================================
echo "Step 1/6: Installing system packages..."
apt-get update
apt-get install -y python3-pip python3-pil python3-numpy git

# Install BCM2835 library (required by Waveshare)
cd /tmp
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
./configure
make
make check
make install
cd ..
rm -rf bcm2835-1.71*

echo "✓ System packages installed"
echo ""

#===========================================
# Step 2: Enable SPI
#===========================================
echo "Step 2/6: Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/firmware/config.txt; then
    echo "dtparam=spi=on" >> /boot/firmware/config.txt
fi
echo "✓ SPI enabled (requires reboot to take effect)"
echo ""

#===========================================
# Step 3: Install Waveshare e-Paper Library
#===========================================
echo "Step 3/6: Installing Waveshare e-Paper library..."

# Clone official Waveshare repository
cd /tmp
rm -rf e-Paper
git clone https://github.com/waveshare/e-Paper
cd e-Paper/RaspberryPi_JetsonNano/python

# Install Python dependencies
pip3 install pillow --break-system-packages
pip3 install RPi.GPIO --break-system-packages
pip3 install spidev --break-system-packages

# Copy library files to system location
mkdir -p /usr/local/lib/python3.11/dist-packages/waveshare_epd
cp -r lib/waveshare_epd/* /usr/local/lib/python3.11/dist-packages/waveshare_epd/

echo "✓ Waveshare library installed"
echo ""

#===========================================
# Step 4: Install Lumy Backend Dependencies
#===========================================
echo "Step 4/6: Installing Lumy backend dependencies..."
pip3 install fastapi uvicorn pydantic aiohttp python-dotenv --break-system-packages

echo "✓ Backend dependencies installed"
echo ""

#===========================================
# Step 5: Test Display
#===========================================
echo "Step 5/6: Testing e-Paper display..."

# Create test script
cat > /tmp/test_display.py << 'TESTPY'
#!/usr/bin/python3
import sys
sys.path.append('/usr/local/lib/python3.11/dist-packages')

from waveshare_epd import epd7in3e
from PIL import Image, ImageDraw, ImageFont
import time

try:
    print("Initializing 7.3inch e-Paper HAT (E)...")
    epd = epd7in3e.EPD()
    epd.init()
    epd.Clear()
    
    print("Creating test image...")
    image = Image.new('RGB', (epd.width, epd.height), 0xFFFFFF)
    draw = ImageDraw.Draw(image)
    
    # Try to load font, fallback to default
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw test message
    draw.text((50, 150), "Lumy Display", font=font_large, fill=0x000000)
    draw.text((50, 280), "Installation Successful!", font=font_small, fill=0x000000)
    
    print("Displaying image...")
    epd.display(epd.getbuffer(image))
    
    print("Entering sleep mode...")
    epd.sleep()
    
    print("✓ Display test PASSED!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Display test FAILED: {e}")
    sys.exit(1)
TESTPY

python3 /tmp/test_display.py

if [ $? -eq 0 ]; then
    echo "✓ Display working correctly"
else
    echo "✗ Display test failed - check connections"
    exit 1
fi
echo ""

#===========================================
# Step 6: Create Systemd Service
#===========================================
echo "Step 6/6: Creating systemd service..."

# Create service file
cat > /etc/systemd/system/lumy.service << EOF
[Unit]
Description=Lumy E-Paper Display Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/backend
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONPATH=/usr/local/lib/python3.11/dist-packages"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lumy.service

echo "✓ Systemd service created"
echo ""

echo "==========================================="
echo "✓ INSTALLATION COMPLETE!"
echo "==========================================="
echo ""
echo "IMPORTANT: System will reboot in 10 seconds to enable SPI."
echo "After reboot, the Lumy service will start automatically."
echo ""
echo "Press Ctrl+C to cancel reboot, or wait..."
sleep 10

reboot
