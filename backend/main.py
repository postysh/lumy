#!/usr/bin/env python3
"""
Lumy - Main Application
Connects to dashboard, displays registration code, and manages widgets
"""
import os
import sys
import time
import logging
import random
import base64
from io import BytesIO
from display_manager import DisplayManager
from device_manager import DeviceManager
from api_client import LumyAPIClient
from weather_widget import WeatherWidget
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def image_to_base64_preview(image, max_width=400):
    """
    Convert PIL image to base64 encoded thumbnail for preview
    
    Args:
        image: PIL Image object
        max_width: Maximum width of thumbnail (maintains aspect ratio)
        
    Returns:
        Base64 encoded image string or None if error
    """
    try:
        from PIL import Image
        
        # Calculate thumbnail size (maintain aspect ratio)
        aspect_ratio = image.height / image.width
        thumbnail_width = min(max_width, image.width)
        thumbnail_height = int(thumbnail_width * aspect_ratio)
        
        # Create thumbnail
        thumbnail = image.copy()
        thumbnail.thumbnail((thumbnail_width, thumbnail_height), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = BytesIO()
        thumbnail.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"Failed to create image preview: {e}")
        return None

def generate_registration_code():
    """
    Generate a random 7-character registration code
    Format: ABC-123 (3 letters, dash, 3 numbers)
    """
    # Remove ambiguous characters: 0, O, I, 1, L
    letters = 'ABCDEFGHJKMNPQRSTUVWXYZ'
    numbers = '23456789'
    
    # Generate 3 letters
    letter_part = ''.join(random.choices(letters, k=3))
    # Generate 3 numbers
    number_part = ''.join(random.choices(numbers, k=3))
    
    return f"{letter_part}-{number_part}"

def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("Lumy Display Starting...")
    logger.info("=" * 60)
    
    # Check if we're running on a Raspberry Pi
    if not os.path.exists('/sys/class/gpio'):
        logger.error("This script must be run on a Raspberry Pi with GPIO access")
        sys.exit(1)
    
    try:
        # Initialize components
        display = DisplayManager()
        device_mgr = DeviceManager(config.DEVICE_ID_FILE)
        api_client = LumyAPIClient(config.API_BASE_URL, config.API_KEY)
        
        # Get device ID
        device_id = device_mgr.get_device_id()
        logger.info(f"Device ID: {device_id}")
        
        # Check if device is already registered
        logger.info("Checking if device is already registered...")
        status = api_client.check_claim_status(device_id)
        
        if status and status.get('registered'):
            # Device is already claimed, skip registration
            logger.info("Device is already registered!")
            logger.info(f"  User ID: {status.get('user_id')}")
            logger.info(f"  Device name: {status.get('device_name')}")
            logger.info("Skipping registration flow, going straight to widgets...")
        else:
            # Device not claimed yet, do registration flow
            logger.info("Device not registered, starting registration flow...")
            
            # Generate registration code
            reg_code = generate_registration_code()
            logger.info(f"Registration code: {reg_code}")
            
            # Register with API
            logger.info("Registering with dashboard...")
            registration = api_client.register_device(device_id, reg_code)
            
            if not registration:
                logger.error("Failed to register with dashboard. Check API URL and API key.")
                logger.error(f"API URL: {config.API_BASE_URL}")
                logger.warning("Displaying code anyway, but claiming won't work without API connection.")
            else:
                logger.info("Successfully registered with dashboard")
            
            # Show welcome screen
            display.show_welcome_screen(reg_code)
            logger.info("Welcome screen displayed")
            
            # Poll for claim status
            logger.info("Waiting for user to claim device...")
            claimed = False
            poll_count = 0
            
            while not claimed:
                time.sleep(config.POLL_INTERVAL)
                poll_count += 1
                
                # Check if claimed
                status = api_client.check_claim_status(device_id)
                
                if status and status.get('registered'):
                    logger.info("Device has been claimed!")
                    logger.info(f"  User ID: {status.get('user_id')}")
                    logger.info(f"  Device name: {status.get('device_name')}")
                    claimed = True
                    break
                
                # Log status every minute
                if poll_count % 6 == 0:  # Every 60 seconds
                    logger.info(f"Still waiting for claim... ({poll_count * config.POLL_INTERVAL}s)")
        
        # Device is claimed, fetch configuration
        logger.info("Fetching configuration...")
        device_config = api_client.get_config(device_id)
        
        if device_config:
            logger.info("Configuration received:")
            logger.info(f"  Widgets: {len(device_config.get('widgets', []))}")
        else:
            logger.warning("Could not fetch configuration")
        
        # Initialize weather widget
        logger.info("Initializing weather widget...")
        weather = WeatherWidget(config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
        
        # Display weather widget
        logger.info("Rendering weather widget...")
        weather_image = weather.render()
        current_display_image = None
        
        if weather_image:
            display.epd.display(display.epd.getbuffer(weather_image))
            current_display_image = weather_image
            logger.info("Weather widget displayed")
        else:
            logger.error("Failed to render weather widget")
        
        # Main loop: Send heartbeats and refresh weather/config
        logger.info("Entering main loop...")
        last_heartbeat = time.time()
        last_weather_refresh = time.time()
        last_config_refresh = time.time()
        
        while True:
            now = time.time()
            
            # Send heartbeat every 60 seconds with display preview
            if now - last_heartbeat >= 60:
                display_preview = None
                if current_display_image:
                    display_preview = image_to_base64_preview(current_display_image)
                api_client.send_heartbeat(device_id, display_preview)
                last_heartbeat = now
            
            # Refresh weather every 10 minutes
            if now - last_weather_refresh >= 600:
                logger.info("Refreshing weather...")
                weather_image = weather.render()
                if weather_image:
                    display.epd.display(display.epd.getbuffer(weather_image))
                    current_display_image = weather_image
                    logger.info("Weather updated")
                last_weather_refresh = now
            
            # Refresh config every 5 minutes
            if now - last_config_refresh >= config.CONFIG_REFRESH_INTERVAL:
                logger.info("Refreshing configuration...")
                device_config = api_client.get_config(device_id)
                if device_config:
                    logger.info("Configuration updated")
                last_config_refresh = now
            
            time.sleep(30)
    
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        if 'display' in locals():
            display.sleep()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
