#!/usr/bin/env python3
"""
Native Waveshare test using their exact pattern
This matches the official Waveshare example code
"""

import sys
import time

print("Waveshare Native Test")
print("=====================")
print("Using official Waveshare initialization pattern")
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
print("=" * 60)
print("IMPORTANT: Make sure no other software is using the display!")
print("If InkyPi is running, stop it first:")
print("  sudo systemctl stop inkypi")
print("=" * 60)
print()
input("Press Enter to continue...")

epd = None

try:
    print()
    print("Step 1: Create EPD object")
    print("-" * 60)
    epd = epd7in3e.EPD()
    print("✓ EPD object created")
    
    print()
    print("Step 2: Initialize display")
    print("-" * 60)
    print("Calling epd.init()...")
    epd.init()
    print("✓ init() completed")
    
    print()
    print("Step 3: Create test image")
    print("-" * 60)
    print(f"Display size: {epd.width} x {epd.height}")
    
    # Create image
    image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Load font
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
        font_med = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 50)
    except:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
    
    # Draw text
    draw.text((100, 300), "LUMY TEST", font=font_large, fill=(0, 0, 0))
    draw.text((100, 450), "Waveshare 7.3\" E-Paper", font=font_med, fill=(0, 0, 255))
    
    # Draw colored rectangles
    colors = [
        ("Black", (0, 0, 0)),
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("Yellow", (255, 255, 0)),
    ]
    
    x = 100
    y = 700
    for name, color in colors:
        draw.rectangle([x, y, x+250, y+250], fill=color, outline=(0, 0, 0), width=3)
        draw.text((x+10, y+270), name, font=font_med, fill=(0, 0, 0))
        x += 300
    
    print("✓ Test image created")
    
    print()
    print("Step 4: Display image (WATCH THE DISPLAY!)")
    print("-" * 60)
    print("This will take 20-30 seconds...")
    print("The display SHOULD flash multiple times!")
    print()
    
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    
    print()
    print("DISPLAYING NOW - WATCH THE SCREEN!")
    start = time.time()
    
    # Get buffer and display
    buffer = epd.getbuffer(image)
    epd.display(buffer)
    
    elapsed = time.time() - start
    print(f"✓ Display command completed in {elapsed:.1f} seconds")
    
    print()
    response = input("Did the display flash and show the test image? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        print("🎉 SUCCESS! The display is working!")
        print()
        print("Next steps:")
        print("1. Your Lumy installation should now work")
        print("2. Run: cd ~/lumy/backend && python3 main.py")
    else:
        print()
        print("✗ Display still not responding")
        print()
        print("Additional troubleshooting:")
        print()
        print("1. CHECK FOR INKYPI CONFLICT:")
        print("   Run: sudo bash scripts/diagnose-conflict.sh")
        print()
        print("2. TRY COMPLETE POWER CYCLE:")
        print("   sudo shutdown -h now")
        print("   Unplug power for 30 seconds")
        print("   Plug back in and try again")
        print()
        print("3. VERIFY DISPLAY MODEL:")
        print("   Is it definitely 7.3inch HAT (E)?")
        print("   Check the back of the display board")
        print()
        print("4. CHECK WAVESHARE EXAMPLES:")
        print("   cd /tmp/e-Paper/RaspberryPi_JetsonNano/python/examples")
        print("   python3 epd_7in3e_test.py")
    
    # Sleep
    print()
    print("Putting display to sleep...")
    time.sleep(2)
    epd.sleep()
    print("✓ Done")
    
except KeyboardInterrupt:
    print()
    print("✗ Interrupted")
    if epd:
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
    
    if epd:
        try:
            epd.sleep()
        except:
            pass
    
    sys.exit(1)
