"""
Weather Widget for Lumy Display
Displays current weather for St. Paul, Minnesota
"""
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherWidget:
    def __init__(self, width=800, height=480):
        self.width = width
        self.height = height
        # Using Open-Meteo (free, no API key required)
        # St. Paul, MN coordinates: 44.9537°N, 93.0900°W
        self.lat = 44.9537
        self.lon = -93.0900
        self.api_url = "https://api.open-meteo.com/v1/forecast"
    
    def fetch_weather(self):
        """Fetch current weather data from Open-Meteo API"""
        try:
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                'temperature_unit': 'fahrenheit',
                'wind_speed_unit': 'mph',
                'timezone': 'America/Chicago'
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                
                weather_info = {
                    'temperature': round(current.get('temperature_2m', 0)),
                    'humidity': current.get('relative_humidity_2m', 0),
                    'wind_speed': round(current.get('wind_speed_10m', 0)),
                    'weather_code': current.get('weather_code', 0),
                    'time': current.get('time', ''),
                }
                
                logger.info(f"Weather data fetched: {weather_info['temperature']}°F")
                return weather_info
            else:
                logger.error(f"Weather API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return None
    
    def get_weather_description(self, code):
        """Convert WMO weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with hail"
        }
        return weather_codes.get(code, "Unknown")
    
    def get_temp_color(self, temp):
        """Get color based on temperature"""
        if temp <= 32:
            return (0, 0, 255)  # Blue - freezing
        elif temp <= 50:
            return (0, 128, 255)  # Light blue - cold
        elif temp <= 70:
            return (0, 200, 0)  # Green - comfortable
        elif temp <= 85:
            return (255, 165, 0)  # Orange - warm
        else:
            return (255, 0, 0)  # Red - hot
    
    def render(self, weather_data=None):
        """
        Render weather widget to image with colors
        
        Args:
            weather_data: Optional pre-fetched weather data
            
        Returns:
            PIL Image object
        """
        if weather_data is None:
            weather_data = self.fetch_weather()
        
        if not weather_data:
            # Return error screen
            return self._render_error()
        
        # Create canvas with light blue background
        image = Image.new('RGB', (self.width, self.height), (240, 248, 255))  # Alice blue
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 56)
            location_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
            temp_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 140)
            desc_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 38)
            value_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
            time_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}")
            # Fallback to default
            title_font = ImageFont.load_default()
            location_font = ImageFont.load_default()
            temp_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
            time_font = ImageFont.load_default()
        
        # Draw decorative header bar
        draw.rectangle([0, 0, self.width, 80], fill=(70, 130, 180))  # Steel blue
        
        # Draw header text
        header_text = "☀ Current Weather"
        header_bbox = draw.textbbox((0, 0), header_text, font=title_font)
        header_width = header_bbox[2] - header_bbox[0]
        header_x = (self.width - header_width) // 2
        draw.text((header_x, 15), header_text, font=title_font, fill='white')
        
        # Draw location with pin emoji
        location_text = "📍 St. Paul, Minnesota"
        location_bbox = draw.textbbox((0, 0), location_text, font=location_font)
        location_width = location_bbox[2] - location_bbox[0]
        location_x = (self.width - location_width) // 2
        draw.text((location_x, 95), location_text, font=location_font, fill=(50, 50, 50))
        
        # Draw temperature with color-coded value
        temp = weather_data['temperature']
        temp_color = self.get_temp_color(temp)
        temp_text = f"{temp}°"
        temp_bbox = draw.textbbox((0, 0), temp_text, font=temp_font)
        temp_width = temp_bbox[2] - temp_bbox[0]
        temp_x = (self.width - temp_width) // 2
        
        # Draw temperature with subtle shadow
        draw.text((temp_x + 3, 148), temp_text, font=temp_font, fill=(200, 200, 200))
        draw.text((temp_x, 145), temp_text, font=temp_font, fill=temp_color)
        
        # Draw weather description with icon
        desc_text = self.get_weather_description(weather_data['weather_code'])
        desc_icon = self.get_weather_icon(weather_data['weather_code'])
        full_desc = f"{desc_icon} {desc_text}"
        desc_bbox = draw.textbbox((0, 0), full_desc, font=desc_font)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (self.width - desc_width) // 2
        draw.text((desc_x, 310), full_desc, font=desc_font, fill=(60, 60, 60))
        
        # Draw info cards
        card_y = 370
        card_height = 70
        card_spacing = 20
        
        # Left card - Humidity (blue theme)
        left_card_x = 50
        card_width = (self.width - 3 * card_spacing - 100) // 2
        
        draw.rectangle(
            [left_card_x, card_y, left_card_x + card_width, card_y + card_height],
            fill=(173, 216, 230),  # Light blue
            outline=(70, 130, 180),
            width=3
        )
        
        humidity_text = f"💧 {weather_data['humidity']}%"
        humidity_bbox = draw.textbbox((0, 0), humidity_text, font=value_font)
        humidity_width = humidity_bbox[2] - humidity_bbox[0]
        humidity_x = left_card_x + (card_width - humidity_width) // 2
        draw.text((humidity_x, card_y + 20), humidity_text, font=value_font, fill=(25, 25, 112))
        
        # Right card - Wind (green theme)
        right_card_x = left_card_x + card_width + card_spacing
        
        draw.rectangle(
            [right_card_x, card_y, right_card_x + card_width, card_y + card_height],
            fill=(144, 238, 144),  # Light green
            outline=(34, 139, 34),
            width=3
        )
        
        wind_text = f"💨 {weather_data['wind_speed']} mph"
        wind_bbox = draw.textbbox((0, 0), wind_text, font=value_font)
        wind_width = wind_bbox[2] - wind_bbox[0]
        wind_x = right_card_x + (card_width - wind_width) // 2
        draw.text((wind_x, card_y + 20), wind_text, font=value_font, fill=(0, 100, 0))
        
        # Draw timestamp footer
        try:
            update_time = datetime.now().strftime('%I:%M %p')
            time_text = f"Last updated: {update_time}"
            time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
            time_width = time_bbox[2] - time_bbox[0]
            time_x = (self.width - time_width) // 2
            draw.text((time_x, 455), time_text, font=time_font, fill=(100, 100, 100))
        except:
            pass
        
        return image
    
    def get_weather_icon(self, code):
        """Get emoji icon for weather condition"""
        if code == 0:
            return "☀️"  # Clear
        elif code in [1, 2]:
            return "⛅"  # Partly cloudy
        elif code == 3:
            return "☁️"  # Cloudy
        elif code in [45, 48]:
            return "🌫️"  # Fog
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            return "🌧️"  # Rain
        elif code in [71, 73, 75, 77, 85, 86]:
            return "❄️"  # Snow
        elif code in [95, 96, 99]:
            return "⛈️"  # Thunderstorm
        else:
            return "🌡️"  # Default
    
    def _render_error(self):
        """Render error screen when weather data unavailable"""
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
        except:
            font = ImageFont.load_default()
        
        error_text = "Weather data unavailable"
        bbox = draw.textbbox((0, 0), error_text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, self.height // 2 - 30), error_text, font=font, fill='black')
        
        return image
