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
        """Fetch current weather and 5-day forecast from Open-Meteo API"""
        try:
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
                'temperature_unit': 'fahrenheit',
                'wind_speed_unit': 'mph',
                'timezone': 'America/Chicago',
                'forecast_days': 5
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                daily = data.get('daily', {})
                
                weather_info = {
                    'temperature': round(current.get('temperature_2m', 0)),
                    'humidity': current.get('relative_humidity_2m', 0),
                    'wind_speed': round(current.get('wind_speed_10m', 0)),
                    'weather_code': current.get('weather_code', 0),
                    'time': current.get('time', ''),
                    'forecast': []
                }
                
                # Parse 5-day forecast
                if daily:
                    times = daily.get('time', [])
                    codes = daily.get('weather_code', [])
                    max_temps = daily.get('temperature_2m_max', [])
                    min_temps = daily.get('temperature_2m_min', [])
                    
                    for i in range(min(5, len(times))):
                        weather_info['forecast'].append({
                            'date': times[i],
                            'weather_code': codes[i] if i < len(codes) else 0,
                            'temp_max': round(max_temps[i]) if i < len(max_temps) else 0,
                            'temp_min': round(min_temps[i]) if i < len(min_temps) else 0,
                        })
                
                logger.info(f"Weather data fetched: {weather_info['temperature']}°F with {len(weather_info['forecast'])} day forecast")
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
    
    def get_day_name(self, date_str):
        """Convert date string to day name"""
        try:
            date_obj = datetime.fromisoformat(date_str)
            return date_obj.strftime('%a')  # Mon, Tue, etc.
        except:
            return ""
    
    def render(self, weather_data=None):
        """
        Render weather widget to image with new layout
        
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
            city_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
            current_temp_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
            header_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
            label_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
            value_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
            day_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            forecast_temp_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}")
            city_font = ImageFont.load_default()
            current_temp_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
            day_font = ImageFont.load_default()
            forecast_temp_font = ImageFont.load_default()
        
        # TOP LEFT: City name and current temperature
        left_margin = 30
        top_margin = 30
        
        city_text = "St. Paul"
        draw.text((left_margin, top_margin), city_text, font=city_font, fill=(40, 40, 40))
        
        temp = weather_data['temperature']
        temp_color = self.get_temp_color(temp)
        temp_text = f"{temp}°F"
        draw.text((left_margin, top_margin + 60), temp_text, font=current_temp_font, fill=temp_color)
        
        # Weather description with icon
        desc_icon = self.get_weather_icon(weather_data['weather_code'])
        desc_text = self.get_weather_description(weather_data['weather_code'])
        full_desc = f"{desc_icon} {desc_text}"
        draw.text((left_margin, top_margin + 145), full_desc, font=label_font, fill=(60, 60, 60))
        
        # TOP RIGHT: "Current Weather" header and info cards
        right_section_x = 420
        
        header_text = "Current Weather"
        draw.text((right_section_x, top_margin), header_text, font=header_font, fill=(40, 40, 40))
        
        # Humidity card
        card_y = top_margin + 60
        card_width = 160
        card_height = 50
        
        draw.rectangle(
            [right_section_x, card_y, right_section_x + card_width, card_y + card_height],
            fill=(173, 216, 230),
            outline=(70, 130, 180),
            width=2
        )
        humidity_text = f"💧 {weather_data['humidity']}%"
        draw.text((right_section_x + 10, card_y + 12), humidity_text, font=value_font, fill=(25, 25, 112))
        
        # Wind card
        wind_card_x = right_section_x + card_width + 20
        draw.rectangle(
            [wind_card_x, card_y, wind_card_x + card_width, card_y + card_height],
            fill=(144, 238, 144),
            outline=(34, 139, 34),
            width=2
        )
        wind_text = f"💨 {weather_data['wind_speed']} mph"
        draw.text((wind_card_x + 10, card_y + 12), wind_text, font=value_font, fill=(0, 100, 0))
        
        # BOTTOM: 5-day forecast
        forecast_y = 240
        
        # Draw separator line
        draw.line([(20, forecast_y - 20), (self.width - 20, forecast_y - 20)], fill=(180, 180, 180), width=2)
        
        # Forecast title
        forecast_title = "5-Day Forecast"
        draw.text((30, forecast_y), forecast_title, font=header_font, fill=(40, 40, 40))
        
        # Draw forecast cards
        forecast_start_y = forecast_y + 55
        card_height = 160
        card_spacing = 10
        total_spacing = card_spacing * 4
        card_width = (self.width - 60 - total_spacing) // 5
        
        for i, day_data in enumerate(weather_data.get('forecast', [])[:5]):
            card_x = 30 + i * (card_width + card_spacing)
            
            # Card background
            draw.rectangle(
                [card_x, forecast_start_y, card_x + card_width, forecast_start_y + card_height],
                fill='white',
                outline=(180, 180, 180),
                width=2
            )
            
            # Day name
            day_name = self.get_day_name(day_data['date'])
            day_bbox = draw.textbbox((0, 0), day_name, font=day_font)
            day_width = day_bbox[2] - day_bbox[0]
            day_x = card_x + (card_width - day_width) // 2
            draw.text((day_x, forecast_start_y + 10), day_name, font=day_font, fill=(40, 40, 40))
            
            # Weather icon
            icon = self.get_weather_icon(day_data['weather_code'])
            icon_bbox = draw.textbbox((0, 0), icon, font=header_font)
            icon_width = icon_bbox[2] - icon_bbox[0]
            icon_x = card_x + (card_width - icon_width) // 2
            draw.text((icon_x, forecast_start_y + 45), icon, font=header_font, fill='black')
            
            # High temp
            high_temp = f"{day_data['temp_max']}°"
            high_bbox = draw.textbbox((0, 0), high_temp, font=forecast_temp_font)
            high_width = high_bbox[2] - high_bbox[0]
            high_x = card_x + (card_width - high_width) // 2
            draw.text((high_x, forecast_start_y + 100), high_temp, font=forecast_temp_font, fill=(255, 69, 0))
            
            # Low temp
            low_temp = f"{day_data['temp_min']}°"
            low_bbox = draw.textbbox((0, 0), low_temp, font=forecast_temp_font)
            low_width = low_bbox[2] - low_bbox[0]
            low_x = card_x + (card_width - low_width) // 2
            draw.text((low_x, forecast_start_y + 125), low_temp, font=forecast_temp_font, fill=(70, 130, 180))
        
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
