"""
Lumy Display Manager - Handles e-paper display updates
Waveshare 7.3inch e-Paper HAT (E) - 800x480
"""
import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont
import logging

# Add waveshare library path
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
if os.path.exists(lib_path):
    sys.path.append(lib_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DisplayManager:
    def __init__(self):
        """Initialize the e-paper display"""
        self.width = 800
        self.height = 480
        self.epd = None
        
        try:
            # Import Waveshare library
            from waveshare_epd import epd7in3e
            self.epd = epd7in3e.EPD()
            logger.info("Initializing e-paper display...")
            self.epd.init()
            logger.info("Display initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import Waveshare library: {e}")
            logger.error("Make sure the library is in the 'lib' folder")
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
    
    def clear(self):
        """Clear the display to white"""
        if self.epd:
            logger.info("Clearing display...")
            self.epd.Clear()
            logger.info("Display cleared")
    
    def show_welcome_screen(self, registration_code):
        """
        Display the Lumy welcome screen with registration code
        
        Args:
            registration_code (str): The device registration code
        """
        if not self.epd:
            logger.error("Display not initialized")
            return
        
        # Create a blank white image
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Try to load fonts, fall back to default if not available
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
            subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
            code_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 100)
            instruction_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}, using default")
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            code_font = ImageFont.load_default()
            instruction_font = ImageFont.load_default()
        
        # Draw "Welcome to Lumy" title centered at top
        title_text = "Welcome to Lumy"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 60), title_text, font=title_font, fill='black')
        
        # Draw subtitle
        subtitle_text = "Your Smart Display"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.width - subtitle_width) // 2
        draw.text((subtitle_x, 160), subtitle_text, font=subtitle_font, fill='black')
        
        # Draw registration code in a box
        code_y = 250
        box_padding = 20
        code_bbox = draw.textbbox((0, 0), registration_code, font=code_font)
        code_width = code_bbox[2] - code_bbox[0]
        code_height = code_bbox[3] - code_bbox[1]
        code_x = (self.width - code_width) // 2
        
        # Draw rounded rectangle background for code
        box_coords = [
            code_x - box_padding,
            code_y - box_padding,
            code_x + code_width + box_padding,
            code_y + code_height + box_padding
        ]
        draw.rectangle(box_coords, outline='black', width=4)
        
        # Draw the code
        draw.text((code_x, code_y), registration_code, font=code_font, fill='black')
        
        # Draw instructions
        instruction_text = "Visit your dashboard and click 'Add Device'"
        instruction_bbox = draw.textbbox((0, 0), instruction_text, font=instruction_font)
        instruction_width = instruction_bbox[2] - instruction_bbox[0]
        instruction_x = (self.width - instruction_width) // 2
        draw.text((instruction_x, 380), instruction_text, font=instruction_font, fill='black')
        
        # Draw second line of instructions
        instruction_text2 = "Enter this code to register your display"
        instruction_bbox2 = draw.textbbox((0, 0), instruction_text2, font=instruction_font)
        instruction_width2 = instruction_bbox2[2] - instruction_bbox2[0]
        instruction_x2 = (self.width - instruction_width2) // 2
        draw.text((instruction_x2, 420), instruction_text2, font=instruction_font, fill='black')
        
        # Display the image
        logger.info("Displaying welcome screen...")
        self.epd.display(self.epd.getbuffer(image))
        logger.info("Welcome screen displayed")
    
    def sleep(self):
        """Put the display to sleep to save power"""
        if self.epd:
            logger.info("Putting display to sleep...")
            self.epd.sleep()
            logger.info("Display in sleep mode")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.epd:
            try:
                self.epd.sleep()
            except:
                pass
