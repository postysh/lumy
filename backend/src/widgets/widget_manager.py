"""Widget manager for display apps and features"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import importlib
import importlib.util

from src.widgets.base_widget import BaseWidget

logger = logging.getLogger(__name__)


class WidgetManager:
    """Manages widgets and display layout"""
    
    def __init__(self, config, display_manager):
        self.config = config
        self.display_manager = display_manager
        
        self.widgets: Dict[str, BaseWidget] = {}
        self.widget_layout: List[Dict] = []
        self.update_interval = config.get('widgets.update_interval', 60)
        self._running = False
        self._update_task = None
    
    async def initialize(self):
        """Initialize widget system"""
        logger.info("Initializing widget manager...")
        
        # Load default widgets
        default_widgets = self.config.get('widgets.default_widgets', [])
        for widget_name in default_widgets:
            await self.load_widget(widget_name)
        
        logger.info(f"Loaded {len(self.widgets)} widgets")
    
    async def load_widget(self, widget_name: str) -> bool:
        """Load a widget by name"""
        try:
            # Try to import widget module
            widget_path = Path(self.config.get('paths.widgets')) / f"{widget_name}_widget.py"
            
            if widget_path.exists():
                spec = importlib.util.spec_from_file_location(
                    f"widgets.{widget_name}",
                    widget_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get widget class (should be named like ClockWidget)
                class_name = f"{widget_name.capitalize()}Widget"
                widget_class = getattr(module, class_name, None)
                
                if widget_class:
                    widget = widget_class(self.config)
                    await widget.initialize()
                    self.widgets[widget_name] = widget
                    logger.info(f"Loaded widget: {widget_name}")
                    return True
            
            logger.warning(f"Widget not found: {widget_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load widget {widget_name}: {e}", exc_info=True)
            return False
    
    async def start(self):
        """Start widget update loop"""
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Widget manager started")
    
    async def stop(self):
        """Stop widget manager"""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Widget manager stopped")
    
    async def _update_loop(self):
        """Periodic widget update loop"""
        while self._running:
            try:
                # Update all widgets
                for widget_name, widget in self.widgets.items():
                    try:
                        await widget.update()
                    except Exception as e:
                        logger.error(f"Error updating widget {widget_name}: {e}")
                
                # Render display
                await self.render_display()
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in widget update loop: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def render_display(self) -> bool:
        """Render all widgets to display"""
        try:
            logger.info("Rendering display...")
            
            # Create canvas
            canvas = self.display_manager.create_canvas()
            draw = ImageDraw.Draw(canvas)
            
            # Simple layout: stack widgets vertically
            # In production, you'd have a more sophisticated layout system
            y_offset = 0
            widget_height = self.display_manager.height // max(len(self.widgets), 1)
            
            for widget_name, widget in self.widgets.items():
                try:
                    # Get widget image
                    widget_image = await widget.render(
                        width=self.display_manager.width,
                        height=widget_height
                    )
                    
                    if widget_image:
                        # Paste widget onto canvas
                        canvas.paste(widget_image, (0, y_offset))
                        y_offset += widget_height
                        
                except Exception as e:
                    logger.error(f"Error rendering widget {widget_name}: {e}")
            
            # Display on E-Paper
            success = await self.display_manager.display_image(canvas)
            
            if success:
                logger.info("Display rendered successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to render display: {e}", exc_info=True)
            return False
    
    async def update_widget(self, widget_id: str, data: Dict) -> bool:
        """Update specific widget with new data"""
        widget = self.widgets.get(widget_id)
        if not widget:
            logger.warning(f"Widget not found: {widget_id}")
            return False
        
        try:
            await widget.update_data(data)
            await widget.update()
            await self.render_display()
            return True
        except Exception as e:
            logger.error(f"Failed to update widget {widget_id}: {e}")
            return False
    
    async def trigger_widget(self, widget_id: str, data: Dict) -> bool:
        """Trigger a widget action"""
        widget = self.widgets.get(widget_id)
        if not widget:
            return False
        
        try:
            await widget.trigger(data)
            return True
        except Exception as e:
            logger.error(f"Failed to trigger widget {widget_id}: {e}")
            return False
    
    async def get_widget_status(self) -> Dict:
        """Get status of all widgets"""
        status = {}
        for widget_name, widget in self.widgets.items():
            status[widget_name] = {
                'loaded': True,
                'last_update': getattr(widget, 'last_update', None),
                'data': getattr(widget, 'data', {})
            }
        return status
