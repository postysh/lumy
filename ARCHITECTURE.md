# Lumy Hybrid Architecture

## Overview

Lumy uses a hybrid cloud + local architecture for maximum flexibility and reliability.

```
┌─────────────┐
│   iPhone    │
│   (BLE)     │
└──────┬──────┘
       │ Bluetooth
       │ (Local Control)
       ▼
┌─────────────────────┐         HTTPS          ┌──────────────────┐
│  Raspberry Pi       │◄──────────────────────►│  Vercel (Cloud)  │
│  - Python Backend   │  Polling/Updates       │  - Next.js       │
│  - Widget Manager   │                        │  - API           │
│  - E-Paper Display  │                        │  - Dashboard     │
│  - BLE Server       │                        │  - Database      │
└─────────────────────┘                        └──────────────────┘
```

## Communication Flows

### 1. Cloud Control (Vercel → Pi)
- Pi polls Vercel API every 60 seconds
- Fetches: widget config, display settings, scheduled updates
- Vercel stores: device state, user preferences, schedules

### 2. Local Control (iPhone → Pi)
- iPhone connects via Bluetooth LE
- Direct commands: refresh, update widget, change settings
- No internet required - works offline
- Instant response (no cloud latency)

### 3. Status Reporting (Pi → Vercel)
- Pi sends status updates to Vercel
- Reports: online/offline, last refresh, widget status, errors
- Enables remote monitoring in web dashboard

## API Contract

### Pi → Vercel Endpoints

#### GET `/api/devices/{device_id}/config`
Fetch device configuration from cloud.

Response:
```json
{
  "device_id": "lumy-001",
  "display": {
    "width": 800,
    "height": 480,
    "refresh_interval": 300
  },
  "widgets": [
    {
      "id": "clock",
      "enabled": true,
      "config": {}
    },
    {
      "id": "weather",
      "enabled": true,
      "config": {
        "api_key": "...",
        "location": "New York"
      }
    }
  ],
  "updated_at": "2026-01-16T00:00:00Z"
}
```

#### POST `/api/devices/{device_id}/status`
Send device status to cloud.

Request:
```json
{
  "device_id": "lumy-001",
  "status": "online",
  "last_refresh": "2026-01-16T01:00:00Z",
  "widgets": {
    "clock": "ok",
    "weather": "error",
    "calendar": "ok"
  },
  "system": {
    "cpu_temp": 45.2,
    "memory_usage": 65.3,
    "uptime": 86400
  }
}
```

#### POST `/api/devices/{device_id}/logs`
Send logs to cloud for debugging.

Request:
```json
{
  "device_id": "lumy-001",
  "level": "error",
  "message": "Failed to fetch weather data",
  "timestamp": "2026-01-16T01:00:00Z",
  "details": {}
}
```

### Vercel Dashboard Endpoints

#### GET `/api/devices`
List all registered devices.

#### POST `/api/devices`
Register a new device.

#### PUT `/api/devices/{device_id}/config`
Update device configuration.

#### GET `/api/devices/{device_id}/logs`
View device logs.

## Bluetooth Protocol

iPhone app uses BLE GATT to communicate with Pi:
- **Service UUID**: `12345678-1234-5678-1234-56789abcdef0`
- **Commands**: `refresh`, `update_widget`, `get_status`, etc.
- See `docs/BLUETOOTH_PROTOCOL.md` for full spec

## Deployment

### Vercel (Cloud)
```bash
cd web
vercel deploy --prod
```

### Raspberry Pi (Local)
```bash
cd backend
python3 main.py
```

## Configuration

### Pi Environment Variables
```bash
LUMY_DEVICE_ID=lumy-001
LUMY_API_URL=https://your-app.vercel.app/api
LUMY_API_KEY=your-api-key
```

### Vercel Environment Variables
```bash
DATABASE_URL=postgresql://...  # Supabase/Neon
NEXTAUTH_SECRET=...
```

## Benefits

✅ **Reliability**: Works offline via Bluetooth  
✅ **Scalability**: Cloud handles heavy lifting  
✅ **Speed**: Local control is instant  
✅ **Flexibility**: Configure from anywhere via web  
✅ **Monitoring**: Remote status and logs  
