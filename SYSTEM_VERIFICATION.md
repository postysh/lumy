# Lumy System Verification Checklist

## ✅ Code Format
- **Backend generates**: `ABC-123` (3 letters, dash, 3 numbers)
- **Dashboard expects**: `ABC-123` format with maxLength=7
- **Status**: ✅ MATCHES

## ✅ API Flow

### 1. Device Registration
**Endpoint**: `POST /api/devices/register`
- **Headers**: `X-API-KEY: ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv`
- **Body**: 
```json
{
  "device_id": "lumy-xxxxxxxxxxxx",
  "registration_code": "ABC-123",
  "expires_in": 3600
}
```
- **Response**:
```json
{
  "success": true,
  "code": "ABC-123",
  "expires_at": "2026-01-18T..."
}
```
- **Database**: Inserts into `registration_codes` table
- **Status**: ✅ IMPLEMENTED

### 2. User Claims Device
**Endpoint**: `POST /api/devices/claim`
- **Auth**: User must be logged in (Supabase auth)
- **Body**:
```json
{
  "code": "ABC-123",
  "device_name": "Lumy Display"
}
```
- **Process**:
  1. Finds code in `registration_codes` table
  2. Updates `claimed_by` and `claimed_at`
  3. Upserts into `devices` table with `user_id`
- **Status**: ✅ IMPLEMENTED

### 3. Device Checks Claim Status
**Endpoint**: `GET /api/devices/{device_id}/registration`
- **Headers**: `X-API-KEY: ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv`
- **Response (not claimed)**:
```json
{
  "registered": false,
  "device_id": "lumy-xxxxxxxxxxxx"
}
```
- **Response (claimed)**:
```json
{
  "registered": true,
  "device_id": "lumy-xxxxxxxxxxxx",
  "user_id": "uuid",
  "device_name": "Lumy Display",
  "registered_at": "2026-01-18T..."
}
```
- **Status**: ✅ IMPLEMENTED

### 4. Device Fetches Config
**Endpoint**: `GET /api/devices/{device_id}/config`
- **Headers**: `Authorization: Bearer {api_key}` (optional)
- **Response**:
```json
{
  "device_id": "lumy-xxxxxxxxxxxx",
  "display": {
    "width": 800,
    "height": 480,
    "refresh_interval": 300
  },
  "widgets": [...]
}
```
- **Status**: ✅ IMPLEMENTED (returns static config for now)

### 5. Device Sends Heartbeat
**Endpoint**: `POST /api/devices/{device_id}/status`
- **Body**:
```json
{
  "status": "online",
  "last_refresh": null,
  "widgets": {},
  "system": {}
}
```
- **Database**: Upserts into `device_status` table
- **Status**: ✅ IMPLEMENTED

## ✅ Backend Configuration

### Config Values
```python
API_BASE_URL = 'https://lumy-hzo8z4iqa-postysh.vercel.app'
API_KEY = 'ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv'
DEVICE_ID_FILE = '/etc/lumy/device_id'
POLL_INTERVAL = 10  # seconds
CONFIG_REFRESH_INTERVAL = 300  # seconds
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
```
- **Status**: ✅ CONFIGURED

### Dependencies
- ✅ `requests>=2.31.0` (for API calls)
- ✅ `python3-pil` (system package for display)
- ✅ `python3-rpi.gpio` (system package for GPIO)
- ✅ `python3-spidev` (system package for SPI)
- ✅ `python3-numpy` (system package)

## ✅ Display Configuration
- **Resolution**: 800x480
- **Fonts**: DejaVu Sans (Bold 80pt, Regular 40pt, Mono Bold 100pt, Regular 30pt)
- **Layout**:
  - Title: "Welcome to Lumy" (centered, top)
  - Subtitle: "Your Smart Display" (centered, below title)
  - Code: Large monospace in box (centered, middle)
  - Instructions: Two lines (centered, bottom)
- **Status**: ✅ CONFIGURED

## ✅ Install Script
- Detects actual user dynamically
- Detects repository location
- Installs system packages
- Downloads Waveshare library (3 files only)
- Sets up systemd service with correct user/paths
- Uses default API credentials from config.py
- **Status**: ✅ READY

## ✅ Systemd Service
```ini
[Unit]
Description=Lumy Display Service
After=network.target

[Service]
Type=simple
User={actual_user}
WorkingDirectory={repo}/backend
EnvironmentFile=-{repo}/backend/.env
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
```
- **Status**: ✅ CONFIGURED

## ✅ Database Schema

### `registration_codes` table
```sql
- id UUID PRIMARY KEY
- code TEXT UNIQUE NOT NULL
- device_id TEXT NOT NULL
- claimed_by UUID
- claimed_at TIMESTAMPTZ
- expires_at TIMESTAMPTZ NOT NULL
- created_at TIMESTAMPTZ
```

### `devices` table
```sql
- id UUID PRIMARY KEY
- device_id TEXT UNIQUE NOT NULL
- user_id UUID NOT NULL
- device_name TEXT
- registered_at TIMESTAMPTZ
- last_seen TIMESTAMPTZ
- is_online BOOLEAN
- metadata JSONB
- created_at TIMESTAMPTZ
- updated_at TIMESTAMPTZ
```

### `device_status` table
```sql
- device_id TEXT PRIMARY KEY
- status TEXT
- last_refresh TIMESTAMPTZ
- widgets JSONB
- system JSONB
- updated_at TIMESTAMPTZ
```
- **Status**: ✅ SCHEMA DEFINED (run migration)

## 🔍 Pre-Flight Checklist

### Vercel Environment Variables
- [ ] `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- [ ] `LUMY_API_KEY` - Must be `ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv`

### Supabase Database
- [ ] Run migration: `database/migrations/003_device_registration.sql`
- [ ] Verify tables exist: `registration_codes`, `devices`, `device_status`
- [ ] Verify RLS policies are enabled

### Raspberry Pi
- [ ] WiFi connected and working
- [ ] SSH access enabled
- [ ] SD card has space (at least 1GB free)
- [ ] Display physically connected to GPIO

## 🚀 Installation Steps

### On Raspberry Pi:
```bash
# 1. Clone repository
git clone https://github.com/postysh/lumy.git lumy
cd lumy

# 2. Run install script
sudo bash scripts/install.sh

# 3. After reboot, check status
sudo systemctl status lumy
sudo journalctl -u lumy -f
```

## 📋 Expected Behavior

### On Pi:
1. Service starts automatically
2. Logs show: "Lumy Display Starting..."
3. Logs show: "Device ID: lumy-xxxxxxxxxxxx"
4. Logs show: "Registration code: ABC-123"
5. Logs show: "Registering with dashboard..."
6. Logs show: "Successfully registered with dashboard"
7. Display shows welcome screen with code
8. Logs show: "Waiting for user to claim device..."
9. Polls every 10 seconds

### In Dashboard:
1. Login to dashboard
2. Click "Add Device"
3. Enter code: ABC-123
4. Click "Add Device" button
5. Device should appear in list

### Back on Pi:
6. Logs show: "Device has been claimed!"
7. Logs show: "Fetching configuration..."
8. Logs show: "Entering main loop..."
9. Sends heartbeat every 60 seconds

## ⚠️ Common Issues

### 1. Registration fails
- Check `API_BASE_URL` includes `https://`
- Check `LUMY_API_KEY` matches Vercel env var
- Check internet connection on Pi

### 2. Display doesn't show anything
- Check SPI is enabled: `ls /dev/spi*`
- Check Waveshare library downloaded: `ls backend/lib/waveshare_epd/`
- Check fonts installed: `ls /usr/share/fonts/truetype/dejavu/`

### 3. Claim code not working in dashboard
- Check you're logged in
- Check code hasn't expired (1 hour default)
- Check code matches exactly (case-insensitive)
- Check database migration ran successfully

### 4. Device never detects claim
- Check X-API-KEY header is set correctly
- Check `/api/devices/{id}/registration` endpoint returns data
- Check `devices` table has entry with correct `device_id`

## ✅ System Status: READY FOR TESTING
