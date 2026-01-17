#!/bin/bash
set -e

echo "==========================================="
echo "Lumy Factory Reset"
echo "Prepare device for customer"
echo "==========================================="
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo bash factory-reset.sh"
    exit 1
fi

echo "⚠️  WARNING: This will:"
echo "  - Clear WiFi credentials"
echo "  - Reset device to BLE setup mode"
echo "  - You will lose SSH access"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds..."
sleep 5

echo ""
echo "Clearing WiFi credentials..."

# Stop WiFi services
systemctl stop wpa_supplicant 2>/dev/null || true
systemctl disable wpa_supplicant 2>/dev/null || true
systemctl mask wpa_supplicant 2>/dev/null || true

# Remove WiFi configurations
rm -f /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null || true
rm -f /etc/wpa_supplicant/wpa_supplicant-wlan0.conf 2>/dev/null || true
rm -f /boot/firmware/wpa_supplicant.conf 2>/dev/null || true
rm -rf /etc/NetworkManager/system-connections/* 2>/dev/null || true

# Create empty wpa_supplicant.conf
cat > /etc/wpa_supplicant/wpa_supplicant.conf << 'WPACONF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
WPACONF

echo "✓ WiFi cleared"

# Ensure BLE service is enabled
echo "Enabling BLE setup service..."
systemctl enable lumy-ble.service

echo "✓ Device ready for customer"
echo ""
echo "Rebooting in 5 seconds..."
echo "After reboot, device will advertise as 'Lumy-Setup' via Bluetooth"
echo ""
sleep 5

reboot
