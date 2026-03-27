import os
import platform
import requests
from .base import BaseNotifier


# ─────────────────────────────────────────────────────────────────────────────
#  Desktop notifier (cross-platform)
# ─────────────────────────────────────────────────────────────────────────────
class DesktopNotifier(BaseNotifier):
    @property
    def name(self) -> str:
        return "desktop"

    def send(self, message: str):
        short = message[:200]
        try:
            from plyer import notification
            notification.notify(
                title="💓 Founder Heartbeat",
                message=short,
                app_name="Heartbeat",
                app_icon=None,
                timeout=10,
            )
            return
        except Exception:
            pass

        os_name = platform.system()
        if os_name == "Darwin":
            safe = short.replace('"', "'")
            os.system(f'osascript -e \'display notification "{safe}" with title "Founder Heartbeat"\'')
        elif os_name == "Windows":
            print(f"\n{'='*60}\n💓 FOUNDER HEARTBEAT\n{'='*60}\n{message}\n{'='*60}\n")
        elif os_name == "Linux":
            safe = short.replace("'", "\\'")
            os.system(f"notify-send 'Founder Heartbeat' '{safe}'")
        else:
            print(f"💓 Heartbeat notification:\n{message}")


# ─────────────────────────────────────────────────────────────────────────────
#  Slack webhook notifier
# ─────────────────────────────────────────────────────────────────────────────
class SlackWebhookNotifier(BaseNotifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    @property
    def name(self) -> str:
        return "slack_webhook"

    def send(self, message: str):
        if not self.webhook_url or "hooks.slack.com/services/XXX" in self.webhook_url:
            print(f"[SlackWebhook] No valid webhook URL configured. Digest:\n{message}")
            return
        try:
            payload = {"text": f"💓 *Founder Heartbeat Digest*\n\n{message}"}
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
            print("✅ Slack webhook notification sent.")
        except Exception as e:
            print(f"⚠️  Slack webhook error: {e}\nDigest:\n{message}")


# ─────────────────────────────────────────────────────────────────────────────
#  Unified router — reads delivery.preferred from settings.yaml
# ─────────────────────────────────────────────────────────────────────────────
class UnifiedNotifier:
    """
    Routes the digest to the correct notifier based on settings.yaml.

    delivery:
      preferred: desktop    # desktop | slack | email | all
      slack_webhook: "https://hooks.slack.com/..."
    """

    def __init__(self, preferred: str = "desktop", slack_webhook: str = "",
                 smtp_user: str = "", smtp_pass: str = "", smtp_to: str = ""):
        self.preferred       = preferred.lower()
        self._desktop        = DesktopNotifier()
        self._slack_webhook  = SlackWebhookNotifier(webhook_url=slack_webhook)

        # Lazy import to avoid hard dependency
        self._smtp_user = smtp_user
        self._smtp_pass = smtp_pass
        self._smtp_to   = smtp_to

    def _email_notifier(self):
        from .email_notifier import EmailNotifier
        return EmailNotifier(smtp_user=self._smtp_user, smtp_pass=self._smtp_pass,
                             smtp_to=self._smtp_to)

    def send(self, message: str):
        if self.preferred == "all":
            self._desktop.send(message)
            self._slack_webhook.send(message)
            self._email_notifier().send(message)
        elif self.preferred == "slack":
            self._slack_webhook.send(message)
        elif self.preferred == "email":
            self._email_notifier().send(message)
        else:  # default: desktop
            self._desktop.send(message)


# Backwards-compatible alias
MacOSNotifier = DesktopNotifier

