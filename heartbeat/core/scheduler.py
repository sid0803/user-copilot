import time
import subprocess
from typing import Callable

class Scheduler:
    def __init__(self, interval_minutes: int = 30):
        self.interval_seconds = interval_minutes * 60

    def is_system_active(self) -> bool:
        """Check if the system is active (MacOS and Windows compatible)."""
        import platform
        os_name = platform.system()

        if os_name == "Darwin": # MacOS
            try:
                cmd = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    idle_seconds = float(result.stdout.strip())
                    return idle_seconds < 1800 # 30 minutes
            except Exception:
                pass
        
        elif os_name == "Windows":
            try:
                import ctypes
                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
                
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                idle_seconds = millis / 1000.0
                return idle_seconds < 1800 # 30 minutes
            except Exception:
                pass

        elif os_name == "Linux":
            try:
                # Try xprintidle if on X11
                result = subprocess.run("xprintidle", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    idle_seconds = int(result.stdout.strip()) / 1000.0
                    return idle_seconds < 1800
            except Exception:
                pass

        return True # Fallback for headless or unknown

    def run(self, task: Callable, daily_task: Callable):
        print("Starting Founder Heartbeat Scheduler...")
        last_daily_run = None
        
        while True:
            now = time.localtime()
            
            # 1. Periodic Heartbeat (every 30 mins)
            if self.is_system_active():
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] System active, running heartbeat...")
                task()
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] System inactive, skipping heartbeat.")
            
            # 2. Daily Summary (8:00 AM)
            today_date = time.strftime("%Y-%m-%d")
            if now.tm_hour == 8 and last_daily_run != today_date:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Triggering DAILY EXECUTIVE SUMMARY...")
                daily_task()
                last_daily_run = today_date

            time.sleep(self.interval_seconds)
