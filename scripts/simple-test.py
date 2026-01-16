#!/usr/bin/env python3
"""
Simple E-Paper test with verbose output
This test is faster and shows what's happening
"""

import sys
import time

print("Simple E-Paper Test")
print("===================")
print()

# Check library
try:
    from waveshare_epd import epd7in3e
    print("✓ Waveshare library loaded")
except ImportError as e:
    print(f"✗ Cannot import waveshare_epd: {e}")
    sys.exit(1)

# Check epdconfig
try:
    from waveshare_epd import epdconfig
    print("✓ epdconfig loaded")
except ImportError as e:
    print(f"✗ Cannot import epdconfig: {e}")
    sys.exit(1)

print()
print("Initializing hardware...")
print("This will:")
print("1. Initialize GPIO pins")
print("2. Initialize SPI")
print("3. Send reset command to display")
print()

try:
    # Initialize
    print("Creating EPD object...")
    epd = epd7in3e.EPD()
    print("✓ EPD object created")
    
    print()
    print("Calling epd.init()...")
    print("(If this hangs, press Ctrl+C and check hardware connections)")
    
    start = time.time()
    epd.init()
    elapsed = time.time() - start
    
    print(f"✓ Display initialized in {elapsed:.2f} seconds")
    print()
    
    # Try a quick clear (this should make the display flash)
    print("Sending clear command to display...")
    print("Watch the display - it should flash black/white several times")
    print()
    
    start = time.time()
    epd.Clear()
    elapsed = time.time() - start
    
    print(f"✓ Clear command completed in {elapsed:.1f} seconds")
    print()
    
    # Sleep the display
    print("Putting display to sleep...")
    epd.sleep()
    print("✓ Display in sleep mode")
    
    # Cleanup
    print()
    print("Cleaning up GPIO...")
    epdconfig.module_exit()
    print("✓ GPIO released")
    
    print()
    print("======================")
    print("✓ Test completed!")
    print("======================")
    print()
    
    if elapsed < 5:
        print("⚠ WARNING: Clear command finished very quickly!")
        print("  This might mean the display is not responding.")
        print("  Expected time: 30-60 seconds")
        print("  Actual time: {:.1f} seconds".format(elapsed))
        print()
        print("Troubleshooting:")
        print("1. Check that the display cable is connected")
        print("2. Check that the HAT is properly seated on GPIO pins")
        print("3. Run: sudo bash scripts/check-hardware.sh")
    else:
        print("Display is working correctly!")
        print("You should have seen the display flash multiple times.")
        print()
        print("Next step: Run the full test")
        print("  python3 scripts/test-display.py")
    
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
    print()
    print("Troubleshooting:")
    print("1. Run hardware check: sudo bash scripts/check-hardware.sh")
    print("2. Check SPI is enabled: ls -l /dev/spidev0.0")
    print("3. Check user groups: groups")
    print("4. Reboot and try again: sudo reboot")
    
    try:
        epdconfig.module_exit()
    except:
        pass
    
    sys.exit(1)
