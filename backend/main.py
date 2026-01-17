#!/usr/bin/python3
"""
Lumy Display Service
Shows registration code after WiFi is configured
"""

import sys
sys.path.append('/usr/local/lib/python3.11/dist-packages')

from waveshare_epd import epd7in3e
from PIL import Image, ImageDraw, ImageFont
import random
import string

def generate_registration_code():
    """Generate 6-character registration code"""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1')
    return ''.join(random.choices(chars, k=6))

def get_device_id():
    """Get device ID from MAC address"""
    try:
        with open('/sys/class/net/wlan0/address', 'r') as f:
            mac = f.read().strip().replace(':', '')[-6:].upper()
            return f"LUMY-{mac}"
    except:
        return f"LUMY-{''.join(random.choices('0123456789ABCDEF', k=6))}"

def show_registration_screen():
    """Display registration code"""
    try:
        print("Initializing display...")
        epd = epd7in3e.EPD()
        epd.init()
        epd.Clear()
        
        # Generate codes
        registration_code = generate_registration_code()
        device_id = get_device_id()
        
        # Create white background
        image = Image.new('RGB', (800, 480), 0xFFFFFF)
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 76)
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 68)
            font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 48)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
        except:
            print("Warning: Could not load fonts, using default")
            font_title = ImageFont.load_default()
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        center_x = 400
        
        # Title
        title = "Welcome to Lumy"
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_w = bbox[2] - bbox[0]
        draw.text((center_x - title_w // 2, 20), title, font=font_title, fill=0x000000)
        
        # Instructions
        inst1 = "Register at:"
        bbox = draw.textbbox((0, 0), inst1, font=font_medium)
        inst1_w = bbox[2] - bbox[0]
        draw.text((center_x - inst1_w // 2, 135), inst1, font=font_medium, fill=0x000000)
        
        inst2 = "lumy-beta.vercel.app"
        bbox = draw.textbbox((0, 0), inst2, font=font_medium)
        inst2_w = bbox[2] - bbox[0]
        draw.text((center_x - inst2_w // 2, 195), inst2, font=font_medium, fill=0x0000FF)
        
        # Registration code in box
        code_y = 290
        bbox = draw.textbbox((0, 0), registration_code, font=font_large)
        code_w = bbox[2] - bbox[0]
        code_h = bbox[3] - bbox[1]
        
        padding = 22
        draw.rectangle([
            center_x - code_w // 2 - padding,
            code_y - padding,
            center_x + code_w // 2 + padding,
            code_y + code_h + padding
        ], outline=0xFF6600, width=6)
        
        draw.text((center_x - code_w // 2, code_y), registration_code, font=font_large, fill=0xFF6600)
        
        # Device ID
        device_text = f"Device: {device_id}"
        bbox = draw.textbbox((0, 0), device_text, font=font_small)
        device_w = bbox[2] - bbox[0]
        draw.text((center_x - device_w // 2, 410), device_text, font=font_small, fill=0x808080)
        
        # Display
        epd.display(epd.getbuffer(image))
        epd.sleep()
        
        print(f"Registration screen displayed")
        print(f"  Code: {registration_code}")
        print(f"  Device: {device_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_registration_screen()
