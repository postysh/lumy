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
from display_manager import DisplayManager
from device_manager import DeviceManager
from api_client import LumyAPIClient
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_registration_code():
    """
    Generate a random 6-character registration code
    Format: XXXXXX (uppercase letters and numbers, no ambiguous chars)
    """
    # Remove ambiguous characters: 0, O, I, 1, L
    chars = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'
    return ''.join(random.choices(chars, k=6))

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
            logger.info("  TODO: Implement widget rendering")
            # TODO: Render widgets based on config
        else:
            logger.warning("Could not fetch configuration")
        
        # Main loop: Send heartbeats and refresh config
        logger.info("Entering main loop...")
        last_heartbeat = time.time()
        last_config_refresh = time.time()
        
        while True:
            now = time.time()
            
            # Send heartbeat every 60 seconds
            if now - last_heartbeat >= 60:
                api_client.send_heartbeat(device_id)
                last_heartbeat = now
            
            # Refresh config every 5 minutes
            if now - last_config_refresh >= config.CONFIG_REFRESH_INTERVAL:
                logger.info("Refreshing configuration...")
                device_config = api_client.get_config(device_id)
                if device_config:
                    logger.info("Configuration updated")
                    # TODO: Update widgets based on new config
                last_config_refresh = now
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        if 'display' in locals():
            display.sleep()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
