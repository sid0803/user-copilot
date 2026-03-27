from typing import List, Dict, Any

class EventProcessor:
    def __init__(self):
        pass

    def process(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize and filter events with enhanced priority scoring."""
        processed_events = []
        
        # Keywords that trigger high priority
        URGENT_KEYWORDS = ["urgent", "broken", "critical", "down", "error", "deadline", "money", "client", "immediate"]
        
        for item in raw_data:
            content = item.get("content", "").lower()
            severity = "INFO"
            
            # 1. Check connector-provided priority
            if item.get("priority") == "high" or item.get("status") == "DOWN":
                severity = "CRITICAL"
                
            # 2. Keyword-based override
            if any(kw in content for kw in URGENT_KEYWORDS):
                severity = "URGENT" if severity != "CRITICAL" else "CRITICAL"
            
            # 3. Connector specific logic
            if item.get("source") == "health_check" and item.get("status") == "DOWN":
                severity = "CRITICAL"

            processed_events.append({
                "source": item.get("source"),
                "content": item.get("content") or f"Status report for {item.get('url', 'unknown')}",
                "severity": severity,
                "timestamp": item.get("timestamp")
            })
        
        # Sort so CRITICAL and URGENT are at the top
        processed_events.sort(key=lambda x: 0 if x['severity'] == "CRITICAL" else 1 if x['severity'] == "URGENT" else 2)
        
        return processed_events
