import { NextResponse } from 'next/server';

// List all known devices
export async function GET() {
  // Return static device list for now
  // Replace with Supabase query later
  return NextResponse.json([
    {
      id: 'lumy-001',
      name: 'Lumy Display',
      status: 'unknown'
    }
  ]);
}
