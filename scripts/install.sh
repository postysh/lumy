#!/bin/bash
################################################################################
# Lumy Display Setup Script
# For Raspberry Pi Zero 2 W with Waveshare 7.3inch e-Paper HAT (E)
################################################################################

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    log_error "This script must be run on a Raspberry Pi"
    exit 1
fi

print_header "Lumy Display Setup"
log_info "This script will set up your Raspberry Pi for the Lumy display"

################################################################################
# Step 1: Update system
################################################################################
print_header "Step 1: Updating System"
log_info "Updating package lists..."
apt-get update -y

################################################################################
# Step 2: Install system dependencies
################################################################################
print_header "Step 2: Installing Dependencies"
log_info "Installing required packages..."
apt-get install -y \
    python3-pip \
    python3-pil \
    python3-numpy \
    python3-rpi.gpio \
    python3-spidev \
    git \
    fonts-dejavu \
    fonts-dejavu-extra

log_success "Dependencies installed"

################################################################################
# Step 3: Enable SPI
################################################################################
print_header "Step 3: Enabling SPI Interface"
if ! raspi-config nonint get_spi | grep -q 0; then
    log_info "Enabling SPI..."
    raspi-config nonint do_spi 0
    log_success "SPI enabled"
else
    log_info "SPI already enabled"
fi

################################################################################
# Step 4: Download Waveshare library
################################################################################
print_header "Step 4: Setting Up Waveshare Library"
BACKEND_DIR="/home/pi/lumy"
LIB_DIR="$BACKEND_DIR/lib"

log_info "Creating library directory: $LIB_DIR"
mkdir -p "$LIB_DIR"

log_info "Downloading Waveshare e-paper library..."

# Download only the necessary files (not the entire repo)
BASE_URL="https://raw.githubusercontent.com/waveshare/e-Paper/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd"

# Create waveshare_epd module
mkdir -p "$LIB_DIR/waveshare_epd"

# Download the 7.3inch e-Paper driver and dependencies
wget -q -O "$LIB_DIR/waveshare_epd/__init__.py" "$BASE_URL/__init__.py" || touch "$LIB_DIR/waveshare_epd/__init__.py"
wget -q -O "$LIB_DIR/waveshare_epd/epd7in3e.py" "$BASE_URL/epd7in3e.py"
wget -q -O "$LIB_DIR/waveshare_epd/epdconfig.py" "$BASE_URL/epdconfig.py"

log_success "Waveshare library downloaded (total: ~30KB)"

################################################################################
# Step 5: Install Python dependencies
################################################################################
print_header "Step 5: Installing Python Dependencies"
if [ -f "/home/pi/lumy/backend/requirements.txt" ]; then
    log_info "Installing Python packages..."
    pip3 install -r /home/pi/lumy/backend/requirements.txt --break-system-packages
    log_success "Python packages installed"
else
    log_warning "requirements.txt not found, skipping Python package installation"
fi

################################################################################
# Step 6: Copy backend files
################################################################################
print_header "Step 6: Setting Up Application"
if [ -d "/home/pi/lumy/backend" ]; then
    log_info "Copying backend files to $BACKEND_DIR..."
    cp /home/pi/lumy/backend/*.py "$BACKEND_DIR/" 2>/dev/null || true
    chown -R pi:pi "$BACKEND_DIR"
    log_success "Application files copied"
else
    log_warning "Backend directory not found"
fi

################################################################################
# Step 7: Create systemd service
################################################################################
print_header "Step 7: Creating System Service"
log_info "Creating lumy.service..."

cat > /etc/systemd/system/lumy.service <<EOF
[Unit]
Description=Lumy Display Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$BACKEND_DIR
ExecStart=/usr/bin/python3 $BACKEND_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

log_info "Enabling lumy service..."
systemctl daemon-reload
systemctl enable lumy.service

log_success "Service created and enabled"

################################################################################
# Step 8: Final setup
################################################################################
print_header "Setup Complete!"
echo ""
log_success "Lumy display is ready!"
echo ""
echo "Next steps:"
echo "  1. Copy your backend code to: $BACKEND_DIR"
echo "  2. Start the service: sudo systemctl start lumy"
echo "  3. Check status: sudo systemctl status lumy"
echo "  4. View logs: sudo journalctl -u lumy -f"
echo ""
log_info "A reboot is recommended to ensure all changes take effect"
echo ""
read -p "Reboot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Rebooting..."
    reboot
else
    log_info "Please reboot manually when ready"
fi
