#!/bin/bash
# Lumy Installation Script - Complete Setup for Raspberry Pi
# This script installs everything needed for Lumy to work properly

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LUMY_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "==========================================="
echo "  Lumy Complete Installation"
echo "==========================================="
echo ""
echo "Installing from: $LUMY_DIR"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠ Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install git if not present
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo apt-get install -y git
fi

# Get actual user (not root if using sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"
echo "Installing for user: $ACTUAL_USER"
echo ""

#===========================================
# STEP 1: System Packages
#===========================================
echo "Step 1/10: Installing system packages..."
sudo apt-get update
sudo apt-get install -y git build-essential
sudo apt-get install -y python3 python3-pip python3-venv python3-dev
sudo apt-get install -y python3-pil python3-numpy
sudo apt-get install -y libopenjp2-7 libtiff6 || true
# GPIO libraries (lgpio is needed for modern Raspberry Pi OS)
sudo apt-get install -y python3-lgpio python3-gpiozero
sudo apt-get install -y bluetooth bluez libbluetooth-dev
sudo apt-get install -y libglib2.0-dev libdbus-1-dev pkg-config
sudo apt-get install -y hostapd dnsmasq
echo "✓ System packages installed"
echo ""

#===========================================
# STEP 2: Enable SPI
#===========================================
echo "Step 2/10: Enabling SPI interface..."
sudo raspi-config nonint do_spi 0
echo "✓ SPI enabled"
echo ""

#===========================================
# STEP 3: Python Virtual Environment
#===========================================
echo "Step 3/10: Creating Python virtual environment..."
cd "$LUMY_DIR/backend"
# Create venv with access to system site-packages (for lgpio/gpiozero)
python3 -m venv --system-site-packages venv
source venv/bin/activate

echo "Step 4/10: Installing Python packages..."
pip install --upgrade pip

# Install all packages (gpiozero is system-installed with lgpio support)
pip install RPi.GPIO spidev Pillow
pip install bleak
pip install fastapi uvicorn pydantic flask
pip install pyyaml aiohttp psutil python-dotenv jinja2

echo "✓ Python packages installed"
echo ""

#===========================================
# STEP 5: Install Waveshare Library (Lightweight)
#===========================================
echo "Step 5/10: Installing Waveshare E-Paper library..."

# Download only the Python library files we need (not the entire 46MB repo)
cd /tmp
rm -rf waveshare_epd_install
mkdir -p waveshare_epd_install/waveshare_epd
cd waveshare_epd_install

# Download library files directly (unmodified from Waveshare)
BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd"
wget -q "$BASE_URL/__init__.py" -O waveshare_epd/__init__.py
wget -q "$BASE_URL/epdconfig.py" -O waveshare_epd/epdconfig.py  
wget -q "$BASE_URL/epd7in3e.py" -O waveshare_epd/epd7in3e.py

# Create minimal setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages
setup(
    name='waveshare-epd',
    version='1.0',
    packages=find_packages(),
    install_requires=['Pillow', 'RPi.GPIO', 'spidev'],
)
EOF

# Install into venv
cd "$LUMY_DIR/backend"
source venv/bin/activate
cd /tmp/waveshare_epd_install
pip install .

# Verify (skip GPIO init check - will be handled by display manager)
python3 << 'VERIFY'
import sys
sys.path.insert(0, '/tmp/waveshare_epd_install')
# Just verify the module can be imported
import waveshare_epd
print('✓ Waveshare library installed')
VERIFY

if [ $? -ne 0 ]; then
    echo "✗ Failed to install Waveshare library"
    exit 1
fi

# Cleanup
cd /tmp
rm -rf waveshare_epd_install

echo ""

#===========================================
# STEP 6: Create GPIO Cleanup Script (needed for display test)
#===========================================
echo "Step 6/10: Creating GPIO cleanup script..."
sudo tee /usr/local/bin/lumy-gpio-cleanup.sh > /dev/null <<'GPIOEOF'
#!/bin/bash
# GPIO cleanup - Waveshare troubleshooting
# See: https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual

# Unexport all GPIO pins via sysfs (most reliable method)
for pin in /sys/class/gpio/gpio*/; do
    if [ -d "$pin" ]; then
        pin_num=$(basename "$pin" | sed 's/gpio//')
        echo "$pin_num" > /sys/class/gpio/unexport 2>/dev/null || true
    fi
done

# Clean up via RPi.GPIO (secondary method)
python3 << 'PYCLEANUP'
try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
except:
    pass
PYCLEANUP

# Brief delay for cleanup to complete
sleep 0.2
GPIOEOF

sudo chmod +x /usr/local/bin/lumy-gpio-cleanup.sh
echo "✓ GPIO cleanup script created"
echo ""

#===========================================
# STEP 7: Test Display (CRITICAL)
#===========================================
echo "Step 7/10: Testing E-Paper display..."
cd "$LUMY_DIR/backend"

# Run GPIO cleanup before display test
echo "  • Cleaning GPIO pins..."
sudo /usr/local/bin/lumy-gpio-cleanup.sh

echo "  • Running display test..."
# MUST run as root for GPIO access, using venv python
sudo "$LUMY_DIR/backend/venv/bin/python3" << 'DISPLAY_TEST'
import sys
import os
# Use system-installed lgpio (modern GPIO library)
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
    
    # Use readable font sizes for 800x480 display
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 58)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Center text
    center_x = 400
    
    # Title
    title = "Installation Complete"
    title_bbox = draw.textbbox((0, 0), title, font=font_large)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((center_x - title_width // 2, 140), title, font=font_large, fill=(0, 150, 0))
    
    # Subtitle
    subtitle = "Display is working correctly"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text((center_x - subtitle_width // 2, 240), subtitle, font=font_small, fill=(100, 100, 100))
    
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
    echo "==========================================="
    echo "  ✗ INSTALLATION FAILED"
    echo "==========================================="
    echo ""
    echo "Display test failed. Please check:"
    echo "  1. E-Paper HAT is properly connected to GPIO pins"
    echo "  2. Reboot and try again (SPI may need reboot)"
    echo "  3. Check hardware connections"
    echo ""
    exit 1
fi

echo ""

#===========================================
# STEP 7: WiFi AP Mode Setup
#===========================================
echo "Step 8/10: Setting up WiFi AP mode..."

# Stop services during configuration
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Configure hostapd for Pi Zero 2 W
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<'EOF'
interface=wlan0
driver=nl80211
ssid=Lumy-Setup
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
EOF

# Stop and disable services that interfere with AP mode
sudo systemctl stop NetworkManager 2>/dev/null || true
sudo systemctl disable NetworkManager 2>/dev/null || true
sudo systemctl stop wpa_supplicant 2>/dev/null || true
sudo systemctl disable wpa_supplicant 2>/dev/null || true
sudo systemctl unmask hostapd 2>/dev/null || true
sudo systemctl unmask dnsmasq 2>/dev/null || true

# Configure dnsmasq
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true
sudo tee /etc/dnsmasq.conf > /dev/null <<'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
EOF

# Create network startup script for AP mode
sudo tee /usr/local/bin/lumy-start-ap.sh > /dev/null <<'APSCRIPT'
#!/bin/bash
set -e

echo "=== Starting Lumy AP Mode ==="

# Kill any interfering processes
pkill wpa_supplicant || true
pkill NetworkManager || true
pkill dhcpcd || true

# Unblock WiFi
rfkill unblock wifi
sleep 1

# Reset interface
ip link set wlan0 down
sleep 1
ip addr flush dev wlan0
sleep 1

# Configure interface for AP mode
ip addr add 192.168.4.1/24 dev wlan0
ip link set wlan0 up
sleep 2

# Start hostapd
echo "Starting hostapd..."
systemctl start hostapd
sleep 3

# Start dnsmasq
echo "Starting dnsmasq..."
systemctl start dnsmasq
sleep 1

echo "=== AP Mode Started Successfully ==="
echo "SSID: $(grep ^ssid= /etc/hostapd/hostapd.conf | cut -d= -f2)"
echo "IP: 192.168.4.1"
APSCRIPT

sudo chmod +x /usr/local/bin/lumy-start-ap.sh

# Create AP mode systemd service
sudo tee /etc/systemd/system/lumy-ap.service > /dev/null <<'EOF'
[Unit]
Description=Lumy WiFi Access Point
After=network.target
Conflicts=NetworkManager.service wpa_supplicant.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/lumy-start-ap.sh
ExecStop=/usr/bin/bash -c 'systemctl stop hostapd; systemctl stop dnsmasq; ip link set wlan0 down'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✓ WiFi AP mode configured"
echo ""

#===========================================
# STEP 9: Systemd Service
#===========================================
echo "Step 9/10: Creating systemd service..."
sudo tee /etc/systemd/system/lumy.service > /dev/null <<EOF
[Unit]
Description=Lumy E-Paper Display Service
After=network.target bluetooth.target

[Service]
Type=simple
User=root
WorkingDirectory=$LUMY_DIR/backend
Environment="PATH=$LUMY_DIR/backend/venv/bin:/usr/bin"
Environment="GPIOZERO_PIN_FACTORY=lgpio"
ExecStartPre=/usr/local/bin/lumy-gpio-cleanup.sh
ExecStart=$LUMY_DIR/backend/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service created"
echo ""

#===========================================
# STEP 10: Configuration
#===========================================
echo "Step 10/10: Creating configuration..."

# Production configuration
PRODUCTION_API_URL="https://lumy-beta.vercel.app/api"
PRODUCTION_API_KEY="ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv"

cat > "$LUMY_DIR/backend/.env" << EOFENV
# Lumy Production Configuration
LUMY_API_URL=$PRODUCTION_API_URL
LUMY_API_KEY=$PRODUCTION_API_KEY

# GPIO Configuration (use system lgpio library)
GPIOZERO_PIN_FACTORY=lgpio

# Device ID will be auto-generated on first run
# LUMY_DEVICE_ID=
# LUMY_USER_ID=
EOFENV

# Change ownership to actual user
sudo chown -R $ACTUAL_USER:$ACTUAL_USER "$LUMY_DIR"

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable lumy.service
sudo systemctl start lumy.service

echo "✓ Configuration complete"
echo ""

#===========================================
# Installation Complete
#===========================================
echo "==========================================="
echo "  ✓ INSTALLATION COMPLETE!"
echo "==========================================="
echo ""
echo "Lumy is now running and will auto-start on boot."
echo ""
echo "The device will show a registration code on the display."
echo "Users can visit: https://lumy-beta.vercel.app"
echo "And enter the code to claim their device."
echo ""
echo "Useful commands:"
echo "  • View logs:      sudo journalctl -u lumy -f"
echo "  • Check status:   sudo systemctl status lumy"
echo "  • Restart:        sudo systemctl restart lumy"
echo "  • Factory reset:  sudo bash scripts/factory-reset.sh"
echo ""
