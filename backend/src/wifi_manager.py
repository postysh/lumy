"""WiFi Manager - Handles AP mode and WiFi configuration"""

import os
import subprocess
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class WiFiManager:
    """Manages WiFi connectivity and AP mode"""
    
    def __init__(self):
        self.ap_ssid = None
        self.is_ap_mode = False
        
    def is_connected(self) -> bool:
        """Check if Pi is connected to WiFi"""
        try:
            # Method 1: Check if wlan0 has an IP address (most reliable)
            result = subprocess.run(
                ['ip', 'addr', 'show', 'wlan0'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Check if wlan0 has an inet (IPv4) address
                if 'inet ' in result.stdout:
                    logger.info("WiFi connected (wlan0 has IP address)")
                    
                    # Method 2: Try to get SSID name for logging
                    try:
                        ssid_result = subprocess.run(
                            ['iwgetid', '-r'],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        if ssid_result.returncode == 0 and ssid_result.stdout.strip():
                            logger.info(f"Connected to SSID: {ssid_result.stdout.strip()}")
                    except:
                        pass  # SSID name is optional
                    
                    return True
            
            logger.warning("Not connected to WiFi (no IP on wlan0)")
            return False
            
        except Exception as e:
            logger.error(f"Error checking WiFi connection: {e}")
            return False
    
    def get_mac_address(self) -> str:
        """Get MAC address for generating AP SSID"""
        try:
            # Get MAC address from wlan0
            mac_path = '/sys/class/net/wlan0/address'
            if Path(mac_path).exists():
                with open(mac_path, 'r') as f:
                    mac = f.read().strip().replace(':', '')[-6:].upper()
                    return mac
        except Exception as e:
            logger.error(f"Error getting MAC address: {e}")
        
        # Fallback to random
        import random
        return ''.join(random.choices('0123456789ABCDEF', k=6))
    
    def start_ap_mode(self):
        """Start WiFi Access Point mode"""
        try:
            logger.info("Starting WiFi AP mode...")
            
            # Generate SSID
            mac = self.get_mac_address()
            self.ap_ssid = f"Lumy-{mac}"
            
            # Stop wpa_supplicant
            subprocess.run(['sudo', 'systemctl', 'stop', 'wpa_supplicant'], check=False)
            
            # Start AP mode service
            subprocess.run(['sudo', 'systemctl', 'start', 'lumy-ap'], check=True)
            
            self.is_ap_mode = True
            logger.info(f"AP mode started: {self.ap_ssid}")
            
            return self.ap_ssid
            
        except Exception as e:
            logger.error(f"Failed to start AP mode: {e}")
            return None
    
    def stop_ap_mode(self):
        """Stop AP mode and return to normal WiFi"""
        try:
            logger.info("Stopping AP mode...")
            
            # Stop AP service
            subprocess.run(['sudo', 'systemctl', 'stop', 'lumy-ap'], check=False)
            
            # Restart wpa_supplicant
            subprocess.run(['sudo', 'systemctl', 'start', 'wpa_supplicant'], check=False)
            
            # Restart networking
            subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'], check=False)
            
            self.is_ap_mode = False
            logger.info("AP mode stopped")
            
        except Exception as e:
            logger.error(f"Error stopping AP mode: {e}")
    
    def configure_wifi(self, ssid: str, password: str) -> bool:
        """Configure WiFi with provided credentials"""
        try:
            logger.info(f"Configuring WiFi: {ssid}")
            
            # Create wpa_supplicant configuration
            config = f"""
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
            
            # Write to wpa_supplicant.conf
            conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
            
            # Backup existing config
            subprocess.run(['sudo', 'cp', conf_path, f'{conf_path}.backup'], check=False)
            
            # Write new config
            with open('/tmp/wpa_supplicant.conf', 'w') as f:
                f.write(config)
            
            subprocess.run(['sudo', 'mv', '/tmp/wpa_supplicant.conf', conf_path], check=True)
            subprocess.run(['sudo', 'chmod', '600', conf_path], check=True)
            
            logger.info("WiFi configuration saved")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure WiFi: {e}")
            return False
    
    def scan_networks(self) -> list:
        """Scan for available WiFi networks"""
        try:
            result = subprocess.run(
                ['sudo', 'iwlist', 'wlan0', 'scan'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            # Parse scan results
            networks = []
            current_network = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'ESSID:' in line:
                    ssid = line.split('ESSID:')[1].strip('"')
                    if ssid:
                        current_network['ssid'] = ssid
                        
                elif 'Quality=' in line:
                    # Extract signal strength
                    try:
                        quality = line.split('Quality=')[1].split()[0]
                        current_network['quality'] = quality
                    except:
                        pass
                        
                elif 'Encryption key:' in line:
                    if 'on' in line:
                        current_network['encrypted'] = True
                    else:
                        current_network['encrypted'] = False
                    
                    # Add to list if we have SSID
                    if 'ssid' in current_network:
                        networks.append(current_network.copy())
                        current_network = {}
            
            # Remove duplicates and sort by quality
            unique_networks = {}
            for net in networks:
                ssid = net.get('ssid')
                if ssid and ssid not in unique_networks:
                    unique_networks[ssid] = net
            
            return list(unique_networks.values())
            
        except Exception as e:
            logger.error(f"Error scanning networks: {e}")
            return []
    
    def reboot_system(self):
        """Reboot the system"""
        logger.info("Rebooting system to apply WiFi configuration...")
        try:
            subprocess.run(['sudo', 'reboot'], check=True)
        except Exception as e:
            logger.error(f"Failed to reboot: {e}")
