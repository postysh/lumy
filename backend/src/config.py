"""Configuration management for Lumy"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
import logging

logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.getenv(
            'LUMY_CONFIG',
            str(Path(__file__).parent.parent / 'config.yaml')
        )
        
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._config = {}
        else:
            logger.warning(f"Config file not found: {config_file}, using defaults")
            self._config = {}
        
        # Merge with defaults
        self._config = {**self._get_defaults(), **self._config}
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'display': {
                'width': 1872,
                'height': 1404,
                'rotation': 0,
                'model': 'epd_7in3e',
                'refresh_interval': 300,  # seconds
                'sleep_after_refresh': True,
            },
            'bluetooth': {
                'enabled': True,
                'device_name': 'Lumy Display',
                'service_uuid': '12345678-1234-5678-1234-56789abcdef0',
                'tx_characteristic_uuid': '12345678-1234-5678-1234-56789abcdef1',
                'rx_characteristic_uuid': '12345678-1234-5678-1234-56789abcdef2',
            },
            'api': {
                'enabled': True,
                'host': '0.0.0.0',
                'port': 8000,
                'cors_origins': ['*'],
            },
            'widgets': {
                'default_widgets': ['clock', 'weather', 'calendar'],
                'update_interval': 60,  # seconds
            },
            'paths': {
                'data': 'data',
                'cache': 'cache',
                'widgets': 'src/widgets/implementations',
                'fonts': 'assets/fonts',
                'images': 'assets/images',
            },
            'logging': {
                'level': 'INFO',
                'file': 'lumy.log',
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
            
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    @property
    def display_width(self) -> int:
        return self.get('display.width')
    
    @property
    def display_height(self) -> int:
        return self.get('display.height')
    
    @property
    def bluetooth_enabled(self) -> bool:
        return self.get('bluetooth.enabled')
    
    @property
    def api_enabled(self) -> bool:
        return self.get('api.enabled')
    
    @property
    def data_dir(self) -> Path:
        return Path(self.get('paths.data'))
    
    @property
    def cache_dir(self) -> Path:
        return Path(self.get('paths.cache'))
