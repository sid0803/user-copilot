from heartbeat.core.config_manager import Config
from heartbeat.connectors.slack import SlackConnector
from heartbeat.connectors.health import HealthCheckConnector
from heartbeat.core.processor import EventProcessor
from heartbeat.core.summarizer import Summarizer
from heartbeat.delivery.unified_notifier import UnifiedNotifier
from heartbeat.core.scheduler import Scheduler
from heartbeat.db.models import DatabaseManager
from heartbeat.connectors.git_conn import GitConnector
from heartbeat.connectors.file_project import FileProjectConnector
import os

def run_heartbeat():
    # 1. Load config
    config = Config()
    
    # 2. Initialize connectors
    project_path = config.connectors.get("git", {}).get("repo_path", ".")
    
    slack_conn = SlackConnector(
        token=config.get_env("SLACK_TOKEN"),
        channel_ids=config.connectors.get("slack", {}).get("channel_ids", [])
    )
    health_conn = HealthCheckConnector(
        endpoints=config.connectors.get("health", {}).get("endpoints", [])
    )
    git_conn = GitConnector(repo_path=project_path)
    file_project_conn = FileProjectConnector(project_path=project_path)
    
    connectors = [slack_conn, health_conn, git_conn, file_project_conn]

    # 3. Pull data
    raw_data = []
    for conn in connectors:
        raw_data.extend(conn.fetch_data())

    # 4. Process events
    processor = EventProcessor()
    processed_events = processor.process(raw_data)

    # 5. Summarize & Save
    summarizer = Summarizer(api_key=config.get_env("ANTHROPIC_API_KEY"))
    digest = summarizer.summarize(processed_events)
    db = DatabaseManager()
    db.save_digest(digest)

    # 6. Deliver
    notifier = UnifiedNotifier()
    notifier.send(digest)
    print("Heartbeat cycle complete.")

def run_daily_summary():
    print("🌅 Triggering Daily Executive Summary...")
    config = Config()
    db = DatabaseManager()
    summarizer = Summarizer(api_key=config.get_env("ANTHROPIC_API_KEY"))
    
    past_digests = db.get_last_24h_digests()
    daily_digest = summarizer.summarize(past_digests, is_daily=True)
    
    notifier = UnifiedNotifier()
    notifier.send(daily_digest)
    print("Daily Executive Summary complete.")

if __name__ == "__main__":
    scheduler = Scheduler(interval_minutes=30)
    scheduler.run(run_heartbeat, run_daily_summary)
