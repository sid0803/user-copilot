import yaml
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self, config_path: str = "heartbeat/config/settings.yaml"):
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
        return os.getenv(key, default)
