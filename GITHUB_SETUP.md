# GitHub Setup Guide

Follow these steps to push Lumy to GitHub and install it on your Raspberry Pi.

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the **+** icon in the top right → **New repository**
3. Repository settings:
   - **Name:** `lumy`
   - **Description:** Bluetooth-controlled E-Paper display for Raspberry Pi
   - **Visibility:** Public (or Private if you prefer)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **Create repository**

## Step 2: Push to GitHub

After creating the repository, run these commands on your Mac:

```bash
cd /Users/evan/Desktop/lumy

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/lumy.git

# Push the code
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Alternative: Using SSH

If you have SSH keys set up:

```bash
git remote add origin git@github.com:YOUR_USERNAME/lumy.git
git push -u origin main
```

## Step 3: Verify Upload

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/lumy`
2. You should see all the files uploaded
3. Check that the README.md displays correctly

## Step 4: Install on Raspberry Pi

Now you can install Lumy on your Raspberry Pi remotely!

### SSH into Your Raspberry Pi

```bash
# From your Mac or iPhone (using a terminal app like Termius)
ssh pi@raspberrypi.local
# Default password: raspberry (change this after first login!)
```

### One-Line Installation

```bash
cd ~ && git clone https://github.com/YOUR_USERNAME/lumy.git && cd lumy && chmod +x scripts/install.sh && ./scripts/install.sh
```

Or step by step:

```bash
# Clone the repository
cd ~
git clone https://github.com/YOUR_USERNAME/lumy.git
cd lumy

# Make scripts executable
chmod +x scripts/install.sh scripts/setup-bluetooth.sh scripts/test-display.py

# Run installation
./scripts/install.sh
```

The installation will take 10-15 minutes.

## Step 5: Test Your Display

After installation completes:

```bash
cd ~/lumy
python3 scripts/test-display.py
```

You should see a test pattern on your E-Paper display!

## Step 6: Start Lumy

```bash
sudo systemctl start lumy
sudo systemctl status lumy
```

## Step 7: Access from iPhone

### Find Your Pi's IP Address

```bash
hostname -I
```

### Open Web Dashboard

On your iPhone (or Mac), open Safari and go to:

```
http://YOUR_PI_IP:8000
```

Example: `http://192.168.1.100:8000`

## Quick Reference

### GitHub Commands

```bash
# Check repository status
git status

# Make changes and commit
git add .
git commit -m "Your commit message"
git push

# Pull latest changes on Pi
cd ~/lumy
git pull
sudo systemctl restart lumy
```

### Raspberry Pi Commands

```bash
# View logs
journalctl -u lumy -f

# Restart service
sudo systemctl restart lumy

# Stop service
sudo systemctl stop lumy

# Check display
python3 ~/lumy/scripts/test-display.py

# Edit configuration
nano ~/lumy/backend/config.yaml
# Then restart: sudo systemctl restart lumy
```

## Troubleshooting

### "Permission denied" when pushing to GitHub

You may need to authenticate. GitHub now requires Personal Access Tokens:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` permissions
3. Use the token as your password when pushing

Or set up SSH keys:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add this to GitHub Settings → SSH Keys
```

### Can't SSH to Raspberry Pi

Make sure SSH is enabled:
1. On the Pi, run `sudo raspi-config`
2. Go to Interface Options → SSH → Enable
3. Alternatively, create an empty file named `ssh` in the boot partition

### Raspberry Pi not found on network

```bash
# Use IP address instead
ssh pi@192.168.1.X

# Or find it with
sudo nmap -sn 192.168.1.0/24 | grep -i raspberry
```

## Security Tips

1. **Change default password:**
   ```bash
   passwd
   ```

2. **Update system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Enable firewall (optional):**
   ```bash
   sudo apt install ufw
   sudo ufw allow ssh
   sudo ufw allow 8000
   sudo ufw enable
   ```

## Next Steps

- Customize `backend/config.yaml` for your preferences
- Add OpenWeatherMap API key for weather widget
- Create custom widgets
- Build iOS app using the Bluetooth protocol docs

## Your Repository URL

After setup, your Lumy will be at:
```
https://github.com/YOUR_USERNAME/lumy
```

Installation command will be:
```bash
git clone https://github.com/YOUR_USERNAME/lumy.git
```

---

**Questions?** Check the docs:
- [Quick Start](docs/QUICK_START.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Bluetooth Protocol](docs/BLUETOOTH_PROTOCOL.md)
