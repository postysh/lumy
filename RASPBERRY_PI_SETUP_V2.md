# Raspberry Pi Setup v2 - Complete Restart

**This is a complete rebuild of the Raspberry Pi backend based on official Raspberry Pi Access Point documentation.**

## 🎯 What Changed

### ❌ Problems with v1:
- Guessed at hostapd configuration
- NetworkManager conflicts
- Incomplete dhcpcd setup
- Missing `nohook wpa_supplicant`
- Factory reset deleted AP configuration

### ✅ Fixes in v2:
- **Official Raspberry Pi AP setup** - Based on proven documentation
- **Proper dhcpcd configuration** - Static IP with `nohook wpa_supplicant` (the critical piece!)
- **Simplified hostapd** - Minimal, working configuration
- **Working DHCP** - dnsmasq properly configured
- **Factory reset preserves AP config** - Only clears saved WiFi networks
- **Large, readable fonts** - 80pt+ titles for 800x480 display

---

## 🚀 Fresh Installation

### Prerequisites:
- Raspberry Pi Zero 2 W
- Waveshare 7.3" E-Paper HAT (E)
- Fresh Raspberry Pi OS (64-bit recommended)
- Internet connection (Ethernet or WiFi for initial setup)

### Step 1: Clone Repository

```bash
git clone https://github.com/postysh/lumy.git
cd lumy
```

### Step 2: Run Installation

```bash
sudo bash scripts/install-v2.sh
```

**What it does:**
1. ✅ Installs system packages
2. ✅ Enables SPI
3. ✅ Creates Python venv with all dependencies
4. ✅ Installs Waveshare library
5. ✅ Tests display (must pass!)
6. ✅ Configures WiFi AP mode properly
7. ✅ Creates systemd service
8. ✅ Prompts for reboot

### Step 3: Reboot

```bash
sudo reboot
```

---

## 📱 Customer First Boot Experience

### What Happens:

1. **Customer powers on device**
2. **Display shows:** "WiFi Setup Required" (large, readable text)
   - "1. Connect to WiFi: Lumy-XXXXXX"
   - "2. Go to: 192.168.4.1"
   - "3. Enter WiFi password"

3. **Customer connects phone/laptop to:** `Lumy-XXXXXX`

4. **Browser automatically opens** to: `http://192.168.4.1`
   - Or customer manually navigates to it

5. **Captive portal shows:**
   - List of available WiFi networks
   - Password field
   - Connect button

6. **Customer selects home WiFi and enters password**

7. **Device connects to home WiFi and reboots**

8. **Display shows:** "Welcome to Lumy" + **Registration Code**

9. **Customer goes to:** `https://lumy-beta.vercel.app`

10. **Customer signs in and registers device with code**

---

## 🏭 Factory Reset (For Shipping)

When preparing a device for a new customer:

```bash
cd ~/lumy
sudo bash scripts/factory-reset-v2.sh
```

**What it does:**
1. ✅ Clears display (blank/white screen)
2. ✅ Resets device registration
3. ✅ Clears ALL saved WiFi networks
4. ✅ **Preserves AP mode configuration** ← Critical!
5. ✅ Removes WiFi state files
6. ✅ Automatically reboots

**Result:**
- Device is ready to ship
- Display is blank
- On first boot, device goes into AP mode
- Customer can configure WiFi

---

## 🔧 How WiFi AP Mode Works

### The Key Components:

#### 1. `/etc/dhcpcd.conf`
```conf
# Lumy AP Mode Configuration
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant  ← THIS IS CRITICAL!
```

**Why it matters:**
- Gives `wlan0` a static IP (192.168.4.1)
- `nohook wpa_supplicant` prevents wpa_supplicant from interfering with hostapd
- **This was the missing piece!**

#### 2. `/etc/hostapd/hostapd.conf`
```conf
interface=wlan0
driver=nl80211
ssid=Lumy-Setup
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
country_code=US
```

**Why this works:**
- Minimal configuration (no unnecessary options)
- Uses `nl80211` driver (standard for Pi)
- Channel 6 (universally compatible)
- Open network (no password for setup)
- `country_code=US` for regulatory compliance

#### 3. `/etc/dnsmasq.conf`
```conf
interface=wlan0
dhcp-range=192.168.4.10,192.168.4.250,255.255.255.0,24h
# Captive portal DNS redirects
address=/connectivitycheck.gstatic.com/192.168.4.1
address=/captive.apple.com/192.168.4.1
address=/www.msftconnecttest.com/192.168.4.1
```

**Why this works:**
- DHCP assigns IPs to connected devices
- DNS redirects trigger captive portal on phones

---

## 🐛 Troubleshooting

### AP not showing up

```bash
# Check if hostapd is running
sudo systemctl status hostapd

# Check logs
sudo journalctl -u hostapd -n 50

# Check if wlan0 has IP
ip addr show wlan0
# Should show: 192.168.4.1/24

# Try restarting services
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq
```

### Can see AP but can't connect

```bash
# Check dnsmasq is running
sudo systemctl status dnsmasq

# Check for wpa_supplicant interference
ps aux | grep wpa_supplicant
# If running: sudo pkill wpa_supplicant

# Verify dhcpcd config
grep -A3 "interface wlan0" /etc/dhcpcd.conf
# Should show static IP and nohook wpa_supplicant
```

### Captive portal not opening

```bash
# Check if Flask server is running
sudo systemctl status lumy
sudo journalctl -u lumy -f

# Check if port 80 is listening
sudo netstat -tulnp | grep :80

# Manually test
curl http://192.168.4.1
```

### Fonts still small

```bash
# Check logs for font loading
sudo journalctl -u lumy -n 100 | grep -i font

# Verify font files exist
ls -lh /usr/share/fonts/truetype/dejavu/

# Check display manager code
grep -n "font_title.*truetype" ~/lumy/backend/main.py
# Should show sizes 80+ for title fonts
```

---

## 📊 Service Status

```bash
# View live logs
sudo journalctl -u lumy -f

# Check service status
sudo systemctl status lumy

# Restart service
sudo systemctl restart lumy

# Check AP mode
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

---

## ✅ What Makes This Work

1. **`nohook wpa_supplicant` in dhcpcd.conf** - Prevents interference
2. **Static IP on wlan0** - Gives AP a consistent address
3. **Simplified hostapd config** - No unnecessary complexity
4. **Proper DHCP range** - Clients get IPs (192.168.4.10-250)
5. **Factory reset preserves AP config** - Device can always go back to AP mode
6. **Large fonts** - 80pt+ titles for readability

---

## 🎯 Success Criteria

✅ Display shows test message after installation  
✅ `Lumy-XXXXXX` WiFi appears after reboot  
✅ Can connect to WiFi from phone/laptop  
✅ Get IP address (192.168.4.x)  
✅ Browser opens captive portal automatically  
✅ Can see WiFi list at http://192.168.4.1  
✅ Can configure home WiFi  
✅ Device reboots and shows registration code  
✅ Fonts are large and readable  
✅ Factory reset works and device goes back to AP mode  

---

## 📞 Support

If issues persist after following this guide:

1. Run installation fresh on a clean SD card
2. Check all services are running
3. Verify dhcpcd.conf has the AP configuration
4. Check logs for specific errors
5. Make sure SPI is enabled (`ls /dev/spi*`)

This v2 approach is based on official Raspberry Pi documentation and proven configurations. It should work reliably.
