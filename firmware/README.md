# Lumy Firmware

Custom firmware for Lumy e-ink display devices.

## Hardware Support

### Currently Testing:
- **Waveshare ESP32-C6 1.47" LCD Display** (Development board)
  - ESP32-C6 RISC-V processor (160MHz)
  - 1.47" LCD (172×320, ST7789 driver)
  - WiFi 6 + Bluetooth 5
  - USB-C programming

### Production Target:
- **XIAO ESP32-S3 + 7.3" E-Paper Display**
  - ESP32-S3 (240MHz dual-core)
  - 7.3" Waveshare E-Paper (800×480, 7-color)
  - WiFi + Bluetooth
  - Battery powered

## Development Setup

### Requirements:
- VS Code
- PlatformIO extension
- USB-C cable

### Installation:

1. **Install VS Code:**
   ```bash
   # Download from https://code.visualstudio.com
   ```

2. **Install PlatformIO:**
   - Open VS Code
   - Go to Extensions (⌘⇧X)
   - Search "PlatformIO IDE"
   - Click Install

3. **Open Project:**
   ```bash
   cd /Users/evan/Desktop/lumy/firmware
   code .
   ```

4. **Build & Upload:**
   - Click PlatformIO icon in sidebar
   - Click "Upload" under esp32c6

## Firmware Architecture

```
firmware/
├── platformio.ini       # Build configuration
├── src/
│   └── main.cpp        # Main firmware
├── include/            # Header files
└── lib/                # Custom libraries
```

## Features

### Phase 1: Basic Testing (Current)
- [x] Serial communication
- [x] Backlight control
- [ ] LCD display test
- [ ] WiFi connection test

### Phase 2: WiFi Provisioning
- [ ] Captive portal setup
- [ ] Save WiFi credentials to flash
- [ ] Auto-connect on boot

### Phase 3: Registration Flow
- [ ] Generate registration code
- [ ] Display code on screen
- [ ] Poll API for registration
- [ ] Save device ID and API key

### Phase 4: Display Updates
- [ ] Fetch content from Vercel API
- [ ] Render images on display
- [ ] Auto-refresh on interval
- [ ] Battery monitoring

## API Integration

Connects to: `https://lumy-beta.vercel.app`

### Endpoints:
- `GET /api/devices/check-registration?code=ABC123`
- `GET /api/devices/{id}/display`
- `GET /api/devices/{id}/status`

## License

Proprietary - Lumy Project
© 2026 Evan
