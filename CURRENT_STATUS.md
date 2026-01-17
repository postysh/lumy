# Lumy Project - Current Status

## ✅ What's Working

### **Web Dashboard (Deployed on Vercel)**
- ✅ User authentication (Supabase)
- ✅ Device registration system
- ✅ Device management interface
- ✅ Modern UI with shadcn/ui sidebar
- ✅ Live at: https://lumy-beta.vercel.app

### **Raspberry Pi Backend (v3.0 - Clean Restart)**
- ✅ Minimal, proven installation script
- ✅ Waveshare 7.3" e-Paper HAT (E) support
- ✅ BCM2835 library integration
- ✅ Welcome screen with registration code
- ✅ Device ID generation
- ✅ Systemd service for auto-start

---

## 📋 Installation Process

### Current Flow (Working)
```
1. Flash Raspberry Pi OS Lite 64-bit with WiFi
2. SSH into device
3. Run: git clone https://github.com/postysh/lumy.git
4. Run: sudo bash lumy/scripts/install.sh
5. System automatically reboots
6. Display shows: "Welcome to Lumy" with registration code
7. User registers at lumy-beta.vercel.app
8. Device is connected!
```

### What the Installer Does
1. **System Packages**: Installs Python, PIL, NumPy, Git
2. **BCM2835 Library**: Downloads and compiles (required by Waveshare)
3. **SPI Enable**: Enables SPI interface in `/boot/firmware/config.txt`
4. **Waveshare Library**: 
   - Clones official repo: https://github.com/waveshare/e-Paper
   - Installs to: `/usr/local/lib/python3.11/dist-packages/waveshare_epd/`
5. **Backend Dependencies**: FastAPI, Uvicorn, Pydantic, aiohttp, python-dotenv
6. **Display Test**: Runs a test to verify e-Paper is working
7. **Systemd Service**: Creates and enables auto-start service
8. **Reboot**: Automatically reboots to enable SPI

---

## 🎯 What's Next

### Phase 1: Core Functionality (Current)
- [x] Clean installation script
- [x] Display working
- [x] Device registration
- [ ] Connect to web dashboard API
- [ ] Receive configuration from dashboard
- [ ] Display clock widget

### Phase 2: WiFi AP Mode (For Customers)
- [ ] Captive portal for WiFi setup
- [ ] First-boot experience
- [ ] Factory reset script
- [ ] Ship-to-customer ready

### Phase 3: Widget System
- [ ] Clock widget
- [ ] Weather widget
- [ ] Calendar widget
- [ ] Custom widgets via dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Web Dashboard (Vercel)            │
│   - Next.js + Supabase              │
│   - Device management               │
│   - Widget configuration            │
└──────────────┬──────────────────────┘
               │ HTTPS API
┌──────────────┴──────────────────────┐
│   Raspberry Pi Zero 2 W              │
│   ┌──────────────────────────────┐  │
│   │  Lumy Backend (Python)       │  │
│   │  - Device registration       │  │
│   │  - Cloud sync                │  │
│   │  - Widget manager            │  │
│   └──────────┬───────────────────┘  │
│              │                       │
│   ┌──────────┴───────────────────┐  │
│   │  Waveshare 7.3" e-Paper      │  │
│   │  - 800x480 resolution        │  │
│   │  - 7 colors (BWR GYOB)       │  │
│   │  - SPI interface             │  │
│   └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 🔧 Technical Details

### Hardware
- **Board**: Raspberry Pi Zero 2 W
- **Display**: Waveshare 7.3inch e-Paper HAT (E)
  - Resolution: 800x480 pixels
  - Colors: Black, White, Red, Green, Blue, Yellow, Orange
  - Interface: SPI
  - Product: https://www.waveshare.com/7.3inch-e-paper-hat-e.htm

### Software Stack
- **OS**: Raspberry Pi OS Lite 64-bit (Bookworm)
- **Backend**: Python 3.11
- **Display Library**: Waveshare official e-Paper library
- **GPIO Library**: BCM2835 (C library)
- **Web Framework**: FastAPI (for future API endpoints)
- **Image Processing**: Pillow (PIL)

### File Structure
```
lumy/
├── backend/
│   └── main.py              # Main application
├── scripts/
│   └── install.sh           # Installation script
├── web/                     # Next.js dashboard (separate deployment)
├── INSTALL.md               # Installation guide
└── CURRENT_STATUS.md        # This file
```

---

## 📝 Key Design Decisions

### Why BCM2835 Library?
- Required by official Waveshare library
- Direct hardware access for SPI
- Proven, stable, well-documented
- Reference: http://www.airspayce.com/mikem/bcm2835/

### Why System Packages Instead of Virtual Environment?
- Raspberry Pi Zero 2 W is resource-constrained
- System packages are pre-compiled for ARM64
- Faster installation
- Less disk space
- Using `--break-system-packages` flag (modern Python 3.11+ requirement)

### Why Minimal Approach?
- Previous attempts failed due to complexity
- Prove each layer works before adding next
- Easier to debug
- Reference: [Waveshare Manual](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual)

---

## 🚀 Testing

### Test on Fresh Device
```bash
# 1. Flash Raspberry Pi OS Lite 64-bit
# 2. Configure WiFi in Imager
# 3. Enable SSH in Imager
# 4. Boot and SSH in
# 5. Run:
cd ~
git clone https://github.com/postysh/lumy.git
cd lumy
sudo bash scripts/install.sh

# 6. Wait for installation and automatic reboot
# 7. After reboot, check display shows welcome screen
# 8. Register device at lumy-beta.vercel.app
```

### Verify Installation
```bash
# Check service status
sudo systemctl status lumy

# View logs
sudo journalctl -u lumy -f

# Check display library
python3 -c "import sys; sys.path.append('/usr/local/lib/python3.11/dist-packages'); from waveshare_epd import epd7in3e; print('OK')"
```

---

## 🛠️ Troubleshooting

### Common Issues
1. **Display blank after reboot**
   - Check if SPI is enabled: `lsmod | grep spi`
   - Run: `sudo raspi-config` -> Interface Options -> SPI -> Enable

2. **Service won't start**
   - Check logs: `sudo journalctl -u lumy -n 50`
   - Check Python path in service file

3. **Library not found**
   - Verify: `ls /usr/local/lib/python3.11/dist-packages/waveshare_epd/`
   - Reinstall from: `/tmp/e-Paper/RaspberryPi_JetsonNano/python/`

---

## 📚 References

- [Waveshare 7.3" e-Paper Manual](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual)
- [Waveshare GitHub](https://github.com/waveshare/e-Paper)
- [BCM2835 Library](http://www.airspayce.com/mikem/bcm2835/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)

---

**Last Updated**: January 17, 2026
**Version**: 3.0 (Clean Restart)
