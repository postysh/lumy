#!/usr/bin/env python3
"""
Helper module for E-Paper scripts
Handles automatic GPIO cleanup before operations
"""

import sys
import time
import subprocess

def cleanup_gpio():
    """Force cleanup of any stuck GPIO from previous runs"""
    print("Auto-cleanup: Releasing any stuck GPIO pins...")
    
    try:
        # Try to release via epdconfig module exit
        try:
            from waveshare_epd import epdconfig
            epdconfig.module_exit()
            time.sleep(0.2)
        except:
            pass
        
        # Kill any other Python processes that might be holding GPIO
        # (but not ourselves)
        import os
        my_pid = os.getpid()
        
        try:
            result = subprocess.run(['pgrep', '-f', 'python.*epd|python.*lumy|python.*test'], 
                                  capture_output=True, text=True, timeout=2)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid and int(pid) != my_pid:
                        subprocess.run(['sudo', 'kill', '-9', pid], 
                                     stderr=subprocess.DEVNULL, timeout=1)
        except:
            pass
        
        time.sleep(0.3)
        print("✓ GPIO cleanup complete")
        return True
        
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")
        return False

def init_display(model='epd7in3e'):
    """
    Initialize E-Paper display with automatic cleanup
    Returns: epd object or None
    """
    cleanup_gpio()
    
    try:
        import importlib
        epd_module = importlib.import_module(f'waveshare_epd.{model}')
        epd = epd_module.EPD()
        epd.init()
        return epd
    except Exception as e:
        print(f"✗ Failed to initialize display: {e}")
        return None
