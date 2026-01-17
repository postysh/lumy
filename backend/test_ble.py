#!/usr/bin/python3
"""
Simple BLE test - check if Bluetooth is working
"""

import sys

try:
    print("Testing Bluetooth...")
    print("")
    
    # Test 1: Check if bluetooth service is running
    import subprocess
    result = subprocess.run(['systemctl', 'is-active', 'bluetooth'], capture_output=True, text=True)
    if result.stdout.strip() == 'active':
        print("✓ Bluetooth service is running")
    else:
        print("✗ Bluetooth service is NOT running")
        print("  Run: sudo systemctl start bluetooth")
        sys.exit(1)
    
    # Test 2: Check if hci0 exists
    result = subprocess.run(['hciconfig', 'hci0'], capture_output=True, text=True)
    if 'hci0' in result.stdout:
        print("✓ Bluetooth adapter (hci0) found")
    else:
        print("✗ Bluetooth adapter not found")
        sys.exit(1)
    
    # Test 3: Try importing bluezero
    try:
        from bluezero import adapter
        print("✓ Bluezero library installed")
        
        # Test 4: Get adapter
        adapt = adapter.Adapter()
        print(f"✓ Adapter address: {adapt.address}")
        print(f"  Adapter name: {adapt.name}")
        print(f"  Powered: {adapt.powered}")
        
    except ImportError:
        print("✗ Bluezero not installed")
        print("  Run: pip3 install bluezero --break-system-packages")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error accessing Bluetooth adapter: {e}")
        sys.exit(1)
    
    print("")
    print("✓ All Bluetooth checks passed!")
    print("")
    print("To start BLE server:")
    print("  sudo systemctl start lumy-ble")
    print("  sudo journalctl -u lumy-ble -f")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
