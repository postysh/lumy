import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function POST(request: NextRequest) {
  const supabase = await createClient();

  // Check if user is authenticated
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { code, device_name } = body;

    if (!code) {
      return NextResponse.json({ error: 'Code is required' }, { status: 400 });
    }

    const codeUpper = code.toUpperCase().trim();

    // Find the registration code
    const { data: regCode, error: codeError } = await supabase
      .from('registration_codes')
      .select('*')
      .eq('code', codeUpper)
      .single();

    if (codeError || !regCode) {
      return NextResponse.json(
        { error: 'Invalid or expired code' },
        { status: 404 }
      );
    }

    // Check if code is expired
    if (new Date(regCode.expires_at) < new Date()) {
      return NextResponse.json({ error: 'Code has expired' }, { status: 400 });
    }

    // Check if code is already claimed
    if (regCode.claimed_at) {
      return NextResponse.json(
        { error: 'Code already claimed' },
        { status: 400 }
      );
    }

    // Check if device is already registered to another user
    const { data: existingDevice } = await supabase
      .from('devices')
      .select('user_id')
      .eq('device_id', regCode.device_id)
      .single();

    if (existingDevice && existingDevice.user_id !== user.id) {
      return NextResponse.json(
        { error: 'Device already registered to another user' },
        { status: 409 }
      );
    }

    // Claim the code
    const { error: claimError } = await supabase
      .from('registration_codes')
      .update({
        claimed_by: user.id,
        claimed_at: new Date().toISOString(),
      })
      .eq('code', codeUpper);

    if (claimError) {
      console.error('Error claiming code:', claimError);
      return NextResponse.json(
        { error: 'Failed to claim code' },
        { status: 500 }
      );
    }

    // Register the device
    const { data: device, error: deviceError } = await supabase
      .from('devices')
      .upsert(
        {
          device_id: regCode.device_id,
          user_id: user.id,
          device_name: device_name || 'Lumy Display',
          registered_at: new Date().toISOString(),
          last_seen: new Date().toISOString(),
          is_online: true,
        },
        { onConflict: 'device_id' }
      )
      .select()
      .single();

    if (deviceError) {
      console.error('Error registering device:', deviceError);
      return NextResponse.json(
        { error: 'Failed to register device' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      device,
    });
  } catch (error) {
    console.error('Error claiming device:', error);
    return NextResponse.json(
      { error: 'Invalid request data' },
      { status: 400 }
    );
  }
}
