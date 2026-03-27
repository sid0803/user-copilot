import time
import requests
from typing import List, Dict, Any
from .base import BaseConnector

# URLs containing these strings are treated as placeholders – skip live pings
_PLACEHOLDER_PATTERNS = ("founderproject.com", "localhost", "127.0.0.1", "example.com", "XXX")


class HealthCheckConnector(BaseConnector):
    def __init__(self, endpoints: List[str], timeout: int = 5):
        self.endpoints = endpoints
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "health_check"

    def _is_placeholder(self, url: str) -> bool:
        return any(p in url for p in _PLACEHOLDER_PATTERNS)

    def fetch_data(self) -> List[Dict[str, Any]]:
        results = []
        for url in self.endpoints:
            if self._is_placeholder(url):
                # Skip live ping for placeholder URLs – return mock UP
                results.append({
                    "source": self.name,
                    "url": url,
                    "status": "UP",
                    "content": f"Service at {url} is UP (mock)",
                    "priority": "low",
                    "timestamp": time.time()
                })
                continue
            try:
                response = requests.get(url, timeout=self.timeout)
                status = "UP" if response.status_code < 400 else "DOWN"
                priority = "low" if status == "UP" else "high"
                results.append({
                    "source": self.name,
                    "url": url,
                    "status": status,
                    "content": f"Service at {url} is {status} (HTTP {response.status_code})",
                    "priority": priority,
                    "timestamp": time.time()
                })
            except requests.exceptions.ConnectionError:
                results.append({
                    "source": self.name,
                    "url": url,
                    "status": "DOWN",
                    "content": f"Service at {url} is DOWN — connection refused",
                    "priority": "high",
                    "timestamp": time.time()
                })
            except Exception as e:
                self.handle_error(e)
                results.append({
                    "source": self.name,
                    "url": url,
                    "status": "UNKNOWN",
                    "content": f"Could not reach {url}: {e}",
                    "priority": "low",
                    "timestamp": time.time()
                })
        return results

