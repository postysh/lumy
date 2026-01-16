#!/usr/bin/env python3
"""
Force clear the display with aggressive reset
This should remove the old InkyPi image
"""

import sys
import time

print("Force Clear E-Paper Display")
print("============================")
print()
print("This will aggressively clear the old InkyPi image")
print()

try:
    from waveshare_epd import epd7in3e
    from waveshare_epd import epdconfig
    print("✓ Waveshare library loaded")
except ImportError as e:
    print(f"✗ Cannot import: {e}")
    sys.exit(1)

try:
    print()
    print("Step 1: Hard reset of the display hardware")
    print("-" * 50)
    
    # Force module exit first to reset everything
    try:
        epdconfig.module_exit()
        time.sleep(1)
    except:
        pass
    
    print("Initializing GPIO and SPI...")
    # Manual initialization of epdconfig
    if epdconfig.module_init() != 0:
        print("✗ Failed to initialize epdconfig")
        sys.exit(1)
    print("✓ GPIO/SPI initialized")
    
    print()
    print("Step 2: Create EPD object and initialize display")
    print("-" * 50)
    
    epd = epd7in3e.EPD()
    
    print("Calling epd.init()...")
    epd.init()
    print("✓ Display initialized")
    
    print()
    print("Step 3: Clear the display")
    print("-" * 50)
    print("This will take 30-60 seconds...")
    print("WATCH THE DISPLAY - it should flash multiple times!")
    print()
    
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    
    print()
    print("CLEARING NOW!")
    start = time.time()
    
    # Try the Clear function
    epd.Clear()
    
    elapsed = time.time() - start
    print(f"✓ Clear completed in {elapsed:.1f} seconds")
    
    print()
    response = input("Did the display flash and clear? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        print("✓ GREAT! The display is now working with our code!")
        print()
        print("Now let's display a simple test pattern...")
        
        from PIL import Image, ImageDraw, ImageFont
        
        # Re-init for display
        epd.init()
        
        # Create a simple test image
        print("Creating test image...")
        image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw "LUMY" in large letters
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 200)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 60)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Title
        draw.text((200, 400), "LUMY", font=font, fill=(0, 0, 0))
        draw.text((200, 650), "E-Paper Display Working!", font=font_small, fill=(0, 128, 0))
        
        # Draw colored boxes
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green  
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 128, 0),  # Orange
        ]
        
        x = 200
        y = 900
        for color in colors:
            draw.rectangle([x, y, x+200, y+200], fill=color, outline=(0, 0, 0), width=3)
            x += 250
        
        print("Displaying test pattern (20-40 seconds)...")
        buffer = epd.getbuffer(image)
        epd.display(buffer)
        
        print()
        print("✓ Test pattern displayed!")
        print()
        print("Check your display - you should see 'LUMY' and colored boxes")
        
    else:
        print()
        print("✗ Display still not responding")
        print()
        print("Let's try a different approach...")
        print()
        
        # Try direct pixel buffer
        print("Attempting to send a direct pixel buffer...")
        
        # Create a simple black and white pattern
        from PIL import Image, ImageDraw
        
        # Re-init
        epd.init()
        
        # Create alternating stripes
        image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw thick black stripes
        for i in range(0, epd.height, 200):
            draw.rectangle([0, i, epd.width, i+100], fill=(0, 0, 0))
        
        print("Sending stripe pattern...")
        buffer = epd.getbuffer(image)
        epd.display(buffer)
        
        print()
        print("Check if you see horizontal stripes on the display")
        print()
        response2 = input("Do you see stripes? (yes/no): ").strip().lower()
        
        if response2 in ['yes', 'y']:
            print("✓ Display is responding to display() but not Clear()")
            print("  This is a known quirk - we can work with this!")
        else:
            print()
            print("Troubleshooting:")
            print("1. The display might need a complete power cycle")
            print("2. Try: sudo shutdown -h now")
            print("3. Unplug power for 30 seconds")
            print("4. Boot back up and try again")
    
    # Sleep and cleanup
    print()
    print("Putting display to sleep and cleaning up...")
    time.sleep(2)
    epd.sleep()
    epdconfig.module_exit()
    print("✓ Done")
    
except KeyboardInterrupt:
    print()
    print("✗ Interrupted")
    try:
        epdconfig.module_exit()
    except:
        pass
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    
    try:
        epdconfig.module_exit()
    except:
        pass
    
    sys.exit(1)
