import requests
from .base import BaseNotifier

class SlackNotifier(BaseNotifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    @property
    def name(self) -> str:
        return "slack"

    def send(self, message: str):
        print(f"Post to Slack: {message[:50]}...")
        if self.webhook_url and "https://hooks.slack.com" in self.webhook_url:
            try:
                payload = {"text": message}
                requests.post(self.webhook_url, json=payload, timeout=10)
            except Exception as e:
                print(f"⚠️  Slack delivery error: {e}")
