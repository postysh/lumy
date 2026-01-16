#!/bin/bash
# Hardware diagnostic script for Lumy E-Paper display

echo "Lumy Hardware Diagnostic"
echo "========================"
echo ""

# Check SPI
echo "Checking SPI interface..."
if [ -e /dev/spidev0.0 ]; then
    echo "✓ SPI device exists: /dev/spidev0.0"
    ls -l /dev/spidev0.0
else
    echo "✗ SPI device not found"
    echo "  Run: sudo bash scripts/enable-spi.sh"
fi

# Check if SPI module is loaded
echo ""
echo "Checking SPI kernel module..."
if lsmod | grep -q spi_bcm2835; then
    echo "✓ SPI kernel module loaded"
else
    echo "✗ SPI kernel module not loaded"
fi

# Check GPIO
echo ""
echo "Checking GPIO access..."
if [ -e /dev/gpiochip0 ]; then
    echo "✓ GPIO device exists: /dev/gpiochip0"
    ls -l /dev/gpiochip0
else
    echo "✗ GPIO device not found"
fi

# Check Python packages
echo ""
echo "Checking Python packages..."
python3 -c "import RPi.GPIO; print('✓ RPi.GPIO installed')" 2>/dev/null || echo "✗ RPi.GPIO not installed"
python3 -c "import spidev; print('✓ spidev installed')" 2>/dev/null || echo "✗ spidev not installed"
python3 -c "import PIL; print('✓ Pillow installed')" 2>/dev/null || echo "✗ Pillow not installed"
python3 -c "import waveshare_epd.epd7in3e; print('✓ Waveshare EPD library installed')" 2>/dev/null || echo "✗ Waveshare EPD library not installed"

# Check for GPIO conflicts
echo ""
echo "Checking for GPIO conflicts..."
PYTHON_PIDS=$(pgrep -f "python.*epd\|python.*lumy")
if [ -n "$PYTHON_PIDS" ]; then
    echo "⚠ Found Python processes that may be using GPIO:"
    ps -p $PYTHON_PIDS -o pid,cmd
    echo ""
    echo "To kill them, run: sudo bash scripts/cleanup-gpio.sh"
else
    echo "✓ No GPIO conflicts detected"
fi

# Check user permissions
echo ""
echo "Checking user permissions..."
if groups | grep -q "gpio"; then
    echo "✓ User is in 'gpio' group"
else
    echo "⚠ User is NOT in 'gpio' group"
    echo "  Run: sudo usermod -a -G gpio $USER"
    echo "  Then logout and login again"
fi

if groups | grep -q "spi"; then
    echo "✓ User is in 'spi' group"
else
    echo "⚠ User is NOT in 'spi' group"
    echo "  Run: sudo usermod -a -G spi $USER"
    echo "  Then logout and login again"
fi

echo ""
echo "========================"
echo "Diagnostic complete!"
echo ""
echo "Hardware checklist:"
echo "1. Is the E-Paper HAT properly seated on the GPIO pins?"
echo "2. Is the display cable connected to the HAT?"
echo "3. Is the display powered on?"
echo ""
