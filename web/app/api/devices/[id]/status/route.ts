import { NextRequest, NextResponse } from 'next/server';

// In-memory storage (replace with Supabase later)
const deviceStatuses = new Map();

// GET - Retrieve device status
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  
  const status = deviceStatuses.get(deviceId) || {
    device_id: deviceId,
    status: 'offline',
    last_refresh: null,
    widgets: {},
    system: {},
    updated_at: null
  };
  
  return NextResponse.json(status);
}

// POST - Update device status
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  const body = await request.json();
  
  // Store status in memory
  const statusData = {
    device_id: deviceId,
    status: body.status,
    last_refresh: body.last_refresh,
    widgets: body.widgets || {},
    system: body.system || {},
    updated_at: new Date().toISOString()
  };
  
  deviceStatuses.set(deviceId, statusData);
  
  // Log the status
  console.log(`Device ${deviceId} status:`, body);
  
  return NextResponse.json({ success: true });
}
