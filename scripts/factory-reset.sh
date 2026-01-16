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

# Method 1: Clear wpa_supplicant config
if [ -f /etc/wpa_supplicant/wpa_supplicant.conf ]; then
    sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup
    sudo tee /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << 'WPAEOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
WPAEOF
    echo "  • wpa_supplicant.conf cleared"
fi

# Method 2: Clear NetworkManager connections (if using NetworkManager)
if [ -d /etc/NetworkManager/system-connections ]; then
    sudo rm -f /etc/NetworkManager/system-connections/* 2>/dev/null || true
    sudo systemctl restart NetworkManager 2>/dev/null || true
    echo "  • NetworkManager connections cleared"
fi

# Method 3: Clear dhcpcd persistent config
if [ -f /etc/dhcpcd.conf ]; then
    # Remove any static IP configs for wlan0
    sudo sed -i '/^interface wlan0/,/^$/d' /etc/dhcpcd.conf 2>/dev/null || true
    echo "  • dhcpcd config cleared"
fi

# Method 4: Remove all WiFi-related state files
sudo rm -f /var/lib/dhcp/*.leases 2>/dev/null || true
sudo rm -f /var/lib/dhcpcd/*.lease 2>/dev/null || true
sudo rm -f /var/lib/dhcpcd5/*.lease 2>/dev/null || true
sudo rm -f /var/lib/wpa_supplicant/* 2>/dev/null || true

# Method 5: Force disconnect and forget all networks
sudo rfkill unblock wifi 2>/dev/null || true
sudo ip link set wlan0 down 2>/dev/null || true
sudo wpa_cli -i wlan0 disconnect 2>/dev/null || true
sudo wpa_cli -i wlan0 remove_network all 2>/dev/null || true
sudo wpa_cli -i wlan0 save_config 2>/dev/null || true

echo "✓ WiFi credentials cleared (will need reboot to take effect)"
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
echo "⚠️  IMPORTANT: You must reboot for WiFi changes to take effect!"
echo ""
read -p "Reboot now? (yes/no): " -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Rebooting in 3 seconds..."
    sleep 3
    sudo reboot
else
    echo "To complete factory reset, reboot manually:"
    echo "  sudo reboot"
    echo ""
fi
