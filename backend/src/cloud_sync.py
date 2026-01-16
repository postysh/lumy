"""Cloud synchronization service for communicating with Vercel"""

import asyncio
import logging
import os
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudSync:
    """Handles communication between Pi and Vercel cloud"""
    
    def __init__(self, config):
        self.config = config
        self.api_url = os.getenv('LUMY_API_URL', '')
        self.api_key = os.getenv('LUMY_API_KEY', '')
        self.device_id = os.getenv('LUMY_DEVICE_ID', 'lumy-default')
        self.poll_interval = config.get('cloud.poll_interval', 60)  # seconds
        self.enabled = bool(self.api_url and self.api_key)
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self._last_config_hash = None
        
    async def initialize(self):
        """Initialize cloud sync service"""
        if not self.enabled:
            logger.warning("Cloud sync disabled - LUMY_API_URL or LUMY_API_KEY not set")
            return
        
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        logger.info(f"Cloud sync initialized - Device ID: {self.device_id}")
        logger.info(f"API URL: {self.api_url}")
    
    async def start(self):
        """Start polling loop"""
        if not self.enabled:
            logger.info("Cloud sync not enabled")
            return
        
        self.running = True
        logger.info(f"Starting cloud sync (poll interval: {self.poll_interval}s)")
        
        # Initial sync
        await self.sync_config()
        await self.send_status("online")
        
        # Start polling loop
        asyncio.create_task(self._poll_loop())
    
    async def stop(self):
        """Stop cloud sync"""
        self.running = False
        
        if self.enabled:
            await self.send_status("offline")
        
        if self.session:
            await self.session.close()
        
        logger.info("Cloud sync stopped")
    
    async def _poll_loop(self):
        """Background polling loop"""
        while self.running:
            try:
                # Fetch config updates
                await self.sync_config()
                
                # Send status update
                await self.send_status("online")
                
            except Exception as e:
                logger.error(f"Poll loop error: {e}")
            
            # Wait for next poll
            await asyncio.sleep(self.poll_interval)
    
    async def sync_config(self) -> Optional[Dict[str, Any]]:
        """Fetch configuration from cloud"""
        if not self.enabled:
            return None
        
        try:
            url = f"{self.api_url}/devices/{self.device_id}/config"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    config = await response.json()
                    
                    # Check if config changed
                    config_hash = hash(str(config))
                    if config_hash != self._last_config_hash:
                        logger.info("Config updated from cloud")
                        self._last_config_hash = config_hash
                        await self._apply_config(config)
                    
                    return config
                
                elif response.status == 404:
                    logger.warning(f"Device not registered: {self.device_id}")
                    return None
                
                else:
                    logger.error(f"Failed to fetch config: HTTP {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            return None
    
    async def _apply_config(self, config: Dict[str, Any]):
        """Apply configuration received from cloud"""
        try:
            # Update display settings
            if 'display' in config:
                display_config = config['display']
                self.config.set('display.refresh_interval', 
                              display_config.get('refresh_interval', 300))
            
            # Update widget configuration
            if 'widgets' in config:
                for widget_config in config['widgets']:
                    widget_id = widget_config['id']
                    enabled = widget_config.get('enabled', True)
                    widget_settings = widget_config.get('config', {})
                    
                    # Update widget config
                    self.config.set(f'widgets.{widget_id}.enabled', enabled)
                    for key, value in widget_settings.items():
                        self.config.set(f'widgets.{widget_id}.{key}', value)
            
            logger.info("Configuration applied from cloud")
            
        except Exception as e:
            logger.error(f"Error applying config: {e}")
    
    async def send_status(self, status: str):
        """Send device status to cloud"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.api_url}/devices/{self.device_id}/status"
            
            # Gather system info
            import psutil
            
            data = {
                'device_id': self.device_id,
                'status': status,
                'last_refresh': datetime.utcnow().isoformat(),
                'system': {
                    'cpu_temp': self._get_cpu_temp(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'uptime': int(datetime.now().timestamp() - psutil.boot_time())
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    logger.debug("Status sent to cloud")
                else:
                    logger.warning(f"Failed to send status: HTTP {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending status: {e}")
    
    async def send_log(self, level: str, message: str, details: Dict = None):
        """Send log entry to cloud"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.api_url}/devices/{self.device_id}/logs"
            
            data = {
                'device_id': self.device_id,
                'level': level,
                'message': message,
                'details': details or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status != 200:
                    logger.debug(f"Failed to send log: HTTP {response.status}")
        
        except Exception as e:
            logger.debug(f"Error sending log: {e}")
    
    def _get_cpu_temp(self) -> Optional[float]:
        """Get CPU temperature (Raspberry Pi)"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
                return round(temp, 1)
        except:
            return None
    
    async def trigger_refresh(self):
        """Triggered when display refreshes"""
        if self.enabled:
            await self.send_status("online")
