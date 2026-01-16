"""Display manager for E-Paper screen control"""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw
import importlib

logger = logging.getLogger(__name__)


class DisplayManager:
    """Manages E-Paper display operations"""
    
    def __init__(self, config):
        self.config = config
        self.epd = None
        self.current_image: Optional[Image.Image] = None
        self.width = config.display_width
        self.height = config.display_height
        self.initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the E-Paper display"""
        try:
            # Import the Waveshare e-Paper library
            # Model: epd_7in3e (7.3inch E-Ink display HAT E - 1872×1404)
            model_name = self.config.get('display.model', 'epd_7in3e')
            
            try:
                # Try to import Waveshare library (unmodified from official repo)
                epd_module = importlib.import_module(f'waveshare_epd.{model_name}')
                self.epd = epd_module.EPD()
                
                logger.info(f"Initializing E-Paper display: {model_name}")
                self.epd.init()
                
                # Clear the display on first init
                logger.info("Clearing display...")
                self.epd.Clear()
                
                self.initialized = True
                logger.info("Display initialized successfully")
                
            except ImportError:
                logger.warning("Waveshare library not found, running in mock mode")
                self.epd = MockEPD(self.width, self.height)
                self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}", exc_info=True)
            # Fallback to mock display for development
            self.epd = MockEPD(self.width, self.height)
            self.initialized = True
    
    async def display_image(self, image: Image.Image, force_refresh: bool = False):
        """Display an image on the E-Paper screen"""
        async with self._lock:
            try:
                if not self.initialized:
                    logger.error("Display not initialized")
                    return False
                
                # Wake up display if it was sleeping (re-init SPI connection)
                try:
                    self.epd.init()
                    logger.debug("Display re-initialized for new image")
                except Exception as init_error:
                    logger.warning(f"Display init warning: {init_error}")
                
                # Ensure image is correct size
                if image.size != (self.width, self.height):
                    logger.info(f"Resizing image from {image.size} to {self.width}x{self.height}")
                    image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
                
                # Convert to appropriate color mode for the display
                # 7.3inch e-Paper HAT (E) supports 7 colors
                image = self._convert_to_display_mode(image)
                
                # Display the image
                logger.info("Displaying image on E-Paper...")
                
                # Get image buffer
                buffer = self.epd.getbuffer(image)
                
                # Display
                self.epd.display(buffer)
                
                # Sleep the display to save power
                if self.config.get('display.sleep_after_refresh', True):
                    await asyncio.sleep(1)  # Wait for refresh to complete
                    self.epd.sleep()
                
                self.current_image = image
                logger.info("Image displayed successfully")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to display image: {e}", exc_info=True)
                return False
    
    def _convert_to_display_mode(self, image: Image.Image) -> Image.Image:
        """Convert image to display color mode"""
        # 7.3inch e-Paper HAT (E) supports 7 colors:
        # Black, White, Green, Blue, Red, Yellow, Orange
        # For now, we'll use a simple conversion
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    async def clear_display(self):
        """Clear the E-Paper display"""
        async with self._lock:
            try:
                logger.info("Clearing display...")
                self.epd.Clear()
                self.current_image = None
                
                if self.config.get('display.sleep_after_refresh', True):
                    await asyncio.sleep(1)
                    self.epd.sleep()
                
                return True
            except Exception as e:
                logger.error(f"Failed to clear display: {e}", exc_info=True)
                return False
    
    def create_canvas(self) -> Image.Image:
        """Create a blank canvas for drawing"""
        return Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
    
    async def cleanup(self):
        """Clean up display resources"""
        try:
            if self.epd and self.initialized:
                logger.info("Cleaning up display...")
                self.epd.sleep()
                # Note: Don't call Clear() on cleanup to preserve last image
        except Exception as e:
            logger.error(f"Error during display cleanup: {e}", exc_info=True)


class MockEPD:
    """Mock E-Paper display for development/testing"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        logger.info(f"Using mock E-Paper display ({width}x{height})")
    
    def init(self):
        logger.info("Mock EPD: init")
    
    def Clear(self):
        logger.info("Mock EPD: clear")
    
    def getbuffer(self, image: Image.Image):
        logger.info(f"Mock EPD: getbuffer for image {image.size}")
        return image.tobytes()
    
    def display(self, buffer):
        logger.info(f"Mock EPD: display {len(buffer)} bytes")
    
    def sleep(self):
        logger.info("Mock EPD: sleep")
