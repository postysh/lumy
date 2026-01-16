"""Base widget class for all display widgets"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)


class BaseWidget(ABC):
    """Abstract base class for widgets"""
    
    def __init__(self, config, widget_id: str = None):
        self.config = config
        self.widget_id = widget_id or self.__class__.__name__
        self.data: Dict[str, Any] = {}
        self.last_update: Optional[float] = None
        self.enabled = True
    
    @abstractmethod
    async def initialize(self):
        """Initialize the widget"""
        pass
    
    @abstractmethod
    async def update(self):
        """Update widget data"""
        pass
    
    @abstractmethod
    async def render(self, width: int, height: int) -> Image.Image:
        """Render widget to image"""
        pass
    
    async def update_data(self, data: Dict[str, Any]):
        """Update widget with new data"""
        self.data.update(data)
    
    async def trigger(self, data: Dict[str, Any]):
        """Trigger widget action"""
        logger.info(f"Widget {self.widget_id} triggered with: {data}")
    
    def create_canvas(self, width: int, height: int, bg_color=(255, 255, 255)) -> Image.Image:
        """Create a blank canvas for the widget"""
        return Image.new('RGB', (width, height), color=bg_color)
    
    def get_font(self, size: int = 20, font_name: str = None) -> ImageFont.ImageFont:
        """Get a font for rendering text"""
        try:
            if font_name:
                # Try to load custom font
                font_path = self.config.data_dir / 'fonts' / font_name
                return ImageFont.truetype(str(font_path), size)
            else:
                # Use default font
                return ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load font: {e}")
            return ImageFont.load_default()
    
    def draw_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        position: tuple,
        font: ImageFont.ImageFont = None,
        fill: tuple = (0, 0, 0),
        align: str = 'left'
    ):
        """Helper to draw text"""
        if font is None:
            font = self.get_font()
        
        draw.text(position, text, font=font, fill=fill, align=align)
    
    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.widget_id}>"
