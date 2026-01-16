-- Device Registration System Tables
-- DROP AND RECREATE EVERYTHING

-- Drop existing tables (cascades to policies)
DROP TABLE IF EXISTS registration_codes CASCADE;
DROP TABLE IF EXISTS devices CASCADE;

-- Create devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id TEXT UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    device_name TEXT DEFAULT 'Lumy Display',
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    is_online BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create registration codes table
CREATE TABLE registration_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    device_id TEXT NOT NULL,
    claimed_by UUID,
    claimed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_devices_user_id ON devices(user_id);
CREATE INDEX idx_devices_device_id ON devices(device_id);
CREATE INDEX idx_registration_codes_code ON registration_codes(code);
CREATE INDEX idx_registration_codes_device_id ON registration_codes(device_id);

-- Enable RLS
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration_codes ENABLE ROW LEVEL SECURITY;

-- RLS policies for devices - users can only see their own
CREATE POLICY "users_own_devices" ON devices
    FOR ALL USING (auth.uid() = user_id);

-- RLS policies for registration codes
CREATE POLICY "auth_can_view_codes" ON registration_codes
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "auth_can_update_codes" ON registration_codes
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Service role bypass (for API)
CREATE POLICY "service_all_devices" ON devices
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_all_codes" ON registration_codes
    FOR ALL USING (auth.role() = 'service_role');
