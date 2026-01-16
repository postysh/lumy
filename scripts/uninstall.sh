#!/bin/bash
# Lumy Uninstall Script - Complete removal

set -e

echo "======================================"
echo "  Lumy Uninstall Script"
echo "======================================"
echo ""
echo "This will completely remove Lumy from your system."
read -p "Are you sure? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]
then
    echo "Uninstall cancelled."
    exit 1
fi

echo ""
echo "Stopping Lumy service..."
sudo systemctl stop lumy.service 2>/dev/null || true
sudo systemctl disable lumy.service 2>/dev/null || true

echo "Removing systemd service..."
sudo rm -f /etc/systemd/system/lumy.service
sudo systemctl daemon-reload

echo "Stopping any running Lumy processes..."
sudo pkill -f "python3.*lumy" || true
sudo pkill -f "python3 main.py" || true

echo "Removing Lumy directory..."
rm -rf ~/lumy

echo "Cleaning up GPIO..."
sudo bash -c 'for pin in /sys/class/gpio/gpio*/; do echo $(basename $pin | sed "s/gpio//") > /sys/class/gpio/unexport 2>/dev/null || true; done'

echo "Removing log files..."
rm -f ~/lumy.log

echo ""
echo "======================================"
echo "  ✓ Lumy Uninstalled Successfully"
echo "======================================"
echo ""
echo "Your Raspberry Pi is now clean."
echo ""
echo "To reinstall Lumy:"
echo "  cd ~"
echo "  git clone https://github.com/postysh/lumy.git"
echo "  cd lumy"
echo "  sudo bash scripts/install.sh"
echo ""
