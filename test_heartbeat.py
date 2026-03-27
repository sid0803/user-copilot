from heartbeat.core.config_manager import Config
from heartbeat.connectors.slack import SlackConnector
from heartbeat.connectors.health import HealthCheckConnector
from heartbeat.core.processor import EventProcessor
from heartbeat.core.summarizer import Summarizer
from heartbeat.delivery.unified_notifier import MacOSNotifier as UnifiedNotifier
from heartbeat.connectors.git_conn import GitConnector
from heartbeat.connectors.file_project import FileProjectConnector
import os

def test_run():
    print("🚀 Starting Founder Heartbeat TEST RUN...")
    
    # 1. Load config (uses default sample)
    config = Config()
    
    # 2. Mocking environment for test
    slack_ids = config.connectors.get("slack", {}).get("channel_ids", ["TEST_CHANNEL"])
    health_urls = config.connectors.get("health", {}).get("endpoints", ["https://test.com"])
    repo_path = config.connectors.get("git", {}).get("repo_path", ".")
    
    slack_conn = SlackConnector(token="mock_token", channel_ids=slack_ids)
    health_conn = HealthCheckConnector(endpoints=health_urls)
    git_conn = GitConnector(repo_path=repo_path)
    file_project_conn = FileProjectConnector(project_path=repo_path)
    
    connectors = [slack_conn, health_conn, git_conn, file_project_conn]

    # 3. Pull data
    print("--- 📥 Pulling Data ---")
    raw_data = []
    for conn in connectors:
        data = conn.fetch_data()
        print(f"[{conn.name}] Fetched {len(data)} items")
        raw_data.extend(data)

    # 4. Process events
    print("--- ⚙️ Processing Events ---")
    processor = EventProcessor()
    processed_events = processor.process(raw_data)
    print(f"Normalized {len(processed_events)} events.")

    # 5. Summarize
    print("--- 🧠 Generating Digest (Claude Mock) ---")
    summarizer = Summarizer(api_key="mock_key")
    digest = summarizer.summarize(processed_events)
    print(f"DIGEST:\n{digest}")

    # 6. Deliver
    print("--- 🔔 Delivering Notification ---")
    notifier = UnifiedNotifier()
    notifier.send(digest)
    
    print("\n✅ Test run complete! If you saw a notification, your system is ready.")

if __name__ == "__main__":
    test_run()
