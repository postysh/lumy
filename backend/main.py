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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.config import Config
from src.display.display_manager import DisplayManager
from src.bluetooth.ble_server import BLEServer
from src.api.server import APIServer
from src.widgets.widget_manager import WidgetManager
from src.cloud_sync import CloudSync
from src.device_registration import DeviceRegistration
from src.wifi_manager import WiFiManager

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
        self.cloud_sync = None
        self.device_registration = None
        self.wifi_manager = WiFiManager()
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Lumy...")

        try:
            # Initialize display manager
            self.display_manager = DisplayManager(self.config)
            await self.display_manager.initialize()
            logger.info("Display manager initialized")
            
            # Check WiFi connectivity
            logger.info("Checking WiFi connectivity...")
            if not self.wifi_manager.is_connected():
                logger.warning("No WiFi connection detected")
                await self._show_ap_mode_message()
                return  # Exit initialization, AP mode will handle setup
            
            logger.info("WiFi connected")
            
            # Check device registration status
            self.device_registration = DeviceRegistration(self.config)
            device_id = self.device_registration.get_or_create_device_id()
            
            # Check if device is registered
            if not await self.device_registration.check_registration_status():
                logger.info("Device not registered - starting registration flow")
                registered = await self.device_registration.initialize_and_register(self.display_manager)
                
                if registered:
                    logger.info("Device successfully registered - showing success message")
                    await self._show_registration_success(self.display_manager)
                    await asyncio.sleep(3)  # Show success message for 3 seconds
                else:
                    logger.error("Device registration failed or timed out")
                    # Continue anyway, allow manual configuration
            else:
                logger.info(f"Device {device_id} is already registered")
            
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
            
            # Initialize cloud sync
            self.cloud_sync = CloudSync(self.config)
            await self.cloud_sync.initialize()
            logger.info("Cloud sync initialized")
            
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
                self.cloud_sync.start(),
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
    
    async def _show_ap_mode_message(self):
        """Show AP mode setup message on display"""
        from PIL import Image, ImageDraw, ImageFont
        
        try:
            # Start AP mode
            ap_ssid = self.wifi_manager.start_ap_mode()
            if not ap_ssid:
                ap_ssid = "Lumy-Setup"
            
            # Create image for AP mode message
            image = Image.new('RGB', (self.display_manager.width, self.display_manager.height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Load fonts (VERY LARGE sizes for 800x480 display readability)
            try:
                font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
                font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
                font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 48)
                font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
            except:
                font_title = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            center_x = self.display_manager.width // 2
            
            # Title
            title_text = "WiFi Setup Required"
            title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text((center_x - title_width // 2, 20), title_text, font=font_title, fill=(0, 0, 0))
            
            # Instructions
            inst1 = "1. Connect to this WiFi:"
            inst1_bbox = draw.textbbox((0, 0), inst1, font=font_medium)
            inst1_width = inst1_bbox[2] - inst1_bbox[0]
            draw.text((center_x - inst1_width // 2, 120), inst1, font=font_medium, fill=(0, 0, 0))
            
            # WiFi name (highlighted)
            ssid_bbox = draw.textbbox((0, 0), ap_ssid, font=font_large)
            ssid_width = ssid_bbox[2] - ssid_bbox[0]
            ssid_height = ssid_bbox[3] - ssid_bbox[1]
            
            # Draw box around SSID
            box_padding = 18
            box_y = 180
            draw.rectangle([
                center_x - ssid_width // 2 - box_padding,
                box_y - box_padding,
                center_x + ssid_width // 2 + box_padding,
                box_y + ssid_height + box_padding
            ], outline=(0, 100, 200), width=5)
            
            draw.text((center_x - ssid_width // 2, box_y), ap_ssid, font=font_large, fill=(0, 100, 200))
            
            # More instructions
            inst2 = "2. Open browser to: 192.168.4.1"
            inst2_bbox = draw.textbbox((0, 0), inst2, font=font_medium)
            inst2_width = inst2_bbox[2] - inst2_bbox[0]
            draw.text((center_x - inst2_width // 2, 285), inst2, font=font_medium, fill=(0, 0, 0))
            
            inst2b = "(or wait for auto-redirect)"
            inst2b_bbox = draw.textbbox((0, 0), inst2b, font=font_small)
            inst2b_width = inst2b_bbox[2] - inst2b_bbox[0]
            draw.text((center_x - inst2b_width // 2, 345), inst2b, font=font_small, fill=(100, 100, 100))
            
            inst3 = "3. Select WiFi & enter password"
            inst3_bbox = draw.textbbox((0, 0), inst3, font=font_medium)
            inst3_width = inst3_bbox[2] - inst3_bbox[0]
            draw.text((center_x - inst3_width // 2, 400), inst3, font=font_medium, fill=(0, 0, 0))
            
            # Display image
            await self.display_manager.display_image(image)
            logger.info(f"AP mode message displayed: {ap_ssid}")
            
            # Start captive portal server
            logger.info("Starting captive portal web server...")
            import subprocess
            import threading
            
            def run_captive_portal():
                """Run Flask captive portal in background thread"""
                try:
                    from src.captive_portal import run_portal
                    run_portal(host='0.0.0.0', port=80)
                except Exception as e:
                    logger.error(f"Captive portal error: {e}")
            
            # Start captive portal in background thread
            portal_thread = threading.Thread(target=run_captive_portal, daemon=True)
            portal_thread.start()
            logger.info("Captive portal running on http://192.168.4.1")
            
            # Keep running to serve the portal
            while True:
                await asyncio.sleep(10)
                # Check if WiFi connected (portal will reboot if successful)
                if self.wifi_manager.is_connected():
                    logger.info("WiFi connected! Rebooting...")
                    subprocess.run(['sudo', 'reboot'])
            
        except Exception as e:
            logger.error(f"Error showing AP mode message: {e}", exc_info=True)
    
    async def _show_registration_success(self, display_manager):
        """Show registration success message"""
        from PIL import Image, ImageDraw, ImageFont
        
        try:
            # Create white background
            image = Image.new('RGB', (display_manager.width, display_manager.height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Load fonts (VERY LARGE sizes for 800x480 readability)
            try:
                font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 82)
                font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 50)
            except:
                font_title = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            center_x = display_manager.width // 2
            
            # Draw success message
            title_text = "Registration Successful!"
            title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text((center_x - title_width // 2, 130), title_text, font=font_title, fill=(0, 150, 0))
            
            # Draw subtitle
            subtitle_text = "Loading your widgets..."
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_medium)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            draw.text((center_x - subtitle_width // 2, 250), subtitle_text, font=font_medium, fill=(0, 0, 0))
            
            # Display image
            await display_manager.display_image(image)
            logger.info("Registration success message displayed")
            
        except Exception as e:
            logger.error(f"Error showing registration success: {e}", exc_info=True)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Lumy...")
        
        self.running = False
        
        # Stop all services
        if self.cloud_sync:
            await self.cloud_sync.stop()
        
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
