from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier for this connector."""
        pass

    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch raw data from the external source."""
        pass

    def handle_error(self, error: Exception):
        """Default error handler."""
        print(f"Error in {self.name}: {error}")
