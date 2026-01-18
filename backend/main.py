#!/usr/bin/env python3
"""
Lumy - Main Application
Displays welcome screen with registration code on e-paper display
"""
import os
import sys
import time
import logging
import random
import string
from display_manager import DisplayManager

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
        # Initialize display
        display = DisplayManager()
        
        # Generate registration code
        # In production, this would be fetched from the API
        reg_code = generate_registration_code()
        logger.info(f"Registration code: {reg_code}")
        
        # Show welcome screen
        display.show_welcome_screen(reg_code)
        
        logger.info("Display updated successfully")
        logger.info("Press Ctrl+C to exit")
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        if 'display' in locals():
            display.sleep()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
