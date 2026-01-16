# Lumy Cloud Setup Guide

This guide shows you how to set up the hybrid architecture with Vercel hosting the Next.js dashboard and your Raspberry Pi communicating with it.

## Architecture Overview

```
┌─────────────┐
│   iPhone    │ ◄──── Bluetooth (local, instant)
└──────┬──────┘
       │
       ▼
┌──────────────────┐         HTTPS          ┌──────────────────┐
│  Raspberry Pi    │ ◄────────────────────► │  Vercel Cloud    │
│  (Lumy Backend)  │    Polls every 60s     │  (Next.js + API) │
└──────────────────┘                        └──────────────────┘
```

## Benefits

- ✅ **Web Dashboard**: Configure from anywhere via browser
- ✅ **Bluetooth Control**: iPhone app for instant local control
- ✅ **Remote Monitoring**: See device status and logs in cloud
- ✅ **Offline Capable**: Works without internet via Bluetooth
- ✅ **Scalable**: Add multiple devices easily

## Step 1: Deploy Next.js to Vercel

### 1.1 Prepare for Deployment

```bash
cd ~/lumy/web

# Install dependencies on your Mac (not Pi)
npm install

# Test build locally
npm run build
```

### 1.2 Deploy to Vercel

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

**Option B: Using GitHub + Vercel Dashboard**

1. Push your code to GitHub (already done)
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your `postysh/lumy` repository
5. Set root directory to `web`
6. Click "Deploy"

### 1.3 Add Database (Supabase)

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Copy the `DATABASE_URL` connection string
4. In Vercel dashboard → Settings → Environment Variables
5. Add: `DATABASE_URL=your-supabase-url`

### 1.4 Create Database Tables

Connect to Supabase and run these SQL commands:

```sql
-- Devices table
CREATE TABLE devices (
  id TEXT PRIMARY KEY,
  name TEXT,
  mac_address TEXT,
  api_key TEXT UNIQUE NOT NULL,
  status TEXT DEFAULT 'offline',
  last_seen TIMESTAMP,
  config JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Device logs table
CREATE TABLE device_logs (
  id SERIAL PRIMARY KEY,
  device_id TEXT REFERENCES devices(id),
  level TEXT,
  message TEXT,
  details JSONB DEFAULT '{}',
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Device status table
CREATE TABLE device_status (
  device_id TEXT PRIMARY KEY REFERENCES devices(id),
  status TEXT,
  last_refresh TIMESTAMP,
  widgets JSONB DEFAULT '{}',
  system JSONB DEFAULT '{}',
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_device_logs_device_id ON device_logs(device_id);
CREATE INDEX idx_device_logs_timestamp ON device_logs(timestamp DESC);
```

## Step 2: Add Vercel API Endpoints

Create these files in your Next.js project:

### `web/app/api/devices/[id]/config/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!
);

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  
  // Verify API key from Authorization header
  const apiKey = request.headers.get('authorization')?.replace('Bearer ', '');
  
  const { data: device, error } = await supabase
    .from('devices')
    .select('config')
    .eq('id', deviceId)
    .eq('api_key', apiKey)
    .single();
  
  if (error || !device) {
    return NextResponse.json({ error: 'Device not found' }, { status: 404 });
  }
  
  return NextResponse.json(device.config);
}
```

### `web/app/api/devices/[id]/status/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!
);

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  const body = await request.json();
  
  // Update device status
  await supabase
    .from('device_status')
    .upsert({
      device_id: deviceId,
      status: body.status,
      last_refresh: body.last_refresh,
      widgets: body.widgets,
      system: body.system,
      updated_at: new Date().toISOString()
    });
  
  // Update last_seen in devices table
  await supabase
    .from('devices')
    .update({ 
      last_seen: new Date().toISOString(),
      status: body.status
    })
    .eq('id', deviceId);
  
  return NextResponse.json({ success: true });
}
```

## Step 3: Configure Raspberry Pi

### 3.1 Create Environment File

On your Pi:

```bash
cd ~/lumy/backend
nano .env
```

Add:

```bash
LUMY_DEVICE_ID=lumy-001
LUMY_API_URL=https://your-app.vercel.app/api
LUMY_API_KEY=your-api-key-from-supabase
```

### 3.2 Register Device in Supabase

In Supabase SQL Editor:

```sql
INSERT INTO devices (id, name, api_key, config)
VALUES (
  'lumy-001',
  'My Lumy Display',
  'generate-a-random-key-here',
  '{"display": {"width": 800, "height": 480, "refresh_interval": 300}, "widgets": [{"id": "clock", "enabled": true, "config": {}}, {"id": "weather", "enabled": true, "config": {"location": "New York"}}]}'
);
```

### 3.3 Install Dependencies

```bash
cd ~/lumy/backend
pip3 install psutil --break-system-packages
```

### 3.4 Test Connection

```bash
python3 main.py
```

You should see:
```
Cloud sync initialized - Device ID: lumy-001
API URL: https://your-app.vercel.app/api
Starting cloud sync (poll interval: 60s)
```

## Step 4: Enable Cloud Sync

Edit `~/lumy/backend/config.yaml`:

```yaml
cloud:
  enabled: true
  poll_interval: 60
```

Restart Lumy:

```bash
sudo pkill -9 python3
python3 main.py
```

## Step 5: Verify It's Working

1. Check the Lumy logs - should see "Config updated from cloud"
2. Go to your Vercel dashboard
3. Check Supabase - device_status table should have recent entries
4. Your Pi is now syncing with the cloud!

## Usage

### Update Config from Dashboard

1. Open your Vercel app in browser
2. Go to devices page
3. Update widget settings
4. Pi will fetch the new config within 60 seconds

### Bluetooth Still Works!

- iPhone can connect via Bluetooth
- No internet required for local control
- Instant response (no cloud latency)

## Troubleshooting

**"Cloud sync disabled"**
- Make sure `.env` file exists with API URL and key

**"Device not registered"**
- Check device_id matches in .env and Supabase

**"Failed to fetch config: HTTP 404"**
- Verify API key is correct
- Check device exists in Supabase

**Connection errors**
- Verify Vercel app is deployed
- Check API URL is correct (https://your-app.vercel.app/api)
- Test URL in browser

## Next Steps

- Build iPhone app with Bluetooth control
- Add more widgets
- Set up auto-start with systemd
- Monitor devices from dashboard
