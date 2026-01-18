"""
API Client for communicating with Lumy dashboard
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LumyAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        })
    
    def register_device(self, device_id: str, registration_code: str, expires_in: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Register device with the API and create a registration code
        
        Args:
            device_id: Unique device identifier (MAC address)
            registration_code: 6-character code for user to enter
            expires_in: Code expiry time in seconds (default 1 hour)
            
        Returns:
            dict with success, code, and expires_at
        """
        try:
            response = self.session.post(
                f'{self.base_url}/api/devices/register',
                json={
                    'device_id': device_id,
                    'registration_code': registration_code,
                    'expires_in': expires_in
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Device registered successfully: {device_id}")
                return data
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return None
    
    def check_claim_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if the device has been claimed by a user
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            dict with device info if claimed, None if not claimed
        """
        try:
            # Check registration_codes table via the status endpoint
            response = self.session.get(
                f'{self.base_url}/api/devices/{device_id}/status',
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('is_claimed'):
                    logger.info(f"Device {device_id} has been claimed!")
                    return data
                return None
            else:
                logger.debug(f"Status check: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking claim status: {e}")
            return None
    
    def get_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch device configuration and widgets
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            dict with display config and widgets
        """
        try:
            response = self.session.get(
                f'{self.base_url}/api/devices/{device_id}/config',
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            
            if response.status_code == 200:
                config = response.json()
                logger.info(f"Config fetched for device {device_id}")
                return config
            else:
                logger.error(f"Failed to fetch config: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            return None
    
    def send_heartbeat(self, device_id: str) -> bool:
        """
        Send heartbeat to update last_seen timestamp
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.post(
                f'{self.base_url}/api/devices/{device_id}/status',
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={'status': 'online'},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False
