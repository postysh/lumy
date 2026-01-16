import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function GET() {
  const supabase = await createClient();

  // Check if user is authenticated
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Get user's devices
  const { data: devices, error } = await supabase
    .from('devices')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Error fetching devices:', error);
    return NextResponse.json({ error: 'Failed to fetch devices' }, { status: 500 });
  }

  // Get latest status for each device from device_status table
  const devicesWithStatus = await Promise.all(
    (devices || []).map(async (device) => {
      const { data: status } = await supabase
        .from('device_status')
        .select('*')
        .eq('device_id', device.device_id)
        .single();

      return {
        ...device,
        current_status: status || null,
      };
    })
  );

  return NextResponse.json(devicesWithStatus);
}
