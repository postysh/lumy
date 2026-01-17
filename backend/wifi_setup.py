#!/usr/bin/python3
"""
Simple WiFi configuration web server
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json

class WiFiHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Serve the configuration page"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lumy WiFi Setup</title>
    <style>
        body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        input, select { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; }
        button { width: 100%; padding: 15px; background: #007bff; color: white; border: none; font-size: 18px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .network { padding: 10px; margin: 5px 0; border: 1px solid #ddd; cursor: pointer; }
        .network:hover { background: #f0f0f0; }
    </style>
</head>
<body>
    <h1>Lumy WiFi Setup</h1>
    <p>Select your WiFi network and enter the password:</p>
    
    <form id="wifiForm" method="POST" action="/configure">
        <div id="networks">Loading networks...</div>
        <input type="text" id="ssid" name="ssid" placeholder="WiFi Network" readonly required>
        <input type="password" name="password" placeholder="WiFi Password" required>
        <button type="submit">Connect</button>
    </form>
    
    <script>
        // Load available networks
        fetch('/scan')
            .then(r => r.json())
            .then(networks => {
                const div = document.getElementById('networks');
                div.innerHTML = '<h3>Available Networks:</h3>';
                networks.forEach(ssid => {
                    const net = document.createElement('div');
                    net.className = 'network';
                    net.textContent = ssid;
                    net.onclick = () => document.getElementById('ssid').value = ssid;
                    div.appendChild(net);
                });
            });
    </script>
</body>
</html>'''
            self.wfile.write(html.encode())
            
        elif self.path == '/scan':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Scan for networks
            try:
                result = subprocess.run(
                    ['iwlist', 'wlan0', 'scan'],
                    capture_output=True,
                    text=True
                )
                
                networks = []
                for line in result.stdout.split('\n'):
                    if 'ESSID:' in line:
                        ssid = line.split('ESSID:')[1].strip().strip('"')
                        if ssid and ssid not in networks:
                            networks.append(ssid)
                
                self.wfile.write(json.dumps(networks).encode())
            except:
                self.wfile.write(json.dumps([]).encode())
    
    def do_POST(self):
        """Handle WiFi configuration"""
        if self.path == '/configure':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            
            # Parse form data
            params = {}
            for item in post_data.split('&'):
                key, value = item.split('=')
                params[key] = value.replace('+', ' ')
            
            ssid = params.get('ssid', '')
            password = params.get('password', '')
            
            if ssid:
                # Configure WiFi
                wpa_conf = f'''
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
'''
                with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
                    f.write(wpa_conf)
                
                # Remove AP mode config from dhcpcd
                with open('/etc/dhcpcd.conf', 'r') as f:
                    lines = f.readlines()
                
                with open('/etc/dhcpcd.conf', 'w') as f:
                    skip = False
                    for line in lines:
                        if 'interface wlan0' in line:
                            skip = True
                        elif skip and line.strip() and not line.startswith(' '):
                            skip = False
                        
                        if not skip:
                            f.write(line)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = '''<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Success</title>
    <style>
        body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; }
        h1 { color: #28a745; }
    </style>
</head>
<body>
    <h1>✓ WiFi Configured!</h1>
    <p>Device is rebooting and will connect to your WiFi network.</p>
    <p>Check the display for your registration code.</p>
</body>
</html>'''
                self.wfile.write(html.encode())
                
                # Reboot to apply changes
                subprocess.Popen(['shutdown', '-r', '+1'])

if __name__ == '__main__':
    print("Starting WiFi setup server on port 80...")
    server = HTTPServer(('0.0.0.0', 80), WiFiHandler)
    server.serve_forever()
