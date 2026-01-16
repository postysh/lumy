#!/bin/bash
# Enable SPI interface on Raspberry Pi

echo "Enabling SPI Interface"
echo "====================="
echo ""

# Enable SPI using raspi-config
echo "Enabling SPI..."
sudo raspi-config nonint do_spi 0

# Verify SPI is enabled
echo ""
echo "Checking SPI status..."
if lsmod | grep -q spi_bcm2835; then
    echo "✓ SPI module is loaded"
else
    echo "⚠ SPI module not loaded yet"
fi

if [ -e /dev/spidev0.0 ]; then
    echo "✓ SPI device exists: /dev/spidev0.0"
else
    echo "✗ SPI device not found: /dev/spidev0.0"
    echo ""
    echo "A reboot is required to activate SPI."
    echo ""
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Rebooting..."
        sudo reboot
    else
        echo ""
        echo "Please reboot manually to complete SPI setup:"
        echo "  sudo reboot"
    fi
fi

echo ""
echo "SPI setup complete!"
