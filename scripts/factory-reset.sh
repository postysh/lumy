#!/bin/bash
# Lumy Factory Reset - Prepare device for new owner

set -e

echo "======================================"
echo "  Lumy Factory Reset"
echo "======================================"
echo ""
echo "This will reset the device to factory settings."
echo "The device will show a new registration code."
echo ""
read -p "Are you sure? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]
then
    echo "Factory reset cancelled."
    exit 1
fi

# Determine lumy directory
if [ -d "$HOME/lumy" ]; then
    LUMY_DIR="$HOME/lumy"
elif [ -d "/home/$SUDO_USER/lumy" ]; then
    LUMY_DIR="/home/$SUDO_USER/lumy"
else
    echo "Error: Cannot find lumy directory"
    exit 1
fi

echo ""
echo "Stopping Lumy service..."
sudo systemctl stop lumy.service

echo "Clearing device registration..."

# Backup current .env
if [ -f "$LUMY_DIR/backend/.env" ]; then
    cp "$LUMY_DIR/backend/.env" "$LUMY_DIR/backend/.env.backup"
    echo "✓ Backed up .env to .env.backup"
fi

# Remove device-specific entries from .env
if [ -f "$LUMY_DIR/backend/.env" ]; then
    # Remove LUMY_DEVICE_ID and LUMY_USER_ID lines
    sed -i '/^LUMY_DEVICE_ID=/d' "$LUMY_DIR/backend/.env"
    sed -i '/^LUMY_USER_ID=/d' "$LUMY_DIR/backend/.env"
    
    # Generate a new unique device ID suffix (so it's different from before)
    NEW_SUFFIX=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1)
    echo "LUMY_DEVICE_ID=lumy-reset-${NEW_SUFFIX}" >> "$LUMY_DIR/backend/.env"
    
    # Add commented placeholder for user ID
    echo "# LUMY_USER_ID=" >> "$LUMY_DIR/backend/.env"
    
    echo "✓ Cleared device registration and generated new device ID"
fi

# Clear logs
rm -f "$LUMY_DIR/backend/lumy.log"
rm -f "$HOME/lumy.log"
echo "✓ Cleared log files"

# Clear the display to force refresh
echo "Clearing display..."
python3 << 'PYTHON_CLEAR'
import sys
sys.path.insert(0, '$LUMY_DIR/backend')
try:
    from waveshare_epd import epd7in3e
    epd = epd7in3e.EPD()
    epd.init()
    epd.Clear()
    epd.sleep()
    print("✓ Display cleared")
except Exception as e:
    print(f"⚠ Could not clear display: {e}")
PYTHON_CLEAR

# Enable service to auto-start on boot, but don't start it now
echo "Enabling Lumy service for auto-start..."
sudo systemctl unmask lumy.service 2>/dev/null || true
sudo systemctl enable lumy.service
echo "✓ Service will auto-start on next boot"

echo ""
echo "======================================"
echo "  ✓ Factory Reset Complete"
echo "======================================"
echo ""
echo "✓ Display cleared (blank/white)"
echo "✓ Device registration removed"
echo "✓ Service configured for first boot"
echo ""
echo "📦 READY TO SHIP!"
echo ""
echo "Customer first-boot experience:"
echo "  1. Power on device"
echo "  2. Display shows: 'WiFi Setup Required'"
echo "  3. Customer connects to 'Lumy-XXXXXX' WiFi"
echo "  4. Browser opens automatically (captive portal)"
echo "  5. Customer selects their WiFi and enters password"
echo "  6. Device reboots automatically"
echo "  7. Display shows: 'Welcome to Lumy' + Registration Code"
echo "  8. Customer visits: https://lumy-beta.vercel.app"
echo "  9. Customer signs in and adds device with code"
echo ""
echo "To test the flow now without shipping:"
echo "  sudo reboot"
echo ""
