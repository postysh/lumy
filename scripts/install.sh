#!/bin/bash
set -e

echo "==========================================="
echo "Lumy Installation - WiFi AP Setup"
echo "Raspberry Pi Zero 2 W + Waveshare 7.3\" e-Paper"
echo "==========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo bash install.sh"
    exit 1
fi

USER="${SUDO_USER:-$USER}"
echo "Installing for user: $USER"
echo ""

#===========================================
# Step 1: System Packages
#===========================================
echo "Step 1/5: Installing packages..."
apt-get update
apt-get install -y python3-pip python3-pil python3-numpy python3-rpi.gpio python3-spidev git hostapd dnsmasq

echo "✓ Packages installed"
echo ""

#===========================================
# Step 2: Enable SPI
#===========================================
echo "Step 2/5: Enabling SPI..."
if ! grep -q "^dtparam=spi=on" /boot/firmware/config.txt; then
    echo "dtparam=spi=on" >> /boot/firmware/config.txt
    echo "✓ SPI enabled (requires reboot)"
else
    echo "✓ SPI already enabled"
fi
echo ""

#===========================================
# Step 3: Install Waveshare Library
#===========================================
echo "Step 3/5: Installing Waveshare library..."

# Install Python packages
pip3 install pillow --break-system-packages

# Download only the 3 files we need
mkdir -p /usr/local/lib/python3.11/dist-packages/waveshare_epd
cd /usr/local/lib/python3.11/dist-packages/waveshare_epd

BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd"
wget -q "${BASE_URL}/__init__.py" -O __init__.py
wget -q "${BASE_URL}/epdconfig.py" -O epdconfig.py
wget -q "${BASE_URL}/epd7in3e.py" -O epd7in3e.py

echo "✓ Waveshare library installed"
echo ""

#===========================================
# Step 4: Configure WiFi AP
#===========================================
echo "Step 4/5: Configuring WiFi AP..."

# Stop services
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true
systemctl unmask hostapd

# Configure hostapd
cat > /etc/hostapd/hostapd.conf << 'EOF'
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
country_code=US
EOF

# Configure dnsmasq
cat > /etc/dnsmasq.conf << 'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/lumy.local/192.168.4.1
EOF

# Configure dhcpcd
cat > /etc/dhcpcd.conf << 'EOF'
hostname
clientid
persistent
option rapid_commit
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
option interface_mtu
require dhcp_server_identifier
slaac private

interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF

echo "✓ WiFi AP configured"
echo ""

#===========================================
# Step 5: Create Lumy Service
#===========================================
echo "Step 5/5: Creating services..."

# Create simple Python backend
mkdir -p /home/$USER/lumy/backend
cat > /home/$USER/lumy/backend/main.py << 'PYTHON'
#!/usr/bin/python3
import sys
sys.path.append('/usr/local/lib/python3.11/dist-packages')

from waveshare_epd import epd7in3e
from PIL import Image, ImageDraw, ImageFont
import time

def main():
    try:
        print("Initializing display...")
        epd = epd7in3e.EPD()
        epd.init()
        epd.Clear()
        
        # Create image
        image = Image.new('RGB', (800, 480), 0xFFFFFF)
        draw = ImageDraw.Draw(image)
        
        # Load font
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        draw.text((50, 200), "Connect to WiFi:", font=font, fill=0x000000)
        draw.text((50, 280), "Lumy-Setup", font=font, fill=0x0000FF)
        
        # Display
        epd.display(epd.getbuffer(image))
        epd.sleep()
        
        print("Display updated successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
PYTHON

# Download WiFi setup server
cd /home/$USER/lumy/backend
wget -q https://raw.githubusercontent.com/postysh/lumy/main/backend/wifi_setup.py -O wifi_setup.py
chmod +x wifi_setup.py

chown -R $USER:$USER /home/$USER/lumy

# Create WiFi setup service
cat > /etc/systemd/system/lumy-wifi-setup.service << EOF
[Unit]
Description=Lumy WiFi Setup Server
After=network.target hostapd.service dnsmasq.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/$USER/lumy/backend
ExecStart=/usr/bin/python3 wifi_setup.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service
cat > /etc/systemd/system/lumy.service << EOF
[Unit]
Description=Lumy Display Service
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/home/$USER/lumy/backend
ExecStart=/usr/bin/python3 main.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lumy.service
systemctl enable lumy-wifi-setup.service
systemctl enable hostapd
systemctl enable dnsmasq

echo "✓ Services created"
echo ""

echo "==========================================="
echo "✓ INSTALLATION COMPLETE"
echo "==========================================="
echo ""
echo "The system will reboot in 10 seconds."
echo "After reboot:"
echo "  1. Display will show 'Connect to WiFi: Lumy-Setup'"
echo "  2. Connect to Lumy-Setup WiFi network"
echo "  3. Browser should auto-open to configuration page"
echo ""
echo "Press Ctrl+C to cancel reboot..."
sleep 10

reboot
