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

# STEP 1: Stop and disable ALL WiFi client services
echo "  • Stopping WiFi services..."
sudo systemctl stop wpa_supplicant 2>/dev/null || true
sudo systemctl disable wpa_supplicant 2>/dev/null || true
sudo systemctl stop NetworkManager 2>/dev/null || true
sudo systemctl disable NetworkManager 2>/dev/null || true

# Kill any running wpa_supplicant processes
sudo pkill -9 wpa_supplicant 2>/dev/null || true
sudo pkill -9 NetworkManager 2>/dev/null || true

# STEP 2: Disconnect wlan0 completely
echo "  • Disconnecting wlan0..."
sudo ip link set wlan0 down 2>/dev/null || true
sudo ip addr flush dev wlan0 2>/dev/null || true

# STEP 3: Clear ALL WiFi configuration files
echo "  • Clearing WiFi configs..."

# Clear wpa_supplicant - COMPLETELY
for conf_file in /etc/wpa_supplicant/*.conf; do
    if [ -f "$conf_file" ]; then
        sudo rm -f "$conf_file"
    fi
done

# Recreate minimal wpa_supplicant.conf
sudo tee /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << 'WPAEOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
WPAEOF

# Clear NetworkManager connections
sudo rm -rf /etc/NetworkManager/system-connections/* 2>/dev/null || true

# STEP 4: Clear ALL WiFi state and lease files
echo "  • Clearing WiFi state files..."
sudo rm -rf /var/lib/dhcp/* 2>/dev/null || true
sudo rm -rf /var/lib/dhcpcd/* 2>/dev/null || true
sudo rm -rf /var/lib/dhcpcd5/* 2>/dev/null || true
sudo rm -rf /var/lib/wpa_supplicant/* 2>/dev/null || true
sudo rm -rf /var/lib/NetworkManager/* 2>/dev/null || true

# STEP 5: Remove Imager-configured WiFi
sudo rm -f /boot/firstrun.sh 2>/dev/null || true
sudo rm -f /boot/firmware/firstrun.sh 2>/dev/null || true
sudo rm -f /boot/firmware/wpa_supplicant.conf 2>/dev/null || true

# STEP 6: Restart dhcpcd to apply AP mode config
echo "  • Restarting dhcpcd for AP mode..."
sudo systemctl restart dhcpcd 2>/dev/null || true

# STEP 7: Enable AP mode services
echo "  • Enabling AP mode services..."
sudo systemctl enable hostapd 2>/dev/null || true
sudo systemctl enable dnsmasq 2>/dev/null || true

echo "✓ WiFi completely cleared - AP mode will start on reboot"
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
