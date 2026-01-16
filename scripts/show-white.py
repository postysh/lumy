#!/usr/bin/env python3
"""
Simple script to display a white screen
Uses the EXACT pattern that worked in waveshare-native-test.py
"""

import sys
import time
import subprocess

print("Display White Screen")
print("====================")
print()

# Kill any stuck processes first
print("Cleaning up...")
subprocess.run(['sudo', 'pkill', '-9', 'python3'], stderr=subprocess.DEVNULL)
subprocess.run(['sudo', 'pkill', '-9', 'python'], stderr=subprocess.DEVNULL)
time.sleep(1)
print("✓ Cleanup done")
print()

try:
    from waveshare_epd import epd7in3e
    from PIL import Image
    print("✓ Libraries imported")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

print()
print("Initializing display...")
epd = epd7in3e.EPD()
epd.init()
print("✓ Display initialized")

print()
print("Creating white image...")
image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
print("✓ Image created")

print()
print("Displaying white screen...")
print("WATCH THE DISPLAY - it should flash!")
print()

for i in range(3, 0, -1):
    print(f"Starting in {i}...")
    time.sleep(1)

print()
print("DISPLAYING NOW!")
start = time.time()
buffer = epd.getbuffer(image)
epd.display(buffer)
elapsed = time.time() - start

print(f"✓ Completed in {elapsed:.1f} seconds")
print()

response = input("Did the display flash and show white? (yes/no): ").strip().lower()

if response in ['yes', 'y']:
    print()
    print("✓ Good! Want to repeat this 2 more times to fully remove ghosting?")
    repeat = input("Repeat? (yes/no): ").strip().lower()
    
    if repeat in ['yes', 'y']:
        for cycle in range(2, 4):
            print()
            print(f"Cycle {cycle}/3...")
            time.sleep(2)
            
            # Re-init and display white
            epd.init()
            image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
            buffer = epd.getbuffer(image)
            epd.display(buffer)
            print(f"✓ Cycle {cycle} complete")
        
        print()
        print("✓ All cycles complete! Ghosting should be gone.")
else:
    print()
    print("✗ Display not responding")
    print()
    print("Try rebooting: sudo reboot")

print()
print("Putting display to sleep...")
time.sleep(2)
epd.sleep()
print("✓ Done")
