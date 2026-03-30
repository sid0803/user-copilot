import yaml
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Project root is two levels up from this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Config:
    def __init__(self, config_dict: Dict = None, config_path: str = None):
        if config_dict:
            self._config = config_dict
        else:
            if config_path is None:
                config_path = os.path.join(PROJECT_ROOT, "heartbeat_app", "config", "settings.yaml")
            
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)

    @property
    def connectors(self) -> Dict:
        return self._config.get("connectors", {})

    @property
    def delivery(self) -> Dict:
        return self._config.get("delivery", {})

    @property
    def ai(self) -> Dict:
        return self._config.get("ai", {})

    def get_env(self, key: str, default: str = None) -> str:
        # In SaaS, we prioritize config_dict (per-user) over environment variables
        if key in self._config:
            return self._config[key]
        return os.getenv(key, default)
