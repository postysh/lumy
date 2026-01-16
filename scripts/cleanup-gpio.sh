#!/bin/bash
# Cleanup GPIO pins that may be stuck in use

echo "GPIO Cleanup Script"
echo "==================="
echo ""

# Kill ANY Python processes
echo "Killing all Python processes..."
sudo pkill -9 python3 2>/dev/null || true
sudo pkill -9 python 2>/dev/null || true
sleep 1
echo "✓ Python processes killed"

# Force release GPIO chip
echo ""
echo "Releasing GPIO chip..."
if [ -e /dev/gpiochip0 ]; then
    # Try to reset the GPIO chip
    sudo python3 -c "
try:
    from waveshare_epd import epdconfig
    epdconfig.module_exit()
    print('✓ GPIO released via epdconfig')
except:
    pass
" 2>/dev/null || true
fi

echo "✓ GPIO cleanup complete"
echo ""
echo "You can now run your script"
