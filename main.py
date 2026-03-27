from heartbeat.core.config_manager import Config
from heartbeat.connectors.slack import SlackConnector
from heartbeat.connectors.health import HealthCheckConnector
from heartbeat.connectors.git_conn import GitConnector
from heartbeat.connectors.file_project import FileProjectConnector
from heartbeat.connectors.gmail_conn import GmailConnector
from heartbeat.connectors.github_conn import GitHubConnector
from heartbeat.connectors.notion_conn import NotionConnector
from heartbeat.core.processor import EventProcessor
from heartbeat.core.summarizer import Summarizer
from heartbeat.delivery.unified_notifier import UnifiedNotifier
from heartbeat.core.scheduler import Scheduler
from heartbeat.db.models import DatabaseManager
import os


def _build_summarizer(config: Config) -> Summarizer:
    """Initialise Summarizer with all available AI keys and the configured provider."""
    ai_cfg   = config.ai
    provider = ai_cfg.get("provider", "auto")  # gemini | anthropic | openai | auto
    return Summarizer(
        gemini_key    = config.get_env("GEMINI_API_KEY"),
        anthropic_key = config.get_env("ANTHROPIC_API_KEY"),
        openai_key    = config.get_env("OPENAI_API_KEY"),
        provider      = provider,
    )


def _build_notifier(config: Config) -> UnifiedNotifier:
    """Initialise UnifiedNotifier from delivery section of settings.yaml."""
    delivery = config.delivery
    return UnifiedNotifier(
        preferred     = delivery.get("preferred", "desktop"),
        slack_webhook = delivery.get("slack_webhook", ""),
        smtp_user     = config.get_env("SMTP_USER", ""),
        smtp_pass     = config.get_env("SMTP_PASS", ""),
        smtp_to       = config.get_env("SMTP_TO", ""),
    )


def run_heartbeat():
    # 1. Load config
    config = Config()

    # 2. Connector config
    project_path = config.connectors.get("git", {}).get("repo_path", ".")

    connectors = [
        SlackConnector(
            token       = config.get_env("SLACK_TOKEN"),
            channel_ids = config.connectors.get("slack", {}).get("channel_ids", []),
        ),
        HealthCheckConnector(
            endpoints = config.connectors.get("health", {}).get("endpoints", []),
        ),
        GitConnector(repo_path=project_path),
        FileProjectConnector(project_path=project_path),
        GmailConnector(),
        GitHubConnector(
            token = config.get_env("GITHUB_TOKEN"),
            repo  = config.connectors.get("github", {}).get("repo", ""),
        ),
        NotionConnector(
            token       = config.get_env("NOTION_TOKEN"),
            database_id = config.connectors.get("notion", {}).get("database_id", ""),
        ),
    ]

    # 3. Pull data
    raw_data = []
    for conn in connectors:
        raw_data.extend(conn.fetch_data())

    # 4. Process events
    processor       = EventProcessor()
    processed_events = processor.process(raw_data)

    # 5. Summarise & Save
    summarizer = _build_summarizer(config)
    digest     = summarizer.summarize(processed_events)
    db         = DatabaseManager()
    db.save_digest(digest)

    # 6. Deliver
    notifier = _build_notifier(config)
    notifier.send(digest)
    print("✅ Heartbeat cycle complete.")


def run_daily_summary():
    print("🌅 Triggering Daily Executive Summary...")
    config = Config()
    db     = DatabaseManager()

    summarizer   = _build_summarizer(config)
    past_digests = db.get_last_24h_digests()
    daily_digest = summarizer.summarize(past_digests, is_daily=True)

    notifier = _build_notifier(config)
    notifier.send(daily_digest)
    print("✅ Daily Executive Summary complete.")


if __name__ == "__main__":
    config    = Config()
    interval  = config.ai.get("interval_minutes", 30)  # reads from timing section too
    scheduler = Scheduler(interval_minutes=interval)
    scheduler.run(run_heartbeat, run_daily_summary)

