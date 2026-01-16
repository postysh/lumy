# Lumy - Project Overview

## What is Lumy?

Lumy is a **Bluetooth-controlled E-Paper display system** designed for Raspberry Pi Zero 2 W with the Waveshare 7.3" E-Paper HAT (E). Unlike traditional WiFi-based solutions, Lumy uses **Bluetooth Low Energy (BLE)** for direct iPhone connectivity, making it perfect for personal information displays, smart home dashboards, and IoT projects.

## Key Features

### 🎨 **Modular Widget System**
- Pre-built widgets: Clock, Weather, Calendar
- Easy-to-extend architecture
- Hot-reloadable widget code
- Customizable layouts

### 📱 **iPhone Control via Bluetooth**
- Direct BLE connection (no WiFi needed)
- Low power consumption
- Secure pairing
- JSON-based command protocol
- Future iOS app support

### 🖥️ **Modern Web Dashboard**
- Beautiful Next.js interface with dark theme
- Real-time status monitoring
- Quick action buttons
- Widget management
- Configuration editor

### 🔋 **Power Efficient**
- E-Paper display only uses power during refresh
- Automatic sleep mode
- Configurable refresh intervals
- Optimized for battery/solar operation

### 🛠️ **Developer Friendly**
- Clean Python architecture
- Well-documented API
- TypeScript web frontend
- Comprehensive guides
- Easy widget development

## Architecture

```
┌─────────────────┐
│  iPhone App     │ (Future)
│  (BLE Client)   │
└────────┬────────┘
         │ Bluetooth LE
         │
┌────────▼────────────────────────────────────┐
│  Raspberry Pi Zero 2 W                      │
│  ┌──────────────────────────────────────┐  │
│  │  Lumy Backend (Python)               │  │
│  │  ┌────────────┐  ┌────────────────┐  │  │
│  │  │ BLE Server │  │ Display Manager│  │  │
│  │  └────────────┘  └────────────────┘  │  │
│  │  ┌────────────┐  ┌────────────────┐  │  │
│  │  │ API Server │  │ Widget Manager │  │  │
│  │  └────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Waveshare 7.3" E-Paper HAT (E)     │  │
│  │  1872×1404 pixels, 7 colors         │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│  Web Dashboard  │
│  (Next.js)      │
│  Browser/iPhone │
└─────────────────┘
```

## Project Structure

```
lumy/
├── backend/              # Python backend
│   ├── main.py          # Entry point
│   ├── config.yaml      # Configuration
│   ├── requirements.txt # Python dependencies
│   └── src/
│       ├── display/     # E-Paper driver
│       ├── bluetooth/   # BLE server
│       ├── widgets/     # Widget system
│       │   ├── base_widget.py
│       │   └── implementations/
│       │       ├── clock_widget.py
│       │       ├── weather_widget.py
│       │       └── calendar_widget.py
│       └── api/         # REST API
│
├── web/                 # Next.js dashboard
│   ├── app/            # Pages
│   ├── components/     # React components
│   └── lib/            # Utilities & API client
│
├── scripts/            # Setup scripts
│   ├── install.sh      # Main installer
│   ├── setup-bluetooth.sh
│   └── test-display.py
│
└── docs/               # Documentation
    ├── QUICK_START.md
    ├── INSTALLATION.md
    └── BLUETOOTH_PROTOCOL.md
```

## Technology Stack

### Backend
- **Python 3.9+** - Core language
- **FastAPI** - REST API framework
- **Bleak/BlueZ** - Bluetooth LE
- **Pillow (PIL)** - Image processing
- **Waveshare e-Paper library** - Display driver
- **asyncio** - Concurrent operations

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **TanStack Query** - Data fetching
- **Axios** - HTTP client
- **Zustand** - State management (future)

### Hardware
- **Raspberry Pi Zero 2 W** - Quad-core ARM Cortex-A53
- **Waveshare 7.3" E-Paper HAT (E)** - epd7in3e
  - Resolution: 1872×1404 pixels
  - Colors: 7 (Black, White, Red, Green, Blue, Yellow, Orange)
  - Interface: SPI

## Quick Start

### 1. Installation
```bash
cd ~/lumy
./scripts/install.sh
```

### 2. Test Display
```bash
python3 scripts/test-display.py
```

### 3. Start Lumy
```bash
sudo systemctl start lumy
```

### 4. Access Dashboard
```
http://YOUR_PI_IP:8000
```

See [docs/QUICK_START.md](docs/QUICK_START.md) for detailed instructions.

## Widget Development

Creating a new widget is simple:

```python
from src.widgets.base_widget import BaseWidget
from PIL import Image, ImageDraw

class MyWidget(BaseWidget):
    def __init__(self, config):
        super().__init__(config, 'my_widget')
    
    async def initialize(self):
        self.data = {'message': 'Hello World'}
    
    async def update(self):
        # Update widget data
        pass
    
    async def render(self, width: int, height: int) -> Image.Image:
        canvas = self.create_canvas(width, height)
        draw = ImageDraw.Draw(canvas)
        draw.text((20, 20), self.data['message'], fill=(0, 0, 0))
        return canvas
```

Save as `backend/src/widgets/implementations/my_widget.py` and add to `config.yaml`.

## API Endpoints

### Status
- `GET /status` - System status
- `GET /config` - Get configuration
- `POST /config` - Update configuration

### Display
- `POST /display/refresh` - Refresh display
- `POST /display/clear` - Clear display

### Widgets
- `GET /widgets` - List widgets
- `POST /widgets/{id}/update` - Update widget
- `POST /widgets/{id}/trigger` - Trigger action

### WebSocket
- `WS /ws` - Real-time updates

## Bluetooth Commands

All commands use JSON format:

```json
{
  "command": "refresh_display",
  "data": {},
  "request_id": "123"
}
```

Available commands:
- `ping` - Check connectivity
- `refresh_display` - Update screen
- `clear_display` - Clear screen
- `update_widget` - Update widget data
- `get_status` - Get system info
- `set_config` - Change settings

See [docs/BLUETOOTH_PROTOCOL.md](docs/BLUETOOTH_PROTOCOL.md) for full protocol.

## Configuration

Edit `backend/config.yaml`:

```yaml
display:
  refresh_interval: 300  # Seconds
  sleep_after_refresh: true

bluetooth:
  enabled: true
  device_name: "Lumy Display"

widgets:
  default_widgets:
    - clock
    - weather
    - calendar
  
  weather:
    api_key: "YOUR_API_KEY"
    location: "Your City"
```

## Roadmap

### Version 1.0 (Current) ✅
- [x] Core display system
- [x] BLE server implementation
- [x] Basic widgets (clock, weather, calendar)
- [x] Web dashboard
- [x] Setup automation

### Version 1.1 (Planned)
- [ ] Native iOS app
- [ ] More widgets (news, stocks, photos)
- [ ] Custom fonts
- [ ] Image upload via Bluetooth
- [ ] Widget marketplace

### Version 2.0 (Future)
- [ ] Multiple display support
- [ ] Cloud sync
- [ ] Voice control integration
- [ ] Solar power optimization
- [ ] Community widget repository

## Use Cases

- **Personal Dashboard** - Time, weather, calendar at a glance
- **Smart Home Control** - Status display for IoT devices
- **Digital Signage** - Low-power information display
- **Art Display** - Rotating digital art with no screen burn
- **Notification Center** - Important alerts and reminders
- **Meeting Room Display** - Schedule and availability
- **E-Reader** - Display books, articles, PDFs

## Performance

- **Refresh Time:** ~15 seconds (full screen)
- **Power Consumption:** <0.5W average (with sleep)
- **Bluetooth Range:** ~10 meters
- **Display Lifetime:** 1,000,000+ refreshes
- **Boot Time:** ~30 seconds

## Contributing

Contributions welcome! Areas for contribution:
- New widgets
- iOS app development
- Documentation improvements
- Bug fixes
- Performance optimizations

## Support

- **Documentation:** [/docs](/docs)
- **Issues:** GitHub Issues
- **Waveshare Docs:** [E-Paper HAT Manual](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(E)_Manual)

## License

MIT License - see [LICENSE](LICENSE)

## Credits

- **Inspired by:** [InkyPi](https://github.com/fatihak/InkyPi)
- **E-Paper Library:** [Waveshare](https://github.com/waveshare/e-Paper)
- **Built with:** Python, Next.js, and lots of ☕

## Author

Created with ❤️ for the maker community

---

**Ready to get started?** See [docs/QUICK_START.md](docs/QUICK_START.md)!
