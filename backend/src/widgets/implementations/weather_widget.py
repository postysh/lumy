"""Weather widget - displays current weather information"""

import asyncio
import aiohttp
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

from src.widgets.base_widget import BaseWidget

logger = logging.getLogger(__name__)


class WeatherWidget(BaseWidget):
    """Displays weather information"""
    
    def __init__(self, config):
        super().__init__(config, 'weather')
        self.api_key = config.get('widgets.weather.api_key', '')
        self.location = config.get('widgets.weather.location', 'New York')
        self.units = config.get('widgets.weather.units', 'metric')
    
    async def initialize(self):
        """Initialize weather widget"""
        logger.info("Initializing weather widget")
        self.data = {
            'temperature': '--',
            'condition': 'Unknown',
            'humidity': '--',
            'location': self.location
        }
        
        if self.api_key:
            await self.update()
    
    async def update(self):
        """Update weather data"""
        if not self.api_key:
            logger.warning("Weather API key not configured")
            self.data = {
                'temperature': '72°F',
                'condition': 'Sunny',
                'humidity': '45%',
                'location': self.location,
                'icon': '☀️'
            }
            return
        
        try:
            # Example using OpenWeatherMap API
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': self.units
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        temp = data['main']['temp']
                        condition = data['weather'][0]['main']
                        humidity = data['main']['humidity']
                        
                        self.data = {
                            'temperature': f"{temp}°{'C' if self.units == 'metric' else 'F'}",
                            'condition': condition,
                            'humidity': f"{humidity}%",
                            'location': self.location,
                            'icon': self._get_weather_icon(condition)
                        }
                        
                        self.last_update = datetime.now().timestamp()
                        logger.info(f"Weather updated: {self.data}")
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}", exc_info=True)
            # Use mock data on error
            self.data = {
                'temperature': '72°F',
                'condition': 'Partly Cloudy',
                'humidity': '45%',
                'location': self.location,
                'icon': '⛅'
            }
    
    def _get_weather_icon(self, condition: str) -> str:
        """Get emoji icon for weather condition"""
        icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️'
        }
        return icons.get(condition, '🌤️')
    
    async def render(self, width: int, height: int) -> Image.Image:
        """Render weather widget"""
        canvas = self.create_canvas(width, height)
        draw = ImageDraw.Draw(canvas)
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline=(200, 200, 200), width=2)
        
        # Title
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        y_pos = 20
        
        # Location
        location_text = self.data.get('location', 'Unknown')
        draw.text((20, y_pos), location_text, font=title_font, fill=(0, 0, 0))
        y_pos += 60
        
        # Temperature (large)
        temp_text = self.data.get('temperature', '--')
        draw.text((20, y_pos), temp_text, font=title_font, fill=(0, 0, 0))
        y_pos += 60
        
        # Condition
        condition_text = self.data.get('condition', 'Unknown')
        icon = self.data.get('icon', '')
        weather_line = f"{icon} {condition_text}"
        draw.text((20, y_pos), weather_line, font=text_font, fill=(0, 0, 0))
        y_pos += 50
        
        # Humidity
        humidity_text = f"Humidity: {self.data.get('humidity', '--')}"
        draw.text((20, y_pos), humidity_text, font=text_font, fill=(0, 0, 0))
        
        return canvas
