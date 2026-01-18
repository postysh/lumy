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
    
    def render(self, weather_data=None):
        """
        Render weather widget to image
        
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
        
        # Create canvas
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
            location_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
            temp_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 120)
            label_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
            value_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
            desc_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
            time_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}")
            # Fallback to default
            title_font = ImageFont.load_default()
            location_font = ImageFont.load_default()
            temp_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            time_font = ImageFont.load_default()
        
        # Draw header
        header_text = "Current Weather"
        header_bbox = draw.textbbox((0, 0), header_text, font=title_font)
        header_width = header_bbox[2] - header_bbox[0]
        header_x = (self.width - header_width) // 2
        draw.text((header_x, 30), header_text, font=title_font, fill='black')
        
        # Draw location
        location_text = "St. Paul, Minnesota"
        location_bbox = draw.textbbox((0, 0), location_text, font=location_font)
        location_width = location_bbox[2] - location_bbox[0]
        location_x = (self.width - location_width) // 2
        draw.text((location_x, 100), location_text, font=location_font, fill='black')
        
        # Draw temperature (large, centered)
        temp_text = f"{weather_data['temperature']}°F"
        temp_bbox = draw.textbbox((0, 0), temp_text, font=temp_font)
        temp_width = temp_bbox[2] - temp_bbox[0]
        temp_x = (self.width - temp_width) // 2
        draw.text((temp_x, 160), temp_text, font=temp_font, fill='black')
        
        # Draw weather description
        desc_text = self.get_weather_description(weather_data['weather_code'])
        desc_bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (self.width - desc_width) // 2
        draw.text((desc_x, 300), desc_text, font=desc_font, fill='black')
        
        # Draw additional info (humidity and wind)
        info_y = 370
        
        # Humidity
        humidity_text = f"Humidity: {weather_data['humidity']}%"
        humidity_bbox = draw.textbbox((0, 0), humidity_text, font=value_font)
        humidity_width = humidity_bbox[2] - humidity_bbox[0]
        humidity_x = (self.width // 2) - humidity_width - 40
        draw.text((humidity_x, info_y), humidity_text, font=value_font, fill='black')
        
        # Wind
        wind_text = f"Wind: {weather_data['wind_speed']} mph"
        wind_x = (self.width // 2) + 40
        draw.text((wind_x, info_y), wind_text, font=value_font, fill='black')
        
        # Draw timestamp
        try:
            update_time = datetime.now().strftime('%I:%M %p')
            time_text = f"Updated: {update_time}"
            time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
            time_width = time_bbox[2] - time_bbox[0]
            time_x = (self.width - time_width) // 2
            draw.text((time_x, 440), time_text, font=time_font, fill='gray')
        except:
            pass
        
        return image
    
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
