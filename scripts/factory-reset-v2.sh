#!/bin/bash
# Lumy Factory Reset v2 - Prepare device for new customer

set -e

echo "======================================"
echo "  Lumy Factory Reset v2"
echo "======================================"
echo ""
echo "This will:"
echo "  • Clear the display"
echo "  • Reset device registration"
echo "  • Clear WiFi credentials"
echo "  • Prepare device for shipping"
echo ""
read -p "Continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Factory reset cancelled."
    exit 1
fi

# Find lumy directory
if [ -d "$HOME/lumy" ]; then
    LUMY_DIR="$HOME/lumy"
elif [ -d "/home/$SUDO_USER/lumy" ]; then
    LUMY_DIR="/home/$SUDO_USER/lumy"
elif [ -d "/home/lumy/lumy" ]; then
    LUMY_DIR="/home/lumy/lumy"
else
    echo "Error: Cannot find lumy directory"
    exit 1
fi

echo ""
echo "Stopping Lumy service..."
sudo systemctl stop lumy.service

echo "Clearing display..."
cd "$LUMY_DIR/backend"
source venv/bin/activate

sudo "$LUMY_DIR/backend/venv/bin/python3" << 'CLEAR_DISPLAY'
import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'

try:
    from waveshare_epd import epd7in3e
    print("  • Initializing display...")
    epd = epd7in3e.EPD()
    epd.init()
    print("  • Clearing...")
    epd.Clear()
    epd.sleep()
    print("  ✓ Display cleared (blank/white)")
except Exception as e:
    print(f"  ⚠ Could not clear display: {e}")
CLEAR_DISPLAY

echo "Resetting device registration..."
# Remove device-specific entries from .env
if [ -f "$LUMY_DIR/backend/.env" ]; then
    cp "$LUMY_DIR/backend/.env" "$LUMY_DIR/backend/.env.backup"
    sed -i '/^LUMY_DEVICE_ID=/d' "$LUMY_DIR/backend/.env"
    sed -i '/^LUMY_USER_ID=/d' "$LUMY_DIR/backend/.env"
    echo "# LUMY_DEVICE_ID=" >> "$LUMY_DIR/backend/.env"
    echo "# LUMY_USER_ID=" >> "$LUMY_DIR/backend/.env"
fi

# Clear logs
rm -f "$LUMY_DIR/backend/lumy.log"

echo "✓ Device registration reset"

echo "Clearing WiFi credentials..."

# Clear wpa_supplicant - remove all saved networks
for conf_file in /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf; do
    if [ -f "$conf_file" ]; then
        sudo tee "$conf_file" > /dev/null << 'WPAEOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
WPAEOF
    fi
done

# Clear NetworkManager connections
sudo rm -rf /etc/NetworkManager/system-connections/* 2>/dev/null || true

# Clear WiFi state files
sudo rm -rf /var/lib/dhcp/*wlan* 2>/dev/null || true
sudo rm -rf /var/lib/dhcpcd/*wlan* 2>/dev/null || true
sudo rm -rf /var/lib/dhcpcd5/*wlan* 2>/dev/null || true
sudo rm -rf /var/lib/wpa_supplicant/* 2>/dev/null || true
sudo rm -rf /var/lib/NetworkManager/* 2>/dev/null || true

# Remove Imager-configured WiFi
sudo rm -f /boot/firstrun.sh 2>/dev/null || true
sudo rm -f /boot/firmware/firstrun.sh 2>/dev/null || true

# IMPORTANT: Keep /etc/dhcpcd.conf AP mode config intact
# This is what allows the device to go into AP mode

echo "✓ WiFi credentials cleared (AP mode config preserved)"
echo ""
echo "======================================"
echo "  ✓ Factory Reset Complete"
echo "======================================"
echo ""
echo "Display: Blank/white (ready to ship)"
echo "Registration: Cleared"
echo "WiFi: Cleared (will auto-start AP mode)"
echo ""
echo "📦 READY TO SHIP!"
echo ""
echo "Customer first boot experience:"
echo "  1. Power on device"
echo "  2. Display shows: 'WiFi Setup Required'"
echo "  3. Customer connects to: Lumy-XXXXXX"
echo "  4. Browser opens to: http://192.168.4.1"
echo "  5. Customer configures WiFi"
echo "  6. Display shows: 'Welcome to Lumy' + Registration Code"
echo "  7. Customer visits: https://lumy-beta.vercel.app"
echo "  8. Customer registers device with code"
echo ""
echo "🔄 Rebooting to complete factory reset..."
echo ""
sleep 2
sudo reboot
