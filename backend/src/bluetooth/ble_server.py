"""Bluetooth Low Energy server for iPhone communication"""

import asyncio
import json
import logging
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from bleak import BleakGATTCharacteristic, BleakGATTServiceCollection
    from bleak.backends.characteristic import GattCharacteristicsFlags
    BLEAK_AVAILABLE = True
except ImportError:
    logger.warning("Bleak not available, BLE will run in mock mode")
    BLEAK_AVAILABLE = False


@dataclass
class BLEMessage:
    """BLE message structure"""
    command: str
    data: Dict[str, Any]
    request_id: Optional[str] = None


class BLEServer:
    """Bluetooth LE server for remote control"""
    
    def __init__(self, config, display_manager, widget_manager):
        self.config = config
        self.display_manager = display_manager
        self.widget_manager = widget_manager
        
        self.service_uuid = config.get('bluetooth.service_uuid')
        self.tx_char_uuid = config.get('bluetooth.tx_characteristic_uuid')
        self.rx_char_uuid = config.get('bluetooth.rx_characteristic_uuid')
        self.device_name = config.get('bluetooth.device_name')
        
        self.connected_devices = set()
        self.message_handlers: Dict[str, Callable] = {}
        self._running = False
        
        # Register command handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message handlers"""
        self.message_handlers = {
            'ping': self._handle_ping,
            'refresh_display': self._handle_refresh_display,
            'clear_display': self._handle_clear_display,
            'update_widget': self._handle_update_widget,
            'get_status': self._handle_get_status,
            'set_config': self._handle_set_config,
            'trigger_app': self._handle_trigger_app,
        }
    
    async def initialize(self):
        """Initialize BLE server"""
        if not self.config.bluetooth_enabled:
            logger.info("Bluetooth is disabled in config")
            return
        
        try:
            if BLEAK_AVAILABLE:
                logger.info("Initializing BLE server...")
                # Setup BLE GATT server
                # Note: On Linux, this typically requires BlueZ and proper permissions
                logger.info(f"BLE Device Name: {self.device_name}")
                logger.info(f"Service UUID: {self.service_uuid}")
            else:
                logger.info("Running BLE in mock mode")
                
        except Exception as e:
            logger.error(f"Failed to initialize BLE server: {e}", exc_info=True)
    
    async def start(self):
        """Start BLE advertising and services"""
        if not self.config.bluetooth_enabled:
            return
        
        self._running = True
        logger.info("Starting BLE server...")
        
        try:
            # In production, this would start the BLE GATT server
            # For now, we'll use a mock implementation
            await self._run_mock_server()
        except Exception as e:
            logger.error(f"BLE server error: {e}", exc_info=True)
    
    async def _run_mock_server(self):
        """Mock BLE server for development"""
        logger.info("BLE mock server running...")
        
        while self._running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stop BLE server"""
        logger.info("Stopping BLE server...")
        self._running = False
    
    async def send_message(self, message: BLEMessage) -> bool:
        """Send message to connected devices"""
        try:
            payload = json.dumps({
                'command': message.command,
                'data': message.data,
                'request_id': message.request_id
            })
            
            logger.info(f"Sending BLE message: {message.command}")
            # In production, send via BLE characteristic
            return True
            
        except Exception as e:
            logger.error(f"Failed to send BLE message: {e}")
            return False
    
    async def _handle_message(self, data: bytes):
        """Handle incoming BLE message"""
        try:
            message_str = data.decode('utf-8')
            message_data = json.loads(message_str)
            
            command = message_data.get('command')
            request_id = message_data.get('request_id')
            payload = message_data.get('data', {})
            
            logger.info(f"Received BLE command: {command}")
            
            # Handle command
            handler = self.message_handlers.get(command)
            if handler:
                response = await handler(payload)
                
                # Send response
                if request_id:
                    await self.send_message(BLEMessage(
                        command=f"{command}_response",
                        data=response,
                        request_id=request_id
                    ))
            else:
                logger.warning(f"Unknown command: {command}")
                
        except Exception as e:
            logger.error(f"Error handling BLE message: {e}", exc_info=True)
    
    # Command Handlers
    
    async def _handle_ping(self, data: Dict) -> Dict:
        """Handle ping command"""
        return {'status': 'pong', 'timestamp': asyncio.get_event_loop().time()}
    
    async def _handle_refresh_display(self, data: Dict) -> Dict:
        """Handle display refresh command"""
        success = await self.widget_manager.render_display()
        return {'status': 'success' if success else 'error'}
    
    async def _handle_clear_display(self, data: Dict) -> Dict:
        """Handle clear display command"""
        success = await self.display_manager.clear_display()
        return {'status': 'success' if success else 'error'}
    
    async def _handle_update_widget(self, data: Dict) -> Dict:
        """Handle widget update command"""
        widget_id = data.get('widget_id')
        widget_data = data.get('data', {})
        
        success = await self.widget_manager.update_widget(widget_id, widget_data)
        return {'status': 'success' if success else 'error'}
    
    async def _handle_get_status(self, data: Dict) -> Dict:
        """Handle status request"""
        return {
            'status': 'online',
            'display_initialized': self.display_manager.initialized,
            'widgets': await self.widget_manager.get_widget_status(),
            'connected_clients': len(self.connected_devices)
        }
    
    async def _handle_set_config(self, data: Dict) -> Dict:
        """Handle configuration update"""
        try:
            for key, value in data.items():
                self.config.set(key, value)
            self.config.save()
            return {'status': 'success'}
        except Exception as e:
            logger.error(f"Failed to set config: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _handle_trigger_app(self, data: Dict) -> Dict:
        """Handle app trigger command"""
        app_name = data.get('app_name')
        app_data = data.get('data', {})
        
        # Trigger specific app/widget
        success = await self.widget_manager.trigger_widget(app_name, app_data)
        return {'status': 'success' if success else 'error'}
