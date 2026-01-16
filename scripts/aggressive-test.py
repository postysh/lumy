#!/usr/bin/env python3
"""
Aggressive E-Paper test with temperature check
Based on Waveshare documentation requirements
"""

import sys
import time

print("Aggressive E-Paper Test")
print("=======================")
print()

# Check library
try:
    from waveshare_epd import epd7in3e
    from waveshare_epd import epdconfig
    print("✓ Waveshare library loaded")
except ImportError as e:
    print(f"✗ Cannot import waveshare_epd: {e}")
    sys.exit(1)

print()
print("=" * 50)
print("IMPORTANT: 7-COLOR DISPLAY TEMPERATURE REQUIREMENTS")
print("=" * 50)
print("Working temperature: 15-35°C (59-95°F)")
print("The display will NOT respond if outside this range!")
print()
input("Press Enter to continue (check your room temperature)...")
print()

print("=" * 50)
print("HARDWARE CONNECTION CHECKLIST")
print("=" * 50)
print("1. HAT is firmly seated on all GPIO pins")
print("2. Ribbon cable is connected on BOTH ends:")
print("   - From HAT to Display Panel")
print("   - Cable contacts facing the correct direction")
print("3. Any protective film removed from display?")
print()
input("Press Enter to continue...")
print()

print("Starting aggressive initialization...")
print("This will try multiple reset cycles")
print()

try:
    # Multiple initialization attempts
    for attempt in range(1, 4):
        print(f"Initialization attempt {attempt}/3...")
        
        try:
            # Clean up any previous state
            try:
                epdconfig.module_exit()
                time.sleep(0.5)
            except:
                pass
            
            # Create fresh EPD object
            epd = epd7in3e.EPD()
            
            # Initialize
            print(f"  - Calling init()...")
            epd.init()
            print(f"  ✓ Init completed")
            
            # Try to wake it up if it was sleeping
            print(f"  - Sending wake command...")
            time.sleep(0.2)
            
            break
            
        except Exception as e:
            print(f"  ✗ Attempt {attempt} failed: {e}")
            if attempt == 3:
                raise
            time.sleep(1)
    
    print()
    print("=" * 50)
    print("SENDING CLEAR COMMAND")
    print("=" * 50)
    print("Watch the display NOW - it should flash multiple times!")
    print("Flashing pattern: Black -> White -> Black -> White...")
    print()
    print("Starting in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print()
    print("CLEARING NOW - WATCH THE DISPLAY!")
    print()
    
    start = time.time()
    epd.Clear()
    elapsed = time.time() - start
    
    print()
    print(f"Clear command finished in {elapsed:.1f} seconds")
    print()
    
    # Ask user
    print("=" * 50)
    print("DID YOU SEE THE DISPLAY FLASH?")
    print("=" * 50)
    response = input("Did the display flash black and white? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        print()
        print("✓ Great! Display is working!")
        print()
        print("Now let's draw a simple pattern...")
        
        from PIL import Image, ImageDraw, ImageFont
        
        # Create simple test pattern
        image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw large colored rectangles
        # Red
        draw.rectangle([100, 100, 400, 400], fill=(255, 0, 0), outline=(0, 0, 0), width=5)
        # Green
        draw.rectangle([500, 100, 800, 400], fill=(0, 255, 0), outline=(0, 0, 0), width=5)
        # Blue
        draw.rectangle([900, 100, 1200, 400], fill=(0, 0, 255), outline=(0, 0, 0), width=5)
        
        # Yellow
        draw.rectangle([100, 500, 400, 800], fill=(255, 255, 0), outline=(0, 0, 0), width=5)
        # Black
        draw.rectangle([500, 500, 800, 800], fill=(0, 0, 0), outline=(255, 0, 0), width=5)
        
        print("Displaying color pattern...")
        print("This will take 20-30 seconds...")
        
        buffer = epd.getbuffer(image)
        epd.display(buffer)
        
        print("✓ Pattern displayed!")
        print()
        print("Check your display - you should see colored rectangles")
        
    else:
        print()
        print("✗ Display did not flash - TROUBLESHOOTING:")
        print()
        print("1. CHECK TEMPERATURE:")
        print("   - Room must be 15-35°C (59-95°F)")
        print("   - Use a thermometer to verify")
        print()
        print("2. CHECK CABLE:")
        print("   - Disconnect and reconnect the ribbon cable")
        print("   - Ensure contacts are clean")
        print("   - Cable should be < 20cm (per Waveshare docs)")
        print()
        print("3. CHECK POWER:")
        print("   - Try a different power supply (2.5A minimum)")
        print("   - Check if the HAT has any LED indicators")
        print()
        print("4. TRY POWER CYCLE:")
        print("   - sudo shutdown -h now")
        print("   - Unplug power for 30 seconds")
        print("   - Plug back in and try again")
        print()
        print("5. CONTACT WAVESHARE:")
        print("   - Display might be defective")
        print("   - Check warranty/replacement")
    
    # Cleanup
    print()
    print("Cleaning up...")
    epd.sleep()
    epdconfig.module_exit()
    print("✓ Done")
    
except KeyboardInterrupt:
    print()
    print("✗ Test interrupted")
    try:
        epdconfig.module_exit()
    except:
        pass
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"✗ Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    
    try:
        epdconfig.module_exit()
    except:
        pass
    
    sys.exit(1)
