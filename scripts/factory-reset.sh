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

deactivate

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
echo ""
echo "======================================"
echo "  ✓ Factory Reset Complete"
echo "======================================"
echo ""
echo "Display: Blank/white (ready to ship)"
echo "Service: Stopped"
echo "Registration: Cleared"
echo ""
echo "📦 READY TO SHIP!"
echo ""
echo "Customer first boot experience:"
echo "  1. Power on device"
echo "  2. Display shows: 'Welcome to Lumy' + Registration Code"
echo "  3. Customer visits: https://lumy-beta.vercel.app"
echo "  4. Customer signs in and adds device with code"
echo ""
echo "To test now without shipping:"
echo "  sudo reboot"
echo ""
