"""
Device Manager - Handles device ID and state management
"""
import os
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DeviceManager:
    def __init__(self, device_id_file: str = '/etc/lumy/device_id'):
        self.device_id_file = device_id_file
        self._device_id = None
    
    def get_device_id(self) -> str:
        """
        Get or create unique device ID
        
        Returns:
            Unique device identifier
        """
        if self._device_id:
            return self._device_id
        
        # Try to load existing device ID
        if os.path.exists(self.device_id_file):
            try:
                with open(self.device_id_file, 'r') as f:
                    self._device_id = f.read().strip()
                    logger.info(f"Loaded device ID: {self._device_id}")
                    return self._device_id
            except Exception as e:
                logger.warning(f"Could not read device ID file: {e}")
        
        # Generate new device ID from MAC address or UUID
        self._device_id = self._generate_device_id()
        
        # Save it
        self._save_device_id(self._device_id)
        
        return self._device_id
    
    def _generate_device_id(self) -> str:
        """
        Generate a unique device ID
        Uses MAC address if available, otherwise generates UUID
        """
        try:
            # Try to get MAC address
            mac = self._get_mac_address()
            if mac:
                device_id = f"lumy-{mac}"
                logger.info(f"Generated device ID from MAC: {device_id}")
                return device_id
        except Exception as e:
            logger.warning(f"Could not get MAC address: {e}")
        
        # Fallback to UUID
        device_id = f"lumy-{uuid.uuid4().hex[:12]}"
        logger.info(f"Generated device ID from UUID: {device_id}")
        return device_id
    
    def _get_mac_address(self) -> Optional[str]:
        """Get MAC address of eth0 or wlan0"""
        try:
            # Try wlan0 first
            with open('/sys/class/net/wlan0/address', 'r') as f:
                mac = f.read().strip().replace(':', '')
                return mac
        except:
            pass
        
        try:
            # Try eth0
            with open('/sys/class/net/eth0/address', 'r') as f:
                mac = f.read().strip().replace(':', '')
                return mac
        except:
            pass
        
        return None
    
    def _save_device_id(self, device_id: str) -> bool:
        """Save device ID to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.device_id_file), exist_ok=True)
            
            with open(self.device_id_file, 'w') as f:
                f.write(device_id)
            
            logger.info(f"Saved device ID to {self.device_id_file}")
            return True
            
        except PermissionError:
            # If we can't write to /etc/lumy/, use home directory
            alt_path = os.path.expanduser('~/.lumy_device_id')
            try:
                with open(alt_path, 'w') as f:
                    f.write(device_id)
                self.device_id_file = alt_path
                logger.info(f"Saved device ID to {alt_path}")
                return True
            except Exception as e:
                logger.error(f"Could not save device ID: {e}")
                return False
        except Exception as e:
            logger.error(f"Error saving device ID: {e}")
            return False
