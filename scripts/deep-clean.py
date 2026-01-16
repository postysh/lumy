#!/usr/bin/env python3
"""
Deep clean the E-Paper display to remove ghosting/afterimages
This does multiple full refresh cycles to completely clear old images
"""

import sys
import time

print("E-Paper Deep Clean")
print("==================")
print()
print("This will do multiple refresh cycles to remove ghosting")
print("from the old InkyPi image. This will take 3-5 minutes.")
print()

try:
    from waveshare_epd import epd7in3e
    print("✓ Imported epd7in3e")
except ImportError as e:
    print(f"✗ Cannot import: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
    print("✓ Imported PIL")
except ImportError as e:
    print(f"✗ Cannot import PIL: {e}")
    sys.exit(1)

print()
input("Press Enter to start deep cleaning...")
print()

try:
    print("Initializing display...")
    epd = epd7in3e.EPD()
    epd.init()
    print("✓ Display initialized")
    print()
    
    # Do multiple clear cycles
    num_cycles = 3
    for cycle in range(1, num_cycles + 1):
        print(f"Cycle {cycle}/{num_cycles}: Clearing display...")
        print("(This takes ~30-60 seconds per cycle)")
        
        start = time.time()
        epd.Clear()
        elapsed = time.time() - start
        
        print(f"✓ Cycle {cycle} completed in {elapsed:.1f} seconds")
        
        if cycle < num_cycles:
            print("Waiting 2 seconds before next cycle...")
            time.sleep(2)
        print()
    
    # Display a fresh white screen
    print("Displaying clean white screen...")
    image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
    buffer = epd.getbuffer(image)
    epd.display(buffer)
    print("✓ Clean white screen displayed")
    
    print()
    print("=" * 60)
    print("Deep clean complete!")
    print("=" * 60)
    print()
    print("The ghosting should be significantly reduced or gone.")
    print("If you still see some ghosting, run this script again.")
    print()
    print("According to Waveshare:")
    print("- Full refresh removes afterimages")
    print("- Multiple cycles = better results")
    print("- Avoid keeping the same image for > 24 hours")
    print()
    
    # Sleep
    print("Putting display to sleep...")
    time.sleep(2)
    epd.sleep()
    print("✓ Done")
    print()
    print("Next steps:")
    print("1. Test with: python3 scripts/waveshare-native-test.py")
    print("2. Or start Lumy: cd ~/lumy/backend && python3 main.py")
    
except KeyboardInterrupt:
    print()
    print("✗ Interrupted")
    try:
        epd.sleep()
    except:
        pass
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    
    try:
        epd.sleep()
    except:
        pass
    
    sys.exit(1)
