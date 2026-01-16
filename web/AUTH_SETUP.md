# Authentication Setup Guide

This guide will help you set up Supabase authentication for your Lumy dashboard.

## 1. Environment Variables

Add these to your `.env.local` file (create it if it doesn't exist):

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your-project-url.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Lumy API Key for Pi Authentication
LUMY_API_KEY=your-secret-api-key
```

## 2. Add to Vercel Environment Variables

In your Vercel project settings, add the same variables:

1. Go to https://vercel.com/your-username/lumy-beta/settings/environment-variables
2. Add each variable above
3. Redeploy after adding them

## 3. Configure Supabase Auth Settings

1. Go to your Supabase project dashboard
2. Navigate to **Authentication** → **URL Configuration**
3. Add your site URL: `https://lumy-beta.vercel.app`
4. Add redirect URLs:
   - `https://lumy-beta.vercel.app/auth/callback`
   - `http://localhost:3000/auth/callback` (for local development)

## 4. Enable Email Provider

1. In Supabase dashboard, go to **Authentication** → **Providers**
2. Make sure **Email** is enabled
3. Configure email templates if desired

## 5. Create Your First User

Two options:

### Option A: Sign up through the app
1. Visit https://lumy-beta.vercel.app/signup
2. Enter your email and password
3. Check your email for the confirmation link
4. Click the link to verify
5. Sign in at https://lumy-beta.vercel.app/login

### Option B: Create user in Supabase dashboard
1. Go to **Authentication** → **Users**
2. Click **Add user**
3. Enter email and password
4. User can now sign in immediately

## Security Features

✅ **Route Protection** - All `/dashboard/*` routes require authentication
✅ **API Protection** - `/api/devices/*` routes still allow Pi without auth
✅ **Session Management** - Automatic session refresh
✅ **Email Verification** - Users must verify their email
✅ **Secure Cookies** - Session stored in HTTPOnly cookies

## API Routes (No Auth Required)

These routes are accessible without authentication (for your Raspberry Pi):

- `POST /api/devices/[id]/status` - Pi status updates
- `GET /api/devices/[id]/config` - Pi config fetch
- `POST /api/devices/[id]/logs` - Pi log sending

## Troubleshooting

### "Email not confirmed" error
- Check your spam folder for the confirmation email
- Or manually confirm the user in Supabase dashboard

### Redirect loop
- Make sure `NEXT_PUBLIC_SUPABASE_URL` is set correctly
- Check that redirect URLs are configured in Supabase

### "Invalid API key" on Pi
- Verify `LUMY_API_KEY` matches in both Pi and Vercel
- Check Pi's `.env` file has correct `LUMY_API_URL`
