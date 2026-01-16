#!/bin/bash
# Lumy Factory Reset - Prepare device for new customer

set -e

echo "======================================"
echo "  Lumy Factory Reset"
echo "======================================"
echo ""
echo "This will:"
echo "  • Clear the display"
echo "  • Reset device registration"
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

echo "Ensuring service auto-starts on reboot..."
sudo systemctl unmask lumy.service 2>/dev/null || true
sudo systemctl enable lumy.service 2>/dev/null || true

echo "Clearing display..."
cd "$LUMY_DIR/backend"
source venv/bin/activate

python3 << 'CLEAR_DISPLAY'
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
# Backup current .env
if [ -f "$LUMY_DIR/backend/.env" ]; then
    cp "$LUMY_DIR/backend/.env" "$LUMY_DIR/backend/.env.backup"
fi

# Remove device-specific entries
sed -i '/^LUMY_DEVICE_ID=/d' "$LUMY_DIR/backend/.env"
sed -i '/^LUMY_USER_ID=/d' "$LUMY_DIR/backend/.env"

# Add commented placeholders
echo "# LUMY_DEVICE_ID=" >> "$LUMY_DIR/backend/.env"
echo "# LUMY_USER_ID=" >> "$LUMY_DIR/backend/.env"

# Clear logs
rm -f "$LUMY_DIR/backend/lumy.log"

echo "✓ Device registration reset"

echo "Clearing WiFi credentials..."

# Stop any running services
echo "  • Stopping services..."
sudo systemctl stop lumy.service 2>/dev/null || true
sudo systemctl stop lumy-ap 2>/dev/null || true
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Clear ALL saved WiFi networks (this is what we want to delete)
echo "  • Clearing saved WiFi networks..."

# NetworkManager connections
sudo rm -rf /etc/NetworkManager/system-connections/* 2>/dev/null || true

# wpa_supplicant - clear all saved networks
for conf_file in /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf; do
    if [ -f "$conf_file" ]; then
        sudo tee "$conf_file" > /dev/null << 'WPAEOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
WPAEOF
    fi
done

# Clear WiFi state files
sudo rm -rf /var/lib/dhcp/*wlan* 2>/dev/null || true
sudo rm -rf /var/lib/dhcpcd/*wlan* 2>/dev/null || true
sudo rm -rf /var/lib/dhcpcd5/*wlan* 2>/dev/null || true
sudo rm -rf /var/lib/wpa_supplicant/* 2>/dev/null || true
sudo rm -rf /var/lib/NetworkManager/* 2>/dev/null || true

# Remove ImagerSettings (WiFi configured during OS imaging)
sudo rm -f /boot/firstrun.sh 2>/dev/null || true
sudo rm -f /boot/firmware/firstrun.sh 2>/dev/null || true

# CRITICAL: KEEP the dhcpcd AP mode config (DO NOT DELETE IT)
# The AP mode config in /etc/dhcpcd.conf should remain so device can go into AP mode

# Force wlan0 down and restart network
sudo ip link set wlan0 down 2>/dev/null || true
sleep 1
sudo ip link set wlan0 up 2>/dev/null || true

echo "✓ WiFi credentials completely cleared"
echo ""
echo "======================================"
echo "  ✓ Factory Reset Complete"
echo "======================================"
echo ""
echo "Display: Blank/white (ready to ship)"
echo "Service: Stopped"
echo "Registration: Cleared"
echo "WiFi: Cleared (will show AP mode)"
echo ""
echo "📦 READY TO SHIP!"
echo ""
echo "Customer first boot experience:"
echo "  1. Power on device"
echo "  2. Display shows: 'Connect to Lumy-XXXXXX WiFi'"
echo "  3. Customer connects phone to that WiFi"
echo "  4. Browser auto-opens to configure home WiFi"
echo "  5. Display shows: 'Welcome to Lumy' + Registration Code"
echo "  6. Customer visits: https://lumy-beta.vercel.app"
echo "  7. Customer signs in and adds device with code"
echo ""
echo "🔄 Rebooting to complete factory reset..."
echo ""
sleep 2
sudo reboot
