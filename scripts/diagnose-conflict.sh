#!/bin/bash
# Check for InkyPi or other e-paper software conflicts

echo "Lumy Conflict Diagnostic"
echo "========================"
echo ""

# Check if InkyPi is installed
echo "Checking for InkyPi installation..."
if [ -d "/home/$USER/InkyPi" ] || [ -d "~/InkyPi" ]; then
    echo "⚠ InkyPi directory found"
    ls -la ~/InkyPi 2>/dev/null || ls -la /home/$USER/InkyPi 2>/dev/null
    echo ""
    echo "InkyPi service might be running and holding the display!"
fi

# Check for InkyPi service
echo ""
echo "Checking for InkyPi service..."
if systemctl list-units --full --all | grep -i inkypi; then
    echo "⚠ InkyPi service found!"
    systemctl status inkypi* 2>/dev/null || true
    echo ""
    echo "To stop InkyPi service:"
    echo "  sudo systemctl stop inkypi"
    echo "  sudo systemctl disable inkypi"
else
    echo "✓ No InkyPi service found"
fi

# Check for running Python processes
echo ""
echo "Checking for running e-paper processes..."
if ps aux | grep -i "[i]nky\|[e]pd\|[e]-paper" | grep -v grep; then
    echo "⚠ Found running processes!"
    echo ""
    echo "To kill them:"
    echo "  sudo pkill -f inky"
    echo "  sudo pkill -f epd"
else
    echo "✓ No conflicting processes found"
fi

# Check Python packages
echo ""
echo "Checking Python packages..."
python3 -c "import inky" 2>/dev/null && echo "⚠ 'inky' package installed (Pimoroni library)" || echo "✓ No 'inky' package"
python3 -c "import waveshare_epd" 2>/dev/null && echo "✓ 'waveshare_epd' package installed" || echo "✗ 'waveshare_epd' NOT installed!"

# Check GPIO ownership
echo ""
echo "Checking GPIO state..."
sudo gpioinfo | grep -A1 "line  17" || echo "GPIO info not available"

echo ""
echo "========================"
echo "Recommendation:"
echo ""
echo "If InkyPi is installed and running, it's holding the display!"
echo "To fix:"
echo "  1. Stop InkyPi: sudo systemctl stop inkypi"
echo "  2. Disable InkyPi: sudo systemctl disable inkypi"
echo "  3. Reboot: sudo reboot"
echo "  4. Then try Lumy again"
echo ""
