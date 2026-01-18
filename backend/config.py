"""
Configuration for Lumy backend
"""
import os

# Try to load .env file if it exists
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# API Configuration
API_BASE_URL = os.getenv('LUMY_API_URL', 'https://lumy-hzo8z4iqa-postysh.vercel.app')
API_KEY = os.getenv('LUMY_API_KEY', 'ZgIj4BaD25SyRVeQ9j0oh3ebpp0tQtgv')

# Device Configuration
DEVICE_ID_FILE = '/etc/lumy/device_id'
POLL_INTERVAL = 10  # seconds between polling for claim status
CONFIG_REFRESH_INTERVAL = 300  # seconds between config refreshes (5 minutes)

# Display Configuration
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
