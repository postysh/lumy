#!/bin/bash
set -e

echo "==========================================="
echo "Lumy Installation - Bluetooth Setup"
echo "Raspberry Pi Zero 2 W + Waveshare 7.3\""
echo "==========================================="
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo bash install.sh"
    exit 1
fi

USER="${SUDO_USER:-$USER}"
echo "Installing for user: $USER"
echo ""

# Check if we should clear WiFi (for production/customer devices)
CLEAR_WIFI=false
if [ "$1" == "--clear-wifi" ]; then
    CLEAR_WIFI=true
    echo "⚠️  WiFi will be cleared after installation"
    echo "⚠️  You will lose SSH access after reboot"
    echo ""
    echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
    sleep 5
else
    echo "ℹ️  WiFi will be preserved (development mode)"
    echo "ℹ️  Use: sudo bash install.sh --clear-wifi"
    echo "ℹ️  to clear WiFi for customer/production devices"
    echo ""
fi

#===========================================
# Step 1: System Packages
#===========================================
echo "Step 1/5: Installing packages..."
apt-get update
apt-get install -y python3-pip python3-pil python3-numpy python3-rpi.gpio python3-spidev git bluetooth bluez python3-bluez python3-dbus

# Install bluezero for easier BLE development
pip3 install bluezero --break-system-packages

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
# Step 4: Configure Bluetooth
#===========================================
echo "Step 4/5: Configuring Bluetooth..."

# Unblock Bluetooth (might be blocked by rfkill)
rfkill unblock bluetooth
sleep 1

# Enable Bluetooth
systemctl enable bluetooth
systemctl start bluetooth

# Configure Bluetooth to be discoverable and pairable
# Edit main.conf to allow discovery
cat >> /etc/bluetooth/main.conf << 'BTCONF'

[General]
Discoverable = true
DiscoverableTimeout = 0
PairableTimeout = 0
BTCONF

# Restart Bluetooth with new config
systemctl restart bluetooth
sleep 2

echo "✓ Bluetooth configured"
echo ""

#===========================================
# Step 5: Create Services
#===========================================
echo "Step 5/5: Creating services..."

# Create backend directory
mkdir -p /home/$USER/lumy/backend

# Download backend files
cd /home/$USER/lumy/backend
wget -q https://raw.githubusercontent.com/postysh/lumy/main/backend/ble_server.py -O ble_server.py
wget -q https://raw.githubusercontent.com/postysh/lumy/main/backend/main.py -O main.py
chmod +x ble_server.py main.py

chown -R $USER:$USER /home/$USER/lumy

# Create BLE service
cat > /etc/systemd/system/lumy-ble.service << EOF
[Unit]
Description=Lumy Bluetooth LE Setup Service
After=bluetooth.target
Requires=bluetooth.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/$USER/lumy/backend
ExecStartPre=/bin/sh -c '/usr/sbin/rfkill unblock bluetooth && sleep 1 && /usr/bin/bluetoothctl power on && sleep 1'
ExecStart=/usr/bin/python3 ble_server.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create display service (runs after WiFi is configured)
cat > /etc/systemd/system/lumy-display.service << EOF
[Unit]
Description=Lumy Display Service
After=network-online.target
Wants=network-online.target

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
systemctl enable lumy-ble.service
systemctl enable lumy-display.service

echo "✓ Services created"
echo ""

echo "==========================================="
echo "✓ INSTALLATION COMPLETE"
echo "==========================================="
echo ""

# Clear WiFi if requested (for production/customer devices)
if [ "$CLEAR_WIFI" = true ]; then
    echo "Clearing WiFi credentials for customer setup..."
    
    # Stop WiFi services
    systemctl stop wpa_supplicant 2>/dev/null || true
    systemctl disable wpa_supplicant 2>/dev/null || true
    systemctl mask wpa_supplicant 2>/dev/null || true
    
    # Remove WiFi configurations
    rm -f /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null || true
    rm -f /etc/wpa_supplicant/wpa_supplicant-wlan0.conf 2>/dev/null || true
    rm -f /boot/firmware/wpa_supplicant.conf 2>/dev/null || true
    
    # Create empty wpa_supplicant.conf
    cat > /etc/wpa_supplicant/wpa_supplicant.conf << 'WPACONF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
WPACONF
    
    echo "✓ WiFi cleared - device ready for customer setup"
    echo ""
    echo "⚠️  IMPORTANT: You will lose SSH access after reboot!"
    echo ""
fi

echo "The system will reboot in 10 seconds."
echo ""

if [ "$CLEAR_WIFI" = true ]; then
    echo "After reboot (NO WiFi):"
    echo "  1. Device will advertise as 'Lumy-Setup' via Bluetooth"
    echo "  2. Open Lumy Desktop app on your Mac"
    echo "  3. Scan for devices and connect"
    echo "  4. Send WiFi credentials via Bluetooth"
    echo "  5. Device will reboot and connect to WiFi"
    echo "  6. Display will show registration code"
else
    echo "After reboot (WiFi preserved):"
    echo "  1. You can still SSH in: ssh $USER@lumy.local"
    echo "  2. Device will also advertise via Bluetooth"
    echo "  3. Test Bluetooth setup with Lumy Desktop app"
    echo "  4. When ready for production, run:"
    echo "     sudo bash scripts/install.sh --clear-wifi"
fi

echo ""
echo "Press Ctrl+C to cancel reboot..."
sleep 10

reboot
