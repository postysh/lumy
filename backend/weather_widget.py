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
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max',
                'temperature_unit': 'fahrenheit',
                'wind_speed_unit': 'mph',
                'timezone': 'America/Chicago',
                'forecast_days': 6  # Get 6 days (today + 5 more)
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
                    'precipitation': current.get('precipitation', 0),
                    'time': current.get('time', ''),
                    'uv_index': 0,
                    'precipitation_chance': 0,
                    'forecast': []
                }
                
                # Get today's UV and precipitation
                if daily:
                    uv_indices = daily.get('uv_index_max', [])
                    precip_probs = daily.get('precipitation_probability_max', [])
                    
                    if len(uv_indices) > 0:
                        weather_info['uv_index'] = round(uv_indices[0])
                    if len(precip_probs) > 0:
                        weather_info['precipitation_chance'] = precip_probs[0]
                
                # Parse 5-day forecast (skip today, get next 5 days)
                if daily:
                    times = daily.get('time', [])
                    codes = daily.get('weather_code', [])
                    max_temps = daily.get('temperature_2m_max', [])
                    min_temps = daily.get('temperature_2m_min', [])
                    
                    for i in range(1, min(6, len(times))):  # Start from index 1 (tomorrow)
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
    
    def get_later_forecast(self, weather_code):
        """Get a simple forecast description for later in the day"""
        desc = self.get_weather_description(weather_code)
        phrases = [
            "Expect similar conditions",
            "Conditions will persist",
            "Staying consistent",
            "No major changes expected"
        ]
        
        if 'rain' in desc.lower() or 'drizzle' in desc.lower():
            return "Rain likely later"
        elif 'snow' in desc.lower():
            return "Snow expected"
        elif 'thunder' in desc.lower():
            return "Storms possible"
        elif 'clear' in desc.lower():
            return "Clear skies ahead"
        elif 'cloud' in desc.lower():
            return "Clouds continuing"
        else:
            return phrases[0]
    
    def draw_dotted_line(self, draw, x, y1, y2, color=(180, 180, 180), spacing=5):
        """Draw a vertical dotted line"""
        y = y1
        while y < y2:
            draw.line([(x, y), (x, min(y + spacing, y2))], fill=color, width=2)
            y += spacing * 2
    
    def render(self, weather_data=None):
        """
        Render weather widget with 3-column layout
        
        Args:
            weather_data: Optional pre-fetched weather data
            
        Returns:
            PIL Image object
        """
        if weather_data is None:
            weather_data = self.fetch_weather()
        
        if not weather_data:
            return self._render_error()
        
        # Create canvas
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            condition_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 42)
            later_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
            temp_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
            label_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
            value_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
            day_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
            forecast_temp_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
            footer_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}")
            # Fallback
            condition_font = ImageFont.load_default()
            later_font = ImageFont.load_default()
            temp_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
            day_font = ImageFont.load_default()
            forecast_temp_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()
        
        # Define column widths (3 columns)
        col1_width = 267  # Left section
        col2_width = 266  # Center section
        col3_width = 267  # Right section
        col1_x = 0
        col2_x = col1_width
        col3_x = col1_width + col2_width
        
        footer_y = self.height - 35
        content_height = footer_y - 20
        
        # Draw dotted vertical dividers
        self.draw_dotted_line(draw, col2_x, 0, footer_y)
        self.draw_dotted_line(draw, col3_x, 0, footer_y)
        
        # ============ LEFT SECTION ============
        left_margin = 20
        
        # Current condition at top
        desc_text = self.get_weather_description(weather_data['weather_code'])
        desc_icon = self.get_weather_icon(weather_data['weather_code'])
        
        # Wrap text if too long
        condition_y = 30
        draw.text((left_margin, condition_y), desc_icon, font=condition_font, fill='black')
        draw.text((left_margin, condition_y + 50), desc_text, font=condition_font, fill=(40, 40, 40))
        
        # "Later" forecast at bottom of left section
        later_y = content_height - 100
        draw.text((left_margin, later_y), "Later:", font=label_font, fill=(100, 100, 100))
        later_forecast = self.get_later_forecast(weather_data['weather_code'])
        draw.text((left_margin, later_y + 35), later_forecast, font=later_font, fill=(60, 60, 60))
        
        # ============ CENTER SECTION ============
        center_x = col2_x + (col2_width // 2)
        
        # Large temperature at top (centered)
        temp = weather_data['temperature']
        temp_color = self.get_temp_color(temp)
        temp_text = f"{temp}°"
        temp_bbox = draw.textbbox((0, 0), temp_text, font=temp_font)
        temp_width = temp_bbox[2] - temp_bbox[0]
        temp_x = center_x - (temp_width // 2)
        draw.text((temp_x, 20), temp_text, font=temp_font, fill=temp_color)
        
        # UV and Precipitation at bottom of center
        uv_precip_y = content_height - 120
        
        # UV Index
        uv_text = "UV Index"
        uv_value = f"{weather_data['uv_index']}"
        uv_bbox = draw.textbbox((0, 0), uv_text, font=label_font)
        uv_text_width = uv_bbox[2] - uv_bbox[0]
        uv_x = center_x - (uv_text_width // 2)
        draw.text((uv_x, uv_precip_y), uv_text, font=label_font, fill=(100, 100, 100))
        
        uv_value_bbox = draw.textbbox((0, 0), uv_value, font=value_font)
        uv_value_width = uv_value_bbox[2] - uv_value_bbox[0]
        uv_value_x = center_x - (uv_value_width // 2)
        draw.text((uv_value_x, uv_precip_y + 30), uv_value, font=value_font, fill=(255, 140, 0))
        
        # Precipitation
        precip_text = "Precipitation"
        precip_value = f"{weather_data['precipitation_chance']}%"
        precip_bbox = draw.textbbox((0, 0), precip_text, font=label_font)
        precip_text_width = precip_bbox[2] - precip_bbox[0]
        precip_x = center_x - (precip_text_width // 2)
        draw.text((precip_x, uv_precip_y + 75), precip_text, font=label_font, fill=(100, 100, 100))
        
        precip_value_bbox = draw.textbbox((0, 0), precip_value, font=value_font)
        precip_value_width = precip_value_bbox[2] - precip_value_bbox[0]
        precip_value_x = center_x - (precip_value_width // 2)
        draw.text((precip_value_x, uv_precip_y + 105), precip_value, font=value_font, fill=(70, 130, 180))
        
        # ============ RIGHT SECTION (5-DAY FORECAST STACKED) ============
        right_margin = col3_x + 15
        forecast_start_y = 20
        forecast_item_height = 73
        
        for i, day_data in enumerate(weather_data.get('forecast', [])[:5]):
            item_y = forecast_start_y + (i * forecast_item_height)
            
            # Day name
            day_name = self.get_day_name(day_data['date'])
            draw.text((right_margin, item_y), day_name, font=day_font, fill=(40, 40, 40))
            
            # Weather icon
            icon = self.get_weather_icon(day_data['weather_code'])
            draw.text((right_margin + 45, item_y - 5), icon, font=condition_font, fill='black')
            
            # High/Low temps
            high_temp = f"{day_data['temp_max']}°"
            low_temp = f"{day_data['temp_min']}°"
            draw.text((right_margin + 100, item_y + 3), high_temp, font=forecast_temp_font, fill=(255, 69, 0))
            draw.text((right_margin + 155, item_y + 3), low_temp, font=forecast_temp_font, fill=(70, 130, 180))
            
            # Separator line (except last item)
            if i < 4:
                sep_y = item_y + forecast_item_height - 5
                draw.line([(right_margin, sep_y), (col3_x + col3_width - 15, sep_y)], fill=(220, 220, 220), width=1)
        
        # ============ FOOTER ============
        # Bottom left: "Weather"
        draw.text((20, footer_y), "Weather", font=footer_font, fill=(100, 100, 100))
        
        # Bottom right: City name
        city_text = "St. Paul, MN"
        city_bbox = draw.textbbox((0, 0), city_text, font=footer_font)
        city_width = city_bbox[2] - city_bbox[0]
        draw.text((self.width - city_width - 20, footer_y), city_text, font=footer_font, fill=(100, 100, 100))
        
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
