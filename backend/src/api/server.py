"""FastAPI server for web dashboard"""

import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)


class APIServer:
    """REST API server for web interface"""
    
    def __init__(self, config, display_manager, widget_manager, ble_server):
        self.config = config
        self.display_manager = display_manager
        self.widget_manager = widget_manager
        self.ble_server = ble_server
        
        self.app = FastAPI(title="Lumy API", version="1.0.0")
        self.server: Optional[uvicorn.Server] = None
        self.connected_websockets = set()
        
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        origins = self.config.get('api.cors_origins', ['*'])
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "Lumy API", "version": "1.0.0"}
        
        @self.app.get("/status")
        async def get_status():
            """Get system status"""
            return {
                "status": "online",
                "display": {
                    "initialized": self.display_manager.initialized,
                    "width": self.display_manager.width,
                    "height": self.display_manager.height,
                },
                "widgets": await self.widget_manager.get_widget_status(),
                "bluetooth": {
                    "enabled": self.config.bluetooth_enabled,
                    "connected_devices": len(self.ble_server.connected_devices)
                }
            }
        
        @self.app.post("/display/refresh")
        async def refresh_display():
            """Trigger display refresh"""
            success = await self.widget_manager.render_display()
            if success:
                return {"status": "success", "message": "Display refreshed"}
            else:
                raise HTTPException(status_code=500, detail="Failed to refresh display")
        
        @self.app.post("/display/clear")
        async def clear_display():
            """Clear the display"""
            success = await self.display_manager.clear_display()
            if success:
                return {"status": "success", "message": "Display cleared"}
            else:
                raise HTTPException(status_code=500, detail="Failed to clear display")
        
        @self.app.get("/widgets")
        async def list_widgets():
            """List all loaded widgets"""
            return {
                "widgets": list(self.widget_manager.widgets.keys()),
                "count": len(self.widget_manager.widgets)
            }
        
        @self.app.post("/widgets/{widget_id}/update")
        async def update_widget(widget_id: str, data: dict):
            """Update widget data"""
            success = await self.widget_manager.update_widget(widget_id, data)
            if success:
                return {"status": "success", "message": f"Widget {widget_id} updated"}
            else:
                raise HTTPException(status_code=404, detail=f"Widget {widget_id} not found")
        
        @self.app.post("/widgets/{widget_id}/trigger")
        async def trigger_widget(widget_id: str, data: dict):
            """Trigger widget action"""
            success = await self.widget_manager.trigger_widget(widget_id, data)
            if success:
                return {"status": "success", "message": f"Widget {widget_id} triggered"}
            else:
                raise HTTPException(status_code=404, detail=f"Widget {widget_id} not found")
        
        @self.app.get("/config")
        async def get_config():
            """Get configuration"""
            return {
                "display": {
                    "width": self.config.get('display.width'),
                    "height": self.config.get('display.height'),
                    "refresh_interval": self.config.get('display.refresh_interval'),
                },
                "widgets": {
                    "update_interval": self.config.get('widgets.update_interval'),
                    "default_widgets": self.config.get('widgets.default_widgets'),
                },
                "bluetooth": {
                    "enabled": self.config.get('bluetooth.enabled'),
                    "device_name": self.config.get('bluetooth.device_name'),
                }
            }
        
        @self.app.post("/config")
        async def update_config(data: dict):
            """Update configuration"""
            try:
                for key, value in data.items():
                    self.config.set(key, value)
                self.config.save()
                return {"status": "success", "message": "Configuration updated"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time updates"""
            await websocket.accept()
            self.connected_websockets.add(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    # Handle websocket messages
                    await websocket.send_json({"echo": data})
            except WebSocketDisconnect:
                self.connected_websockets.remove(websocket)
    
    async def start(self):
        """Start API server"""
        if not self.config.api_enabled:
            logger.info("API server disabled in config")
            return
        
        host = self.config.get('api.host', '0.0.0.0')
        port = self.config.get('api.port', 8000)
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        self.server = uvicorn.Server(config)
        
        logger.info(f"Starting API server on {host}:{port}")
        await self.server.serve()
    
    async def stop(self):
        """Stop API server"""
        if self.server:
            logger.info("Stopping API server...")
            self.server.should_exit = True
            
            # Close all websocket connections
            for ws in self.connected_websockets:
                try:
                    await ws.close()
                except:
                    pass
            
            self.connected_websockets.clear()
    
    async def broadcast_message(self, message: dict):
        """Broadcast message to all connected websockets"""
        for ws in self.connected_websockets:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send websocket message: {e}")
