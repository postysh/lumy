# Lumy

A Bluetooth-controlled E-Paper display system for Raspberry Pi with iPhone integration.

## Overview

Lumy transforms your Waveshare 7.3" E-Paper display into a smart, customizable information dashboard controlled via Bluetooth from your iPhone. Unlike traditional WiFi-based solutions, Lumy uses Bluetooth Low Energy (BLE) for seamless mobile connectivity.

## Features

- 🎨 **Modular Widget System** - Display weather, calendar, notes, images, and more
- 📱 **Bluetooth LE Control** - Direct iPhone connectivity without WiFi dependency
- 🖥️ **Web Dashboard** - Configure and manage your display via browser
- 🔋 **Low Power** - Optimized for Raspberry Pi Zero 2 W
- 🎯 **Extensible** - Easy-to-add custom widgets and apps

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Waveshare 7.3" E-Paper HAT (E) - 1872×1404 resolution
- MicroSD card (16GB+ recommended)
- Power supply for Raspberry Pi

## Project Structure

```
lumy/
├── backend/               # Python backend for Pi
│   ├── src/
│   │   ├── display/      # E-Paper driver and rendering
│   │   ├── bluetooth/    # BLE server implementation
│   │   ├── widgets/      # Widget system
│   │   └── api/          # REST API for web interface
│   ├── requirements.txt
│   └── main.py
├── web/                  # Next.js web dashboard
│   ├── app/
│   ├── components/
│   └── lib/
├── docs/                 # Documentation
├── scripts/              # Setup and utility scripts
└── README.md
```

## Installation

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed setup instructions.

## Quick Start

### On Raspberry Pi

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Web Dashboard

```bash
cd web
npm install
npm run dev
```

## Architecture

- **Backend**: Python 3.9+ with asyncio for concurrent operations
- **Display**: Waveshare e-Paper library with PIL for rendering
- **Bluetooth**: Bleak/BlueZ for BLE server
- **Web**: Next.js 14+ with TypeScript and Tailwind CSS
- **Communication**: JSON-based protocol over BLE GATT characteristics

## License

MIT

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.
