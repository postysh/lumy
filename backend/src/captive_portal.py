"""Captive Portal - Web interface for WiFi configuration"""

import logging
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from wifi_manager import WiFiManager

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
wifi_manager = WiFiManager()

# HTML template for captive portal
PORTAL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lumy WiFi Setup</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        select, input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .network-list {
            max-height: 200px;
            overflow-y: auto;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 5px;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🖥️ Lumy</h1>
            <p class="subtitle">E-Paper Display Setup</p>
        </div>
        
        <form id="wifiForm">
            <div class="form-group">
                <label for="ssid">WiFi Network</label>
                <select id="ssid" name="ssid" required>
                    <option value="">Loading networks...</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter WiFi password" required>
            </div>
            
            <button type="submit" id="submitBtn">
                Connect to WiFi
            </button>
        </form>
        
        <div class="status" id="status"></div>
        
        <p style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
            After connecting, your device will reboot and display a registration code.
        </p>
    </div>
    
    <script>
        // Load available networks
        async function loadNetworks() {
            try {
                const response = await fetch('/api/scan');
                const networks = await response.json();
                
                const select = document.getElementById('ssid');
                select.innerHTML = '';
                
                if (networks.length === 0) {
                    select.innerHTML = '<option value="">No networks found</option>';
                    return;
                }
                
                networks.forEach(net => {
                    const option = document.createElement('option');
                    option.value = net.ssid;
                    option.textContent = net.ssid + (net.encrypted ? ' 🔒' : '');
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Failed to load networks:', error);
                document.getElementById('ssid').innerHTML = '<option value="">Error loading networks</option>';
            }
        }
        
        // Handle form submission
        document.getElementById('wifiForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const status = document.getElementById('status');
            const ssid = document.getElementById('ssid').value;
            const password = document.getElementById('password').value;
            
            if (!ssid) {
                status.className = 'status error';
                status.style.display = 'block';
                status.textContent = 'Please select a network';
                return;
            }
            
            // Disable form
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Connecting...';
            status.style.display = 'none';
            
            try {
                const response = await fetch('/api/configure', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ ssid, password }),
                });
                
                const result = await response.json();
                
                if (result.success) {
                    status.className = 'status success';
                    status.textContent = '✓ Connected! Device is rebooting...';
                    status.style.display = 'block';
                    
                    // Show success message
                    setTimeout(() => {
                        status.textContent = 'You can close this page. Check your display for the registration code!';
                    }, 3000);
                } else {
                    status.className = 'status error';
                    status.textContent = '✗ Failed: ' + (result.error || 'Unknown error');
                    status.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Connect to WiFi';
                }
            } catch (error) {
                status.className = 'status error';
                status.textContent = '✗ Connection failed. Please try again.';
                status.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Connect to WiFi';
            }
        });
        
        // Load networks on page load
        loadNetworks();
        
        // Refresh networks every 10 seconds
        setInterval(loadNetworks, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main captive portal page"""
    return render_template_string(PORTAL_HTML)

@app.route('/api/scan')
def scan_networks():
    """Scan for available WiFi networks"""
    try:
        networks = wifi_manager.scan_networks()
        return jsonify(networks)
    except Exception as e:
        logger.error(f"Error scanning networks: {e}")
        return jsonify([]), 500

@app.route('/api/configure', methods=['POST'])
def configure_wifi():
    """Configure WiFi with provided credentials"""
    try:
        data = request.get_json()
        ssid = data.get('ssid')
        password = data.get('password')
        
        if not ssid:
            return jsonify({'success': False, 'error': 'SSID required'}), 400
        
        logger.info(f"Configuring WiFi: {ssid}")
        
        # Configure WiFi
        success = wifi_manager.configure_wifi(ssid, password)
        
        if success:
            # Schedule reboot in 2 seconds
            import threading
            threading.Timer(2.0, wifi_manager.reboot_system).start()
            
            return jsonify({'success': True, 'message': 'WiFi configured. Rebooting...'})
        else:
            return jsonify({'success': False, 'error': 'Failed to configure WiFi'}), 500
            
    except Exception as e:
        logger.error(f"Error configuring WiFi: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Catch-all route for captive portal detection
@app.route('/generate_204')
@app.route('/gen_204')
@app.route('/ncsi.txt')
@app.route('/success.txt')
def captive_portal_detection():
    """Handle captive portal detection requests"""
    return index()

def run_portal(host='0.0.0.0', port=80):
    """Run the captive portal server"""
    logger.info(f"Starting captive portal on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    run_portal()
