#!/usr/bin/env python3
"""
Lumy - Bluetooth-controlled E-Paper Display System
Main entry point for the application
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

from src.config import Config
from src.display.display_manager import DisplayManager
from src.bluetooth.ble_server import BLEServer
from src.api.server import APIServer
from src.widgets.widget_manager import WidgetManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lumy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class LumyApp:
    """Main application class for Lumy"""
    
    def __init__(self):
        self.config = Config()
        self.display_manager = None
        self.ble_server = None
        self.api_server = None
        self.widget_manager = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Lumy...")
        
        try:
            # Initialize display manager
            self.display_manager = DisplayManager(self.config)
            await self.display_manager.initialize()
            logger.info("Display manager initialized")
            
            # Initialize widget manager
            self.widget_manager = WidgetManager(self.config, self.display_manager)
            await self.widget_manager.initialize()
            logger.info("Widget manager initialized")
            
            # Initialize BLE server
            self.ble_server = BLEServer(
                self.config,
                self.display_manager,
                self.widget_manager
            )
            await self.ble_server.initialize()
            logger.info("BLE server initialized")
            
            # Initialize API server
            self.api_server = APIServer(
                self.config,
                self.display_manager,
                self.widget_manager,
                self.ble_server
            )
            logger.info("API server initialized")
            
            logger.info("Lumy initialization complete!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Lumy: {e}", exc_info=True)
            raise
    
    async def start(self):
        """Start all services"""
        logger.info("Starting Lumy services...")
        
        self.running = True
        
        try:
            # Start services concurrently
            await asyncio.gather(
                self.ble_server.start(),
                self.api_server.start(),
                self.widget_manager.start(),
                self._main_loop()
            )
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            await self.shutdown()
    
    async def _main_loop(self):
        """Main application loop"""
        logger.info("Main loop started")
        
        while self.running:
            try:
                # Periodic tasks can go here
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(5)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Lumy...")
        
        self.running = False
        
        # Stop all services
        if self.api_server:
            await self.api_server.stop()
        
        if self.ble_server:
            await self.ble_server.stop()
        
        if self.widget_manager:
            await self.widget_manager.stop()
        
        if self.display_manager:
            await self.display_manager.cleanup()
        
        logger.info("Lumy shutdown complete")


async def main():
    """Main entry point"""
    app = LumyApp()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(app.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await app.initialize()
        await app.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await app.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
