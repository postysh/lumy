#!/usr/bin/python3
"""
Lumy - E-Paper Display Manager
Minimal, working version
"""

import sys
sys.path.append('/usr/local/lib/python3.11/dist-packages')

import os
import asyncio
import logging
from pathlib import Path
from waveshare_epd import epd7in3e
from PIL import Image, ImageDraw, ImageFont

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('lumy')

class LumyDisplay:
    """Main Lumy Display Manager"""
    
    def __init__(self):
        self.epd = None
        self.width = 800
        self.height = 480
        self.device_id = self.get_device_id()
        self.registration_code = self.generate_registration_code()
        
    def get_device_id(self):
        """Get unique device ID from MAC address"""
        try:
            with open('/sys/class/net/wlan0/address', 'r') as f:
                mac = f.read().strip().replace(':', '')[-6:].upper()
                return f"LUMY-{mac}"
        except:
            import random
            return f"LUMY-{''.join(random.choices('0123456789ABCDEF', k=6))}"
    
    def generate_registration_code(self):
        """Generate 6-character registration code"""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1')
        return ''.join(random.choices(chars, k=6))
    
    def init_display(self):
        """Initialize e-Paper display"""
        try:
            logger.info("Initializing display...")
            self.epd = epd7in3e.EPD()
            self.epd.init()
            self.epd.Clear()
            logger.info("Display initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            return False
    
    def show_welcome_screen(self):
        """Display welcome screen with registration code"""
        try:
            logger.info("Creating welcome screen...")
            
            # Create white background
            image = Image.new('RGB', (self.width, self.height), 0xFFFFFF)
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            try:
                font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
                font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
                font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
                font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
            except:
                logger.warning("Could not load fonts, using default")
                font_title = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Calculate center
            center_x = self.width // 2
            
            # Draw title
            title = "Welcome to Lumy"
            bbox = draw.textbbox((0, 0), title, font=font_title)
            title_width = bbox[2] - bbox[0]
            draw.text((center_x - title_width // 2, 30), title, font=font_title, fill=0x000000)
            
            # Draw instructions
            inst1 = "Register at:"
            bbox = draw.textbbox((0, 0), inst1, font=font_medium)
            inst1_width = bbox[2] - bbox[0]
            draw.text((center_x - inst1_width // 2, 140), inst1, font=font_medium, fill=0x000000)
            
            inst2 = "lumy-beta.vercel.app"
            bbox = draw.textbbox((0, 0), inst2, font=font_medium)
            inst2_width = bbox[2] - bbox[0]
            draw.text((center_x - inst2_width // 2, 200), inst2, font=font_medium, fill=0x0000FF)
            
            # Draw registration code in a box
            code_y = 290
            bbox = draw.textbbox((0, 0), self.registration_code, font=font_large)
            code_width = bbox[2] - bbox[0]
            code_height = bbox[3] - bbox[1]
            
            # Draw box
            padding = 20
            draw.rectangle([
                center_x - code_width // 2 - padding,
                code_y - padding,
                center_x + code_width // 2 + padding,
                code_y + code_height + padding
            ], outline=0xFF6600, width=4)
            
            # Draw code
            draw.text((center_x - code_width // 2, code_y), self.registration_code, font=font_large, fill=0xFF6600)
            
            # Draw device ID
            device_text = f"Device: {self.device_id}"
            bbox = draw.textbbox((0, 0), device_text, font=font_small)
            device_width = bbox[2] - bbox[0]
            draw.text((center_x - device_width // 2, 420), device_text, font=font_small, fill=0x808080)
            
            # Display image
            logger.info("Displaying welcome screen...")
            self.epd.display(self.epd.getbuffer(image))
            
            logger.info(f"Welcome screen displayed - Code: {self.registration_code}, Device: {self.device_id}")
            
        except Exception as e:
            logger.error(f"Error showing welcome screen: {e}", exc_info=True)
    
    def sleep(self):
        """Put display to sleep"""
        try:
            if self.epd:
                logger.info("Putting display to sleep...")
                self.epd.sleep()
        except Exception as e:
            logger.error(f"Error putting display to sleep: {e}")


async def main():
    """Main application loop"""
    logger.info("Starting Lumy Display Service...")
    logger.info(f"Python path: {sys.path}")
    
    display = LumyDisplay()
    
    # Initialize display
    if not display.init_display():
        logger.error("Failed to initialize display - exiting")
        return
    
    # Show welcome screen
    display.show_welcome_screen()
    
    # Put display to sleep
    display.sleep()
    
    logger.info("Lumy Display Service started successfully")
    logger.info(f"Registration Code: {display.registration_code}")
    logger.info(f"Device ID: {display.device_id}")
    
    # Keep running
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
