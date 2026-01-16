#!/bin/bash
# Setup WiFi Access Point Mode for Lumy

set -e

echo "========================================="
echo "  Setting up WiFi AP Mode"
echo "========================================="

# Install required packages
echo "Installing AP mode packages..."
sudo apt-get install -y hostapd dnsmasq

# Stop services during configuration
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Configure hostapd
echo "Configuring hostapd..."
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

# Tell hostapd where to find config
sudo tee /etc/default/hostapd > /dev/null <<'EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Backup dnsmasq.conf
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true

# Configure dnsmasq
echo "Configuring dnsmasq..."
sudo tee /etc/dnsmasq.conf > /dev/null <<'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
EOF

# Create AP mode network configuration
echo "Configuring network for AP mode..."
sudo tee /etc/network/interfaces.d/ap-mode > /dev/null <<'EOF'
auto wlan0
iface wlan0 inet static
    address 192.168.4.1
    netmask 255.255.255.0
    network 192.168.4.0
    broadcast 192.168.4.255
EOF

# Create systemd service for AP mode
echo "Creating AP mode systemd service..."
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

# Create captive portal service
echo "Creating captive portal service..."

# Determine lumy directory
if [ -d "$HOME/lumy" ]; then
    LUMY_DIR="$HOME/lumy"
elif [ -d "/home/$SUDO_USER/lumy" ]; then
    LUMY_DIR="/home/$SUDO_USER/lumy"
else
    LUMY_DIR="/home/lumy/lumy"
fi

ACTUAL_USER="${SUDO_USER:-$USER}"

sudo tee /etc/systemd/system/lumy-captive-portal.service > /dev/null <<EOF
[Unit]
Description=Lumy Captive Portal
After=lumy-ap.service
Requires=lumy-ap.service

[Service]
Type=simple
User=root
WorkingDirectory=$LUMY_DIR/backend/src
Environment="PYTHONPATH=$LUMY_DIR/backend"
ExecStart=/usr/bin/python3 $LUMY_DIR/backend/src/captive_portal.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Don't enable services by default (only start them when needed)
sudo systemctl disable hostapd 2>/dev/null || true
sudo systemctl disable dnsmasq 2>/dev/null || true

echo "✓ AP mode setup complete"
echo ""
echo "AP mode will automatically start when no WiFi is detected."
