import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  const apiKey = request.headers.get('X-API-KEY');

  if (apiKey !== process.env.LUMY_API_KEY) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // Check if device is registered
    const { data: device, error } = await supabase
      .from('devices')
      .select('user_id, device_name, registered_at')
      .eq('device_id', deviceId)
      .single();

    if (error && error.code !== 'PGRST116') {
      console.error('Error checking registration:', error);
      return NextResponse.json(
        { error: 'Failed to check registration' },
        { status: 500 }
      );
    }

    if (!device) {
      return NextResponse.json({
        registered: false,
        device_id: deviceId,
      });
    }

    return NextResponse.json({
      registered: true,
      device_id: deviceId,
      user_id: device.user_id,
      device_name: device.device_name,
      registered_at: device.registered_at,
    });
  } catch (error) {
    console.error('Error checking registration:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
