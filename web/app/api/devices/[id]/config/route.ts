import { NextRequest, NextResponse } from 'next/server';

// This is a placeholder - you'll need to add Supabase after deployment
// For now, return static config
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const deviceId = params.id;
  
  // Verify API key (basic check for now)
  const apiKey = request.headers.get('authorization')?.replace('Bearer ', '');
  if (!apiKey) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  // Return default config (replace with database query after Supabase setup)
  const config = {
    device_id: deviceId,
    display: {
      width: 800,
      height: 480,
      refresh_interval: 300
    },
    widgets: [
      {
        id: 'clock',
        enabled: true,
        config: {}
      },
      {
        id: 'weather',
        enabled: true,
        config: {
          location: 'New York',
          units: 'metric'
        }
      },
      {
        id: 'calendar',
        enabled: true,
        config: {
          max_events: 5
        }
      }
    ],
    updated_at: new Date().toISOString()
  };
  
  return NextResponse.json(config);
}
