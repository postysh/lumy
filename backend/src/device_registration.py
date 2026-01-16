"""Device registration and pairing system"""

import asyncio
import logging
import os
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class DeviceRegistration:
    """Handles device registration and pairing flow"""
    
    def __init__(self, config):
        self.config = config
        self.device_id = None
        self.registration_code = None
        self.is_registered = False
        self.user_id = None
        
    def get_or_create_device_id(self) -> str:
        """Get existing device ID or create a new one based on MAC address"""
        # Check if device ID already exists in .env
        device_id = os.getenv('LUMY_DEVICE_ID')
        if device_id:
            logger.info(f"Using existing device ID: {device_id}")
            return device_id
        
        # Generate new device ID based on MAC address
        try:
            # Get MAC address of eth0 or wlan0
            mac = None
            for interface in ['eth0', 'wlan0']:
                mac_path = f'/sys/class/net/{interface}/address'
                if Path(mac_path).exists():
                    with open(mac_path, 'r') as f:
                        mac = f.read().strip().replace(':', '')
                    break
            
            if mac:
                # Use last 8 characters of MAC + random suffix
                device_id = f"lumy-{mac[-8:]}-{uuid.uuid4().hex[:4]}"
            else:
                # Fallback to pure random ID
                device_id = f"lumy-{uuid.uuid4().hex[:12]}"
            
            logger.info(f"Generated new device ID: {device_id}")
            self._save_device_id_to_env(device_id)
            return device_id
            
        except Exception as e:
            logger.error(f"Error generating device ID: {e}")
            # Fallback
            device_id = f"lumy-{uuid.uuid4().hex[:12]}"
            self._save_device_id_to_env(device_id)
            return device_id
    
    def _save_device_id_to_env(self, device_id: str):
        """Save device ID to .env file"""
        env_file = Path(__file__).parent.parent / '.env'
        
        # Read existing .env
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Update or add LUMY_DEVICE_ID
        found = False
        for i, line in enumerate(lines):
            if line.startswith('LUMY_DEVICE_ID='):
                lines[i] = f'LUMY_DEVICE_ID={device_id}\n'
                found = True
                break
        
        if not found:
            lines.append(f'LUMY_DEVICE_ID={device_id}\n')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        logger.info(f"Saved device ID to .env: {device_id}")
    
    def generate_registration_code(self) -> str:
        """Generate a 6-character registration code (ABC-123 format)"""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=3))
        code = f"{letters}-{numbers}"
        logger.info(f"Generated registration code: {code}")
        return code
    
    async def check_registration_status(self) -> bool:
        """Check if device is registered in Supabase"""
        try:
            import aiohttp
            
            api_url = os.getenv('LUMY_API_URL')
            api_key = os.getenv('LUMY_API_KEY')
            
            if not api_url or not api_key:
                logger.warning("API URL or API key not configured")
                return False
            
            async with aiohttp.ClientSession() as session:
                url = f"{api_url}/devices/{self.device_id}/registration"
                headers = {"X-API-KEY": api_key}
                
                logger.debug(f"Checking registration status: {url}")
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Registration check response: {data}")
                        
                        if data.get('registered'):
                            self.is_registered = True
                            self.user_id = data.get('user_id')
                            logger.info(f"✓ Device is registered to user: {self.user_id}")
                            return True
                        else:
                            logger.debug(f"Device not yet registered (checked at {url})")
                    else:
                        logger.warning(f"Registration check failed with status: {response.status}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking registration status: {e}", exc_info=True)
            return False
    
    async def send_registration_code(self):
        """Send registration code to Supabase"""
        try:
            import aiohttp
            
            api_url = os.getenv('LUMY_API_URL')
            api_key = os.getenv('LUMY_API_KEY')
            
            if not api_url or not api_key:
                logger.error("API URL or API key not configured, cannot register")
                return False
            
            async with aiohttp.ClientSession() as session:
                url = f"{api_url}/devices/register"
                headers = {"X-API-KEY": api_key}
                payload = {
                    "device_id": self.device_id,
                    "registration_code": self.registration_code,
                    "expires_in": 3600  # 1 hour
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info("Registration code sent to cloud")
                        return True
                    else:
                        logger.error(f"Failed to send registration code: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending registration code: {e}")
            return False
    
    async def wait_for_registration(self, display_manager, timeout=3600):
        """Wait for device to be registered (poll every 5 seconds)"""
        logger.info(f"Waiting for device registration (device_id: {self.device_id})...")
        logger.info(f"Registration code: {self.registration_code}")
        
        start_time = datetime.now()
        check_count = 0
        
        while (datetime.now() - start_time).seconds < timeout:
            check_count += 1
            logger.info(f"Registration check #{check_count} (elapsed: {(datetime.now() - start_time).seconds}s)")
            
            # Check if registered
            if await self.check_registration_status():
                logger.info("✓ Device successfully registered!")
                return True
            
            # Wait 5 seconds before checking again
            await asyncio.sleep(5)
        
        logger.warning(f"Registration timeout after {check_count} checks - no registration received")
        return False
    
    async def show_welcome_screen(self, display_manager):
        """Display welcome screen with registration code"""
        from PIL import Image, ImageDraw, ImageFont
        
        try:
            # Create white background
            image = Image.new('RGB', (display_manager.width, display_manager.height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Load fonts (MASSIVE sizes for 800x480 display - MUST BE READABLE)
            try:
                font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
                font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
                font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 52)
                font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 38)
                logger.info("Fonts loaded successfully - title:100pt, large:80pt, medium:52pt, small:38pt")
            except Exception as e:
                logger.error(f"FONT LOADING FAILED: {e} - Using default fonts which are TOO SMALL")
                font_title = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Calculate center positions
            center_x = display_manager.width // 2
            
            # Draw "Welcome to Lumy"
            title_text = "Welcome to Lumy"
            title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text((center_x - title_width // 2, 15), title_text, font=font_title, fill=(0, 0, 0))
            
            # Draw registration instructions
            instruction1 = "To register:"
            instruction1_bbox = draw.textbbox((0, 0), instruction1, font=font_medium)
            instruction1_width = instruction1_bbox[2] - instruction1_bbox[0]
            draw.text((center_x - instruction1_width // 2, 135), instruction1, font=font_medium, fill=(0, 0, 0))
            
            instruction2 = "lumy-beta.vercel.app"
            instruction2_bbox = draw.textbbox((0, 0), instruction2, font=font_medium)
            instruction2_width = instruction2_bbox[2] - instruction2_bbox[0]
            draw.text((center_x - instruction2_width // 2, 195), instruction2, font=font_medium, fill=(0, 100, 200))
            
            # Draw registration code in a box
            code_y = 290
            box_padding = 22
            code_text = f"{self.registration_code}"
            code_bbox = draw.textbbox((0, 0), code_text, font=font_large)
            code_width = code_bbox[2] - code_bbox[0]
            code_height = code_bbox[3] - code_bbox[1]
            
            # Draw box around code
            box_left = center_x - code_width // 2 - box_padding
            box_right = center_x + code_width // 2 + box_padding
            box_top = code_y - box_padding
            box_bottom = code_y + code_height + box_padding
            draw.rectangle([box_left, box_top, box_right, box_bottom], outline=(255, 100, 0), width=6)
            
            # Draw code
            draw.text((center_x - code_width // 2, code_y), code_text, font=font_large, fill=(255, 100, 0))
            
            # Draw device ID at bottom
            device_text = f"Device: {self.device_id}"
            device_bbox = draw.textbbox((0, 0), device_text, font=font_small)
            device_width = device_bbox[2] - device_bbox[0]
            draw.text((center_x - device_width // 2, 435), device_text, font=font_small, fill=(128, 128, 128))
            
            # Display image
            await display_manager.display_image(image)
            logger.info("Welcome screen displayed")
            
        except Exception as e:
            logger.error(f"Error showing welcome screen: {e}", exc_info=True)
    
    async def initialize_and_register(self, display_manager):
        """Main registration flow"""
        logger.info("Starting device registration flow...")
        
        # Get or create device ID
        self.device_id = self.get_or_create_device_id()
        
        # Check if already registered
        if await self.check_registration_status():
            logger.info("Device is already registered - skipping registration flow")
            self.is_registered = True
            return True
        
        # Generate registration code
        self.registration_code = self.generate_registration_code()
        
        # Send code to cloud
        await self.send_registration_code()
        
        # Show welcome screen
        await self.show_welcome_screen(display_manager)
        
        # Wait for registration
        registered = await self.wait_for_registration(display_manager, timeout=3600)
        
        if registered:
            # Save user_id to .env
            self._save_user_id_to_env(self.user_id)
            logger.info("Device registration complete!")
            return True
        else:
            logger.warning("Device registration timed out")
            return False
    
    def _save_user_id_to_env(self, user_id: str):
        """Save user ID to .env file"""
        env_file = Path(__file__).parent.parent / '.env'
        
        # Read existing .env
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Update or add LUMY_USER_ID
        found = False
        for i, line in enumerate(lines):
            if line.startswith('LUMY_USER_ID='):
                lines[i] = f'LUMY_USER_ID={user_id}\n'
                found = True
                break
        
        if not found:
            lines.append(f'LUMY_USER_ID={user_id}\n')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        logger.info(f"Saved user ID to .env: {user_id}")
