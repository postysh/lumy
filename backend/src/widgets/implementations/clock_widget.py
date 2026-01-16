"""Clock widget - displays current time and date"""

import asyncio
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

from src.widgets.base_widget import BaseWidget

logger = logging.getLogger(__name__)


class ClockWidget(BaseWidget):
    """Displays current time and date"""
    
    def __init__(self, config):
        super().__init__(config, 'clock')
        self.format_12h = True
        self.show_seconds = False
        self.show_date = True
    
    async def initialize(self):
        """Initialize clock widget"""
        logger.info("Initializing clock widget")
        self.data = {
            'time': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%A, %B %d, %Y')
        }
    
    async def update(self):
        """Update clock data"""
        now = datetime.now()
        
        if self.format_12h:
            time_format = '%I:%M:%S %p' if self.show_seconds else '%I:%M %p'
        else:
            time_format = '%H:%M:%S' if self.show_seconds else '%H:%M'
        
        self.data = {
            'time': now.strftime(time_format),
            'date': now.strftime('%A, %B %d, %Y'),
            'day': now.strftime('%A'),
            'timestamp': now.timestamp()
        }
        
        self.last_update = now.timestamp()
    
    async def render(self, width: int, height: int) -> Image.Image:
        """Render clock widget"""
        canvas = self.create_canvas(width, height)
        draw = ImageDraw.Draw(canvas)
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline=(200, 200, 200), width=2)
        
        # Draw time (large font)
        time_text = self.data.get('time', '--:--')
        try:
            time_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
        except:
            time_font = ImageFont.load_default()
        
        # Center the time
        time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
        time_width = time_bbox[2] - time_bbox[0]
        time_x = (width - time_width) // 2
        time_y = height // 3
        
        draw.text((time_x, time_y), time_text, font=time_font, fill=(0, 0, 0))
        
        # Draw date (smaller font)
        if self.show_date:
            date_text = self.data.get('date', '')
            try:
                date_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
            except:
                date_font = ImageFont.load_default()
            
            date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_width = date_bbox[2] - date_bbox[0]
            date_x = (width - date_width) // 2
            date_y = time_y + 100
            
            draw.text((date_x, date_y), date_text, font=date_font, fill=(0, 0, 0))
        
        return canvas
