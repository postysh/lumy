"""Calendar widget - displays upcoming events"""

import asyncio
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import logging

from src.widgets.base_widget import BaseWidget

logger = logging.getLogger(__name__)


class CalendarWidget(BaseWidget):
    """Displays calendar events"""
    
    def __init__(self, config):
        super().__init__(config, 'calendar')
        self.max_events = config.get('widgets.calendar.max_events', 5)
        self.days_ahead = config.get('widgets.calendar.days_ahead', 7)
    
    async def initialize(self):
        """Initialize calendar widget"""
        logger.info("Initializing calendar widget")
        self.data = {
            'events': []
        }
        await self.update()
    
    async def update(self):
        """Update calendar data"""
        # In production, this would sync with Google Calendar, iCal, etc.
        # For now, use mock data
        now = datetime.now()
        
        mock_events = [
            {
                'title': 'Team Meeting',
                'time': (now + timedelta(hours=2)).strftime('%I:%M %p'),
                'date': now.strftime('%b %d'),
            },
            {
                'title': 'Lunch with Sarah',
                'time': '12:00 PM',
                'date': now.strftime('%b %d'),
            },
            {
                'title': 'Project Deadline',
                'time': '5:00 PM',
                'date': (now + timedelta(days=1)).strftime('%b %d'),
            },
            {
                'title': 'Dentist Appointment',
                'time': '10:00 AM',
                'date': (now + timedelta(days=3)).strftime('%b %d'),
            }
        ]
        
        self.data = {
            'events': mock_events[:self.max_events],
            'count': len(mock_events)
        }
        
        self.last_update = datetime.now().timestamp()
    
    async def render(self, width: int, height: int) -> Image.Image:
        """Render calendar widget"""
        canvas = self.create_canvas(width, height)
        draw = ImageDraw.Draw(canvas)
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline=(200, 200, 200), width=2)
        
        # Fonts
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
            event_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
            time_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        except:
            title_font = ImageFont.load_default()
            event_font = ImageFont.load_default()
            time_font = ImageFont.load_default()
        
        y_pos = 20
        
        # Title
        draw.text((20, y_pos), "📅 Upcoming Events", font=title_font, fill=(0, 0, 0))
        y_pos += 60
        
        # Events
        events = self.data.get('events', [])
        
        if not events:
            draw.text((20, y_pos), "No upcoming events", font=event_font, fill=(128, 128, 128))
        else:
            for event in events:
                # Event title
                title = event.get('title', 'Untitled')
                draw.text((20, y_pos), title, font=event_font, fill=(0, 0, 0))
                y_pos += 40
                
                # Event time and date
                time_text = f"{event.get('date', '')} at {event.get('time', '')}"
                draw.text((20, y_pos), time_text, font=time_font, fill=(100, 100, 100))
                y_pos += 50
                
                # Stop if we run out of space
                if y_pos > height - 60:
                    break
        
        return canvas
