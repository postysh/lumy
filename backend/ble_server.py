#!/usr/bin/python3
"""
Lumy Bluetooth LE Server
Receives WiFi credentials from macOS/iOS app
"""

import sys
import json
import subprocess
import time
from bluezero import adapter, peripheral

# BLE Service and Characteristic UUIDs (must match Swift app)
LUMY_SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
WIFI_CREDENTIAL_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef1'
WIFI_STATUS_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef2'

class LumyBLEServer:
    def __init__(self):
        self.adapter = adapter.Adapter()
        self.wifi_credentials = None
        self.status = "Waiting for WiFi credentials..."
        
    def on_wifi_credentials_write(self, value):
        """Called when WiFi credentials are received"""
        try:
            # Decode JSON credentials
            json_str = bytes(value).decode('utf-8')
            self.wifi_credentials = json.loads(json_str)
            
            ssid = self.wifi_credentials.get('ssid', '')
            password = self.wifi_credentials.get('password', '')
            
            print(f"Received WiFi credentials:")
            print(f"  SSID: {ssid}")
            print(f"  Password: {'*' * len(password)}")
            
            # Configure WiFi
            self.status = f"Connecting to {ssid}..."
            self.configure_wifi(ssid, password)
            
        except Exception as e:
            print(f"Error processing credentials: {e}")
            self.status = f"Error: {str(e)}"
    
    def configure_wifi(self, ssid, password):
        """Configure WiFi with received credentials"""
        try:
            # Create wpa_supplicant.conf
            wpa_conf = f'''country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
'''
            
            # Write configuration
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
                f.write(wpa_conf)
            
            print("WiFi configuration written")
            self.status = "WiFi configured! Rebooting..."
            
            # Give BLE time to send status
            time.sleep(2)
            
            # Reboot to apply WiFi
            subprocess.run(['sudo', 'reboot'])
            
        except Exception as e:
            print(f"Error configuring WiFi: {e}")
            self.status = f"Configuration error: {str(e)}"
    
    def get_status(self):
        """Return current status"""
        return self.status.encode('utf-8')
    
    def start(self):
        """Start the BLE server"""
        print("Starting Lumy BLE Server...")
        print(f"Device Name: {self.adapter.name}")
        print(f"Device Address: {self.adapter.address}")
        
        # Create BLE peripheral
        periph = peripheral.Peripheral(
            self.adapter.address,
            local_name='Lumy-Setup'
        )
        
        # Add Lumy service
        periph.add_service(srv_id=1, uuid=LUMY_SERVICE_UUID, primary=True)
        
        # Add WiFi Credential characteristic (writable)
        periph.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=WIFI_CREDENTIAL_CHAR_UUID,
            value=[],
            notifying=False,
            flags=['write'],
            write_callback=self.on_wifi_credentials_write
        )
        
        # Add Status characteristic (readable, notifiable)
        periph.add_characteristic(
            srv_id=1,
            chr_id=2,
            uuid=WIFI_STATUS_CHAR_UUID,
            value=[],
            notifying=True,
            flags=['read', 'notify'],
            read_callback=self.get_status
        )
        
        # Start advertising
        periph.publish()
        
        print("BLE server started and advertising...")
        print("Waiting for connections...")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == '__main__':
    server = LumyBLEServer()
    server.start()
