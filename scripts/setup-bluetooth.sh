#!/bin/bash
# Setup Bluetooth for Lumy

echo "Setting up Bluetooth for Lumy..."

# Enable Bluetooth
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER

# Configure BlueZ for BLE
sudo tee /etc/bluetooth/main.conf > /dev/null <<EOF
[General]
Name = Lumy Display
Class = 0x000100
DiscoverableTimeout = 0
PairableTimeout = 0
Discoverable = yes
Pairable = yes

[LE]
MinConnectionInterval=7.5
MaxConnectionInterval=15
ConnectionLatency=0
ConnectionSupervisionTimeout=5000
EOF

# Restart Bluetooth service
sudo systemctl restart bluetooth

echo "Bluetooth setup complete!"
echo "Device should be discoverable as 'Lumy Display'"
