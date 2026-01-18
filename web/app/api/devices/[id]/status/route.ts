import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

// GET - Retrieve device status
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  
  try {
    const { data, error } = await supabase
      .from('device_status')
      .select('*')
      .eq('device_id', deviceId)
      .single();
    
    if (error || !data) {
      return NextResponse.json({
        device_id: deviceId,
        status: 'offline',
        last_refresh: null,
        widgets: {},
        system: {},
        updated_at: null
      });
    }
    
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({
      device_id: deviceId,
      status: 'offline',
      last_refresh: null,
      widgets: {},
      system: {},
      updated_at: null
    });
  }
}

// POST - Update device status
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  const body = await request.json();
  
  try {
    const statusData = {
      device_id: deviceId,
      status: body.status,
      last_refresh: body.last_refresh,
      widgets: body.widgets || {},
      system: body.system || {},
      updated_at: new Date().toISOString()
    };
    
    // Upsert status in Supabase
    const { error } = await supabase
      .from('device_status')
      .upsert(statusData);
    
    if (error) {
      console.error('Supabase error:', error);
    } else {
      console.log(`Device ${deviceId} status updated:`, body);
    }
    
    // If display preview is provided, update the device record
    if (body.display_preview) {
      const { error: deviceError } = await supabase
        .from('devices')
        .update({ 
          display_preview: body.display_preview,
          last_seen: new Date().toISOString(),
          is_online: true
        })
        .eq('device_id', deviceId);
      
      if (deviceError) {
        console.error('Failed to update device preview:', deviceError);
      }
    } else {
      // Just update last_seen and is_online
      await supabase
        .from('devices')
        .update({ 
          last_seen: new Date().toISOString(),
          is_online: true
        })
        .eq('device_id', deviceId);
    }
    
    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('Error updating status:', err);
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
