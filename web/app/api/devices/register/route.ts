import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

export async function POST(request: NextRequest) {
  const apiKey = request.headers.get('X-API-KEY');

  if (apiKey !== process.env.LUMY_API_KEY) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { device_id, registration_code, expires_in = 3600 } = body;

    if (!device_id || !registration_code) {
      return NextResponse.json(
        { error: 'device_id and registration_code are required' },
        { status: 400 }
      );
    }

    // Calculate expiry time
    const expiresAt = new Date(Date.now() + expires_in * 1000);

    // Insert registration code
    const { data, error } = await supabase
      .from('registration_codes')
      .insert({
        device_id,
        code: registration_code.toUpperCase(),
        expires_at: expiresAt.toISOString(),
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating registration code:', error);
      return NextResponse.json(
        { error: 'Failed to create registration code' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      code: registration_code.toUpperCase(),
      expires_at: expiresAt.toISOString(),
    });
  } catch (error) {
    console.error('Error processing registration:', error);
    return NextResponse.json(
      { error: 'Invalid request data' },
      { status: 400 }
    );
  }
}
