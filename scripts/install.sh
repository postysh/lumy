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

# Enable Bluetooth
systemctl enable bluetooth
systemctl start bluetooth

# Make Bluetooth discoverable
hciconfig hci0 piscan

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

[Service]
Type=simple
User=root
WorkingDirectory=/home/$USER/lumy/backend
ExecStart=/usr/bin/python3 ble_server.py
Restart=on-failure
RestartSec=5

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
echo "The system will reboot in 10 seconds."
echo ""
echo "After reboot:"
echo "  1. Device will advertise as 'Lumy-Setup' via Bluetooth"
echo "  2. Open the Lumy Desktop app on your Mac"
echo "  3. Scan for devices and connect"
echo "  4. Send WiFi credentials"
echo "  5. Device will reboot and show registration code"
echo ""
echo "Press Ctrl+C to cancel reboot..."
sleep 10

reboot
