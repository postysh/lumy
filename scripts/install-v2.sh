#!/bin/bash
# Lumy Installation Script v2 - Complete Rebuild
# Based on official Raspberry Pi Access Point setup

set -e

echo "==========================================="
echo "  Lumy Complete Installation (v2)"
echo "==========================================="
echo ""

# Get actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
LUMY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Installing from: $LUMY_DIR"
echo "Installing for user: $ACTUAL_USER"
echo ""

#===========================================
# STEP 1: System Packages
#===========================================
echo "Step 1/8: Installing system packages..."
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv python3-dev
sudo apt-get install -y python3-pil python3-numpy
sudo apt-get install -y python3-lgpio python3-gpiozero
sudo apt-get install -y fonts-dejavu fonts-dejavu-core
sudo apt-get install -y hostapd dnsmasq
echo "✓ System packages installed"
echo ""

#===========================================
# STEP 2: Enable SPI & Fix WiFi Driver
#===========================================
echo "Step 2/8: Enabling SPI interface..."
sudo raspi-config nonint do_spi 0
echo "✓ SPI enabled"

echo "  • Fixing WiFi driver issues..."
# Fix known brcmfmac driver issues on Pi Zero 2 W
sudo mkdir -p /etc/modprobe.d
sudo tee /etc/modprobe.d/brcmfmac.conf > /dev/null <<'WIFI_FIX'
# Fix WiFi connection issues on Pi Zero 2 W
options brcmfmac roamoff=1 feature_disable=0x82000
WIFI_FIX
echo "✓ WiFi driver configured"
echo ""

#===========================================
# STEP 3: Python Virtual Environment
#===========================================
echo "Step 3/8: Creating Python virtual environment..."
cd "$LUMY_DIR/backend"

# Remove old venv if exists
rm -rf venv

# Create venv with system site packages (for lgpio)
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install RPi.GPIO spidev Pillow
pip install fastapi uvicorn pydantic flask
pip install pyyaml aiohttp psutil python-dotenv jinja2

echo "✓ Python environment created"
echo ""

#===========================================
# STEP 4: Waveshare E-Paper Library
#===========================================
echo "Step 4/8: Installing Waveshare E-Paper library..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download only necessary files
mkdir -p waveshare_epd
cd waveshare_epd
wget -q https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/__init__.py
wget -q https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in3e.py
wget -q https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py
cd ..

# Create setup.py at the root level
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages
setup(
    name='waveshare-epd',
    version='1.0',
    packages=['waveshare_epd'],
    install_requires=['Pillow', 'RPi.GPIO', 'spidev']
)
SETUP

# Install into venv
cd "$LUMY_DIR/backend"
source venv/bin/activate
pip install "$TEMP_DIR"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✓ Waveshare library installed"
echo ""

#===========================================
# STEP 5: GPIO Cleanup Script
#===========================================
echo "Step 5/8: Creating GPIO cleanup script..."
sudo tee /usr/local/bin/lumy-gpio-cleanup.sh > /dev/null <<'CLEANUP'
#!/bin/bash
# Clean up GPIO before starting display

# Unexport all GPIO pins via sysfs
for pin in /sys/class/gpio/gpio*; do
    if [ -d "$pin" ]; then
        echo $(basename "$pin" | sed 's/gpio//') > /sys/class/gpio/unexport 2>/dev/null || true
    fi
done

# Use RPi.GPIO cleanup
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.cleanup()" 2>/dev/null || true

exit 0
CLEANUP

sudo chmod +x /usr/local/bin/lumy-gpio-cleanup.sh
echo "✓ GPIO cleanup script created"
echo ""

#===========================================
# STEP 6: Display Test
#===========================================
echo "Step 6/8: Testing E-Paper display..."
cd "$LUMY_DIR/backend"

# Run GPIO cleanup
sudo /usr/local/bin/lumy-gpio-cleanup.sh

echo "  • Running display test..."
sudo "$LUMY_DIR/backend/venv/bin/python3" << 'DISPLAY_TEST'
import sys
import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'

try:
    from waveshare_epd import epd7in3e
    from PIL import Image, ImageDraw, ImageFont
    
    print("  • Initializing display...")
    epd = epd7in3e.EPD()
    epd.init()
    
    print("  • Creating test image...")
    image = Image.new('RGB', (800, 480), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Use large, readable fonts that fit 800x480
    try:
        font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
        font_subtitle = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 44)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()

    # Center text
    title_text = "Install Complete"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    
    subtitle_text = "Display Working"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_subtitle)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    
    center_x = 400
    center_y = 240
    
    draw.text((center_x - title_width // 2, center_y - title_height - 20), title_text, font=font_title, fill=(0, 150, 0))
    draw.text((center_x - subtitle_width // 2, center_y + 20), subtitle_text, font=font_subtitle, fill=(100, 100, 100))
    
    print("  • Displaying on screen...")
    epd.display(epd.getbuffer(image))
    epd.sleep()
    
    print("✓ Display test PASSED!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Display test FAILED: {e}")
    print("\nPossible issues:")
    print("  1. E-Paper HAT not properly connected")
    print("  2. SPI not enabled (reboot may be needed)")
    print("  3. Hardware issue with display")
    sys.exit(1)
DISPLAY_TEST

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Display test failed. Please fix the display before continuing."
    exit 1
fi

echo "✓ Display test passed"
echo ""

#===========================================
# STEP 7: WiFi Access Point Setup
#===========================================
echo "Step 7/8: Setting up WiFi Access Point..."

# Stop services
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Configure dhcpcd for static IP (CRITICAL - prevents wpa_supplicant interference)
echo "  • Configuring dhcpcd..."
if ! grep -q "^interface wlan0$" /etc/dhcpcd.conf; then
    sudo tee -a /etc/dhcpcd.conf > /dev/null <<'DHCPCD'

# Lumy AP Mode Configuration
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
DHCPCD
fi

# Configure hostapd (minimal, proven config)
echo "  • Configuring hostapd..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<'HOSTAPD'
interface=wlan0
driver=nl80211
ssid=Lumy-Setup
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
country_code=US
HOSTAPD

# Set hostapd config path
sudo sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd 2>/dev/null || true
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee -a /etc/default/hostapd > /dev/null

# Configure dnsmasq for DHCP
echo "  • Configuring dnsmasq..."
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true
sudo tee /etc/dnsmasq.conf > /dev/null <<'DNSMASQ'
interface=wlan0
bind-interfaces
dhcp-range=192.168.4.10,192.168.4.250,255.255.255.0,24h
dhcp-option=3,192.168.4.1
dhcp-option=6,192.168.4.1
# Captive portal DNS redirects
address=/connectivitycheck.gstatic.com/192.168.4.1
address=/captive.apple.com/192.168.4.1
address=/www.msftconnecttest.com/192.168.4.1
DNSMASQ

# Create lumy-ap service (called by wifi_manager.py)
echo "  • Creating lumy-ap service..."
sudo tee /etc/systemd/system/lumy-ap.service > /dev/null <<'APSERVICE'
[Unit]
Description=Lumy WiFi Access Point
After=dhcpcd.service
Wants=dhcpcd.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/usr/sbin/rfkill unblock wifi
ExecStartPre=/bin/sleep 1
ExecStartPre=/bin/systemctl restart dhcpcd
ExecStartPre=/bin/sleep 3
ExecStart=/bin/systemctl start hostapd
ExecStartPost=/bin/sleep 2
ExecStartPost=/bin/systemctl start dnsmasq
ExecStop=/bin/systemctl stop dnsmasq
ExecStop=/bin/systemctl stop hostapd
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
APSERVICE

# Unmask and disable services (only start when lumy-ap calls them)
echo "  • Configuring services..."
sudo systemctl unmask hostapd
sudo systemctl unmask dnsmasq
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq
sudo systemctl daemon-reload

echo "✓ WiFi AP configured"
echo ""

#===========================================
# STEP 8: Lumy Service
#===========================================
echo "Step 8/8: Creating Lumy systemd service..."

sudo tee /etc/systemd/system/lumy.service > /dev/null <<EOF
[Unit]
Description=Lumy E-Paper Display Service
After=network.target dhcpcd.service
Wants=dhcpcd.service

[Service]
Type=simple
User=root
WorkingDirectory=$LUMY_DIR/backend
Environment="PYTHONUNBUFFERED=1"
Environment="GPIOZERO_PIN_FACTORY=lgpio"
ExecStartPre=/usr/local/bin/lumy-gpio-cleanup.sh
ExecStart=$LUMY_DIR/backend/venv/bin/python3 -u main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable lumy.service

echo "✓ Lumy service created"
echo ""

#===========================================
# Create Configuration
#===========================================
echo "Step 9/8: Creating configuration..."

cd "$LUMY_DIR/backend"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    tee .env > /dev/null <<ENV
# Lumy Configuration
LUMY_API_URL=https://lumy-beta.vercel.app/api
LUMY_API_KEY=ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv

# Device-specific (auto-generated on first run)
# LUMY_DEVICE_ID=
# LUMY_USER_ID=
ENV
fi

echo "✓ Configuration created"
echo ""

#===========================================
# Installation Complete
#===========================================
echo "==========================================="
echo "  ✓ INSTALLATION COMPLETE!"
echo "==========================================="
echo ""
echo "Display: Test passed ✓"
echo "WiFi AP: Configured for AP mode"
echo "Service: Enabled and ready"
echo ""
echo "IMPORTANT: Reboot required for WiFi AP to start"
echo ""
echo "After reboot:"
echo "  • Display will show setup instructions"
echo "  • Connect to WiFi: Lumy-Setup"
echo "  • Open browser to: http://192.168.4.1"
echo "  • Configure home WiFi"
echo "  • Device will show registration code"
echo ""
echo "Useful commands:"
echo "  • View logs: sudo journalctl -u lumy -f"
echo "  • Check status: sudo systemctl status lumy"
echo "  • Restart: sudo systemctl restart lumy"
echo ""
read -p "Reboot now? (yes/no): " -r
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    sudo reboot
fi
