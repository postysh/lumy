-- Add display_preview column to devices table
-- This stores a base64-encoded thumbnail of the current display

ALTER TABLE devices
ADD COLUMN IF NOT EXISTS display_preview TEXT;

COMMENT ON COLUMN devices.display_preview IS 'Base64-encoded thumbnail preview of current display (data URL format)';
