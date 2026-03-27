import os
from .base import BaseNotifier

class MacOSNotifier(BaseNotifier):
    @property
    def name(self) -> str:
        return "macos"

    def send(self, message: str):
        print(f"Delivering notification: {message[:50]}...")
        import platform
        os_name = platform.system()

        # Try plyer if installed
        try:
            from plyer import notification
            notification.notify(
                title="Founder Heartbeat",
                message=message[:200],
                app_name="Heartbeat"
            )
            return
        except Exception:
            pass

        if os_name == "Darwin":
            title = "Founder Heartbeat"
            os.system(f"osascript -e 'display notification \"{message[:100]}\" with title \"{title}\"'")
        elif os_name == "Windows":
            print(f"--- WINDOWS NOTIFICATION --- \n{message}\n---------------------------")
        elif os_name == "Linux":
            os.system(f"notify-send 'Founder Heartbeat' '{message[:100]}'")
        else:
            print(f"Notification: {message}")
