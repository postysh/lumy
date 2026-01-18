#!/usr/bin/env python3
"""
Quick test script to verify e-paper display is working
Run this directly on the Raspberry Pi: python3 test-display.py
"""
import sys
import os

# Add the lib directory to path
lib_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'lib')
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd7in3e
import time

def main():
    print("Initializing e-paper display...")
    epd = epd7in3e.EPD()
    epd.init()
    
    print("Creating test image...")
    width = 800
    height = 480
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw some test patterns
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
    
    # Draw text
    text = "Lumy Test Display"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, 200), text, font=font, fill='black')
    
    # Draw a rectangle
    draw.rectangle([50, 50, 750, 430], outline='black', width=3)
    
    print("Displaying image on e-paper...")
    epd.display(epd.getbuffer(image))
    
    print("Success! Display updated.")
    print("Putting display to sleep...")
    epd.sleep()
    print("Done!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
