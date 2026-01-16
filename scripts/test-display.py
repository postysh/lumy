#!/usr/bin/env python3
"""
Test script for E-Paper display
Run this to verify your display is working correctly
"""

import sys
import time
import signal
import atexit
from PIL import Image, ImageDraw, ImageFont

try:
    from waveshare_epd import epd7in3e
    EPAPER_AVAILABLE = True
except ImportError:
    print("Warning: Waveshare library not found")
    EPAPER_AVAILABLE = False

def test_display():
    """Test the E-Paper display"""
    print("Testing Lumy E-Paper Display...")
    print("Display: Waveshare 7.3inch E-Paper HAT (E)")
    print("Resolution: 1872×1404")
    print("")
    
    if not EPAPER_AVAILABLE:
        print("ERROR: Waveshare library not installed")
        print("Please run: sudo python3 scripts/install.sh")
        return False
    
    epd = None
    
    def cleanup():
        """Cleanup GPIO on exit"""
        if epd is not None:
            try:
                epd7in3e.epdconfig.module_exit()
            except:
                pass
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    
    try:
        # Initialize display
        print("Initializing display...")
        epd = epd7in3e.EPD()
        epd.init()
        print("✓ Display initialized")
        
        # Clear display
        print("Clearing display (this takes 30-60 seconds, please wait)...")
        start_time = time.time()
        epd.Clear()
        clear_time = time.time() - start_time
        print(f"✓ Display cleared (took {clear_time:.1f} seconds)")
        
        # Create test image
        print("Creating test image...")
        image = Image.new('RGB', (epd.width, epd.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw test pattern
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Title
        draw.text((100, 200), "Lumy Display Test", font=font_large, fill=(0, 0, 0))
        
        # Info
        draw.text((100, 320), "✓ Display is working correctly!", font=font_small, fill=(0, 128, 0))
        draw.text((100, 400), f"Resolution: {epd.width}×{epd.height}", font=font_small, fill=(0, 0, 0))
        draw.text((100, 480), "Time: " + time.strftime("%Y-%m-%d %H:%M:%S"), font=font_small, fill=(0, 0, 0))
        
        # Color test boxes
        colors = [
            ("Black", (0, 0, 0)),
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)),
        ]
        
        x_start = 100
        y_start = 600
        box_size = 150
        spacing = 200
        
        for i, (name, color) in enumerate(colors):
            x = x_start + (i * spacing)
            draw.rectangle([x, y_start, x + box_size, y_start + box_size], fill=color, outline=(0, 0, 0), width=3)
            draw.text((x, y_start + box_size + 20), name, font=font_small, fill=(0, 0, 0))
        
        # Display image
        print("Displaying test pattern (this takes 20-40 seconds, please wait)...")
        start_time = time.time()
        buffer = epd.getbuffer(image)
        epd.display(buffer)
        display_time = time.time() - start_time
        print(f"✓ Test pattern displayed (took {display_time:.1f} seconds)")
        
        # Sleep
        print("Putting display to sleep...")
        time.sleep(2)
        epd.sleep()
        print("✓ Display sleep mode")
        
        # Cleanup GPIO
        print("Cleaning up GPIO...")
        epd7in3e.epdconfig.module_exit()
        print("✓ GPIO released")
        
        print("")
        print("=================================")
        print("✓ All tests passed successfully!")
        print("=================================")
        print("")
        print("Your Lumy display is ready to use!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n✗ Test interrupted by user")
        if epd is not None:
            try:
                epd7in3e.epdconfig.module_exit()
            except:
                pass
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if epd is not None:
            try:
                epd7in3e.epdconfig.module_exit()
            except:
                pass
        return False

if __name__ == "__main__":
    success = test_display()
    sys.exit(0 if success else 1)
