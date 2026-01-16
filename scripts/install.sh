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
python3 -m venv venv
source venv/bin/activate

echo "Step 4/10: Installing Python packages..."
pip install --upgrade pip

# Install all packages (use RPi.GPIO backend, no need for lgpio)
pip install RPi.GPIO spidev Pillow
pip install gpiozero colorzero
pip install bleak
pip install fastapi uvicorn pydantic
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

deactivate

# Cleanup
cd /tmp
rm -rf waveshare_epd_install

echo ""

#===========================================
# STEP 6: Test Display (CRITICAL)
#===========================================
echo "Step 6/10: Testing E-Paper display..."
cd "$LUMY_DIR/backend"

# Run GPIO cleanup before display test
echo "  • Cleaning GPIO pins..."
sudo /usr/local/bin/lumy-gpio-cleanup.sh

echo "  • Running display test..."
# MUST run as root for GPIO access
sudo "$LUMY_DIR/backend/venv/bin/python3" << 'DISPLAY_TEST'
import sys
import os
# Force gpiozero to use RPi.GPIO backend (already installed)
os.environ['GPIOZERO_PIN_FACTORY'] = 'rpigpio'

try:
    from waveshare_epd import epd7in3e
    from PIL import Image, ImageDraw, ImageFont
    
    print("  • Initializing display...")
    epd = epd7in3e.EPD()
    epd.init()
    
    print("  • Creating test image...")
    image = Image.new('RGB', (800, 480), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((200, 200), "Lumy Install Test", font=font, fill=(0, 0, 0))
    draw.text((250, 280), "Display Working!", font=font, fill=(0, 0, 255))
    
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
echo "Step 7/10: Setting up WiFi AP mode..."

# Stop services during configuration
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Configure hostapd
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<'EOF'
interface=wlan0
driver=nl80211
ssid=Lumy-Setup
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
EOF

sudo tee /etc/default/hostapd > /dev/null <<'EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Configure dnsmasq
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true
sudo tee /etc/dnsmasq.conf > /dev/null <<'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
EOF

# Create AP mode systemd service
sudo tee /etc/systemd/system/lumy-ap.service > /dev/null <<'EOF'
[Unit]
Description=Lumy WiFi Access Point
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c '\
    systemctl stop wpa_supplicant; \
    ifconfig wlan0 down; \
    ifconfig wlan0 192.168.4.1 netmask 255.255.255.0 up; \
    systemctl start hostapd; \
    systemctl start dnsmasq'
ExecStop=/usr/bin/bash -c '\
    systemctl stop hostapd; \
    systemctl stop dnsmasq; \
    systemctl start wpa_supplicant; \
    systemctl restart dhcpcd'

[Install]
WantedBy=multi-user.target
EOF

# Disable services by default (only start when needed)
sudo systemctl disable hostapd 2>/dev/null || true
sudo systemctl disable dnsmasq 2>/dev/null || true

echo "✓ WiFi AP mode configured"
echo ""

#===========================================
# STEP 8: GPIO Cleanup Script
#===========================================
echo "Step 8/10: Creating GPIO cleanup script..."
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
Environment="GPIOZERO_PIN_FACTORY=rpigpio"
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

# GPIO Configuration (use RPi.GPIO backend for gpiozero)
GPIOZERO_PIN_FACTORY=rpigpio

# Device ID will be auto-generated on first run
# LUMY_DEVICE_ID=
# LUMY_USER_ID=
EOFENV

# Change ownership to actual user
sudo chown -R $ACTUAL_USER:$ACTUAL_USER "$LUMY_DIR"

deactivate

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
