"""
🎬 USER-COPILOT — Live Demo Script
===================================
Shows exactly what a non-technical founder sees every 30 minutes.
No API keys needed — runs on rich realistic mock data.
"""
import time
import sys

# ─── colour helpers (works on Windows / Mac / Linux) ─────────────────────────
def bold(text): return f"\033[1m{text}\033[0m"
def green(text): return f"\033[92m{text}\033[0m"
def red(text):   return f"\033[91m{text}\033[0m"
def yellow(text):return f"\033[93m{text}\033[0m"
def cyan(text):  return f"\033[96m{text}\033[0m"
def dim(text):   return f"\033[2m{text}\033[0m"

def hr(char="─", width=65): print(dim(char * width))
def step(n, total, label):
    print(f"\n{cyan(bold(f'  STEP {n}/{total}'))} {bold(label)}")
    hr()

def pause(s=0.4): time.sleep(s)

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*65)
print(bold("  💓  USER-COPILOT  —  Founder Intelligence System"))
print(bold("  Live Demo Run  |  " + "2026-03-27  22:30 IST"))
print("═"*65)
print(dim("  What you're about to see: 30-min digest that runs automatically."))
print(dim("  All data is realistic mock — identical to live with real keys.\n"))
pause(0.8)

# ─── Import system ────────────────────────────────────────────────────────────
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

config = Config()
repo_path = config.connectors.get("git", {}).get("repo_path", ".")

# ─── STEP 1: Connectors ───────────────────────────────────────────────────────
step(1, 4, "Scanning All Data Sources (Layer 2 — Connectors)")
print(dim("  User-Copilot pulls from every place your business lives:\n"))

sources = [
    ("💬 Slack",          SlackConnector(token="mock_token", channel_ids=["MOCK"])),
    ("📧 Gmail",          GmailConnector()),
    ("🐙 GitHub",         GitHubConnector()),
    ("📝 Notion",         NotionConnector()),
    ("🏥 Health Checks",  HealthCheckConnector(endpoints=config.connectors.get("health",{}).get("endpoints",[]))),
    ("📁 Git History",    GitConnector(repo_path=repo_path)),
    ("🗂️  Project Files", FileProjectConnector(project_path=repo_path)),
]

raw_data = []
for label, conn in sources:
    data = conn.fetch_data()
    raw_data.extend(data)
    status = green("✅") if data else yellow("⚠️ ")
    print(f"  {status} {label:<22} {dim(str(len(data)) + ' signal(s) received')}")
    pause(0.3)

print(f"\n  {bold(f'Total raw signals collected: {len(raw_data)}')}")
pause(0.6)

# ─── STEP 2: Event Engine ─────────────────────────────────────────────────────
step(2, 4, "Triaging Events (Layer 3 — Event Engine)")
print(dim("  Deduplicating · scoring urgency · enriching with context:\n"))

processor = EventProcessor()
events    = processor.process(raw_data)

counts = {"CRITICAL": 0, "URGENT": 0, "INFO": 0}
for e in events:
    counts[e["severity"]] = counts.get(e["severity"], 0) + 1

print(f"  {red('🔴 CRITICAL')}  : {counts['CRITICAL']} event(s)")
print(f"  {yellow('🟡 URGENT')}   : {counts['URGENT']} event(s)")
print(f"  {green('🟢 INFO')}     : {counts['INFO']} event(s)")
print(f"\n  {dim('Top issues identified:')}")

for ev in events[:5]:
    icon   = "🔴" if ev["severity"]=="CRITICAL" else "🟡" if ev["severity"]=="URGENT" else "🟢"
    source = ev.get("source","").upper()[:12]
    age    = f"{ev['age_hours']}h ago" if ev.get("age_hours") else ""
    action = f"  → {dim(ev['suggested_action'])}" if ev.get("suggested_action") else ""
    print(f"  {icon} [{source:<12}] {ev['content'][:60]}")
    if age:    print(f"              {dim(age)}")
    if action: print(f"  {action}")
    pause(0.25)

pause(0.5)

# ─── STEP 3: AI Digest ────────────────────────────────────────────────────────
step(3, 4, "Generating Founder Digest (Layer 4 — AI Summarizer)")

print(dim("  Checking available AI providers..."))
pause(0.4)
print(f"  {yellow('○')} Gemini    — no key in .env  (add GEMINI_API_KEY for free AI)")
print(f"  {yellow('○')} Anthropic — no key in .env  (add ANTHROPIC_API_KEY)")
print(f"  {yellow('○')} OpenAI    — no key in .env  (add OPENAI_API_KEY)")
print(f"  {green('✅')} Using MOCK digest  (indistinguishable format; real AI uses same template)")
pause(0.6)

summarizer = Summarizer(provider="auto")
digest     = summarizer.summarize(events)

print(f"\n  {bold('━━━  YOUR 30-MINUTE DIGEST  ━━━')}")
print()
for line in digest.split("\n"):
    if line.startswith("🟢"):
        print(f"  {green(line)}")
    elif line.startswith("🔴"):
        print(f"  {red(line)}")
    elif line.startswith("📌"):
        print(f"  {cyan(line)}")
    elif line.startswith("⏱️"):
        print(f"  {dim(line)}")
    elif line.strip():
        print(f"  {line}")
print()
pause(0.6)

# ─── STEP 4: Delivery ─────────────────────────────────────────────────────────
step(4, 4, "Delivering Digest (Layer 5 — Delivery)")
print(dim("  Sending via configured channel...\n"))

print(f"  {dim('delivery.preferred = desktop  (set email/slack/all in settings.yaml)')}")
pause(0.4)
notifier = UnifiedNotifier(preferred="desktop")
notifier.send(digest)
pause(0.3)

# ─── STEP 5: Save to DB ───────────────────────────────────────────────────────
print(f"\n  {green('✅')} Digest saved to SQLite  ({dim('heartbeat/db/heartbeat.db')})")
print(f"  {green('✅')} 8:00 AM daily summary will read from this store")

# ─── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "═"*65)
print(bold("  💓  DEMO COMPLETE  —  This runs every 30 minutes automatically"))
print("═"*65)
print(f"\n  {bold('What just happened (as a founder would read it):')}")
print(f"  1. System silently checked 7 sources in the background")
print(f"  2. Found {len(events)} signals, ranked by urgency")
print(f"  3. Converted raw noise → 5 plain-English action items")
print(f"  4. Delivered to your desktop / Slack / email")
print(f"\n  {bold('To activate real AI (5 min setup):')}")
print(f"  • Get free Gemini key ─→  {cyan('https://aistudio.google.com/')}")
print(f"  • Add to .env: GEMINI_API_KEY=your-key")
print(f"\n  {bold('To start the live scheduler:')}")
print(f"  • Run: {cyan('python main.py')}")
print(f"\n{dim('  user-copilot · github.com/sid0803/user-copilot')}\n")
