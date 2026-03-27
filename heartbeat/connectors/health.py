import requests
from typing import List, Dict, Any
from .base import BaseConnector

class HealthCheckConnector(BaseConnector):
    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints

    @property
    def name(self) -> str:
        return "health_check"

    def fetch_data(self) -> List[Dict[str, Any]]:
        results = []
        for url in self.endpoints:
            try:
                # Mocking status check for MVP
                # response = requests.get(url, timeout=5)
                # status = "UP" if response.status_code == 200 else "DOWN"
                status = "UP" # Mocked
                results.append({
                    "source": "health_check",
                    "url": url,
                    "status": status,
                    "timestamp": 1234567890
                })
            except Exception as e:
                self.handle_error(e)
                results.append({
                    "source": "health_check",
                    "url": url,
                    "status": "DOWN",
                    "error": str(e)
                })
        return results
