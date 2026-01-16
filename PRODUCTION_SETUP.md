# Lumy Production Setup Guide

This guide explains how to prepare Lumy devices for customers with zero configuration needed by the end user.

## Overview

**The Goal:** Customer receives a device, powers it on, sees a registration code, and claims it in 2 minutes.

## Architecture

```
┌─────────────────────────────────────────┐
│  YOU (One-time setup per device)       │
│  ─────────────────────────────────      │
│  • Install Lumy on Raspberry Pi         │
│  • Test that welcome screen appears     │
│  • Ship device to customer              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  CUSTOMER (Zero configuration)          │
│  ─────────────────────────────────      │
│  1. Power on device                     │
│  2. See welcome screen + code           │
│  3. Visit lumy-beta.vercel.app          │
│  4. Sign in                             │
│  5. Click "Add Device"                  │
│  6. Enter code                          │
│  7. Done!                               │
└─────────────────────────────────────────┘
```

## Step 1: Vercel Configuration

### Set Production API Key

In your Vercel project environment variables, make sure you have:

```bash
LUMY_API_KEY=lumy-production-2026
```

**Important:** This key is hardcoded in the install script for production devices. If you change it in Vercel, you must also update `scripts/install.sh`.

## Step 2: Prepare a Master Device

### Initial Setup (do this once)

```bash
# On a fresh Raspberry Pi OS installation
cd ~
git clone https://github.com/postysh/lumy.git
cd lumy
sudo bash scripts/install.sh
```

The installer will:
- ✅ Install all dependencies
- ✅ Set up systemd service
- ✅ Auto-configure with production API URL
- ✅ Start Lumy automatically
- ✅ Show registration code on display

**This takes 15-30 minutes on Pi Zero.** But you only do it once per device!

### Verify Installation

Check that the welcome screen appears:

```bash
journalctl -u lumy -f | grep -i 'code'
```

You should see:
```
Generated registration code: ABC-123
```

The display should show:
```
Welcome to Lumy
Register at: lumy-beta.vercel.app
Code: ABC-123
```

## Step 3: Create a Disk Image (Optional but Recommended)

Once you have one working device, create a disk image:

```bash
# On your Mac/PC (not on the Pi)
# Insert SD card and create image
sudo dd if=/dev/disk2 of=lumy-production-v1.img bs=1m

# Compress for storage
gzip lumy-production-v1.img
```

Now you can flash this image to multiple SD cards instantly!

## Step 4: Ship to Customer

### Before Shipping Checklist

- [ ] Display shows "Welcome to Lumy" screen
- [ ] Registration code is visible
- [ ] Device auto-starts on power up
- [ ] Waveshare cable is securely connected

### What to Include

1. **Raspberry Pi with Lumy pre-installed**
2. **Power supply** (2.5A minimum for Pi Zero)
3. **Quick start card** with instructions

### Quick Start Card Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  LUMY E-PAPER DISPLAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SETUP (2 MINUTES):

1. Plug in power cable
2. Wait 30 seconds for display to show code
3. Visit: lumy-beta.vercel.app
4. Sign in (or create account)
5. Click "Add Device"
6. Enter the code shown on your display
7. Done!

Your display will update automatically!

Support: [your email]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 5: Customer Onboarding

### What Customer Does

1. **Powers on device** → Sees welcome screen
2. **Visits dashboard** → Signs in/up
3. **Clicks "Add Device"** → Dialog appears
4. **Enters code** → Device is claimed
5. **Sees their device** → In device list
6. **Display updates** → Shows widgets automatically

### Registration Code Expiry

- Codes expire after **1 hour**
- If expired, device will generate a new code
- Customer can restart device to get new code: `sudo reboot`

## Step 6: Factory Reset (Reselling a Device)

If you need to reset a device for a new customer:

```bash
cd ~/lumy
sudo bash scripts/factory-reset.sh
```

This will:
- Clear the device registration
- Generate a new code
- Preserve the installation (no reinstall needed)

## Troubleshooting

### Display doesn't show welcome screen

```bash
# Check service status
sudo systemctl status lumy

# View logs
journalctl -u lumy -f

# Restart service
sudo systemctl restart lumy
```

### Display shows error or blank

```bash
# Test display directly
cd ~/lumy
python3 scripts/test-display.py
```

### SPI not enabled

```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

## Production API Configuration

The production setup uses these defaults:

```bash
LUMY_API_URL=https://lumy-beta.vercel.app/api
LUMY_API_KEY=lumy-production-2026
```

These are hardcoded in `scripts/install.sh` for consistency.

## Scaling Production

### For 1-10 Devices
- Install each one manually using the install script
- Takes 20-30 min per device (mostly unattended)

### For 10+ Devices
- Create a master disk image (once)
- Flash image to SD cards using Etcher or dd
- Takes 5 minutes per device

### For 100+ Devices
- Partner with a contract manufacturer
- Provide them the disk image
- They flash and test each device

## Support

If a customer has issues:

1. **Check device in dashboard** → Should show online/offline status
2. **View device logs remotely** → (Coming soon: log streaming)
3. **Ask for registration code** → They can read it from display
4. **Factory reset remotely** → (Coming soon: remote reset)

## Security Notes

- API key is the same for all production devices (by design)
- Device security is handled by Supabase RLS (row-level security)
- Each device has unique device_id (MAC-based)
- Devices can only be claimed by one user
- Once claimed, only that user can access it

## Cost Analysis

**Per Device:**
- Raspberry Pi Zero 2 W: $15
- Waveshare 7.3" Display: $45
- SD Card (32GB): $8
- Power Supply: $8
- Case (optional): $5-15

**Total:** ~$80-90 per device

**Your Time:**
- First device: 1 hour (learning)
- Subsequent devices: 30 min each (if installing manually)
- With disk image: 10 min each (mostly flashing)

## Next Steps

1. ✅ Set up Vercel with production API key
2. ✅ Install Lumy on test device
3. ✅ Verify registration flow works
4. ✅ Create disk image (optional)
5. ✅ Prepare quick start cards
6. ✅ Ship first device!

---

**Questions?** Check the troubleshooting guide or open an issue on GitHub.
