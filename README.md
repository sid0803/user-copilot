# 💓 Heartbeat: Your Universal Personal Intelligence System

![Hero Header](assets/dashboard.png)

> **"Turn the Digital Noise of Every User into Human Clarity."**
> 
> Heartbeat is a modular, AI-driven decision engine designed to act as your **Personal Chief of Staff**. It scans your emails, messages, tasks, and system logs to deliver a clear, actionable executive brief every 30 minutes.

---

## 🌟 The Vision: Intelligence for Everyone

In a world where we are overwhelmed by notifications from Slack, Gmail, Notion, and GitHub, **Heartbeat** is the filter. Whether you are a **Founder**, a **Remote Engineer**, a **Freelance Designer**, or a **Busy Student**, Heartbeat connects the dots across your digital life so you can focus on what actually matters.

### 🎯 Core Philosophy
- **Noise Reduction:** If it's not urgent, it doesn't interrupt you.
- **Deep Context:** Cross-referencing signals (e.g., a GitHub bug + a Gmail complaint).
- **Local First:** Your data belongs to you. Processing happens on your machine.

---

## 🏗️ 6-Layer Intelligence Architecture

Heartbeat follows a strict "Pipeline" approach to data. Each layer refines the information until it becomes a simple human decision.

![Architecture Diagram](assets/architecture.png)

### 1. 🔍 Layer 1: Scanners (Connectors)
Pluggable tools that "watch" your accounts.
- **💬 Slack:** Monitors DMs and specific channels for urgent mentions.
- **📧 Gmail:** Scans for keywords related to client risks, invoices, or deadlines.
- **🐙 GitHub:** Watches for PR stale-ness, critical issues, and commit activity.
- **📝 Notion:** Tracks overdue tasks and project roadmap changes.
- **🏥 Logs/Health:** Pings endpoints to ensure your infrastructure is 100% UP.

### 2. 🧹 Layer 2: Event Engine (Normalization)
Converts raw data from 7+ sources into a standard "Event" format. It deduplicates alerts—so if an error shows up in your logs and on Slack, you only see it once.

### 3. 🧠 Layer 3: The Brain (Classifier)
Uses business-level rules to calculate a **Priority Score (0-10)**.
- **Rule Engine:** Detects revenue risks, client follow-ups, and blockers.
- **Multi-Source Thinking:** If the same topic appears across Slack AND Email, the system escalates the priority to `CRITICAL`.

### 4. 📝 Layer 4: AI Summarizer (The COO)
Leverages high-performance LLMs (Gemini 1.5 Flash, Claude 3, or GPT-4o) to write a human-readable 60-second brief. It converts technical signals into business decisions.

### 5. 📂 Layer 5: Persistence (Vault)
Stores every signal and digest in a local SQLite database. This allows for **Daily Executive Summaries** that recap your last 24 hours of activity.

### 6. 🔔 Layer 6: Delivery (Routing)
Routes the final brief to your preferred endpoint:
- **Chrome Extension (Popup)**
- **Web Dashboard**
- **Desktop Notifications**
- **Slack Webhooks / HTML Email**

---

## 🧩 Matrix of Supported Connectors

| Connector | Type | Primary Benefit |
| :--- | :--- | :--- |
| **Slack** | Communication | Detects "at risk" client conversations or team blockers. |
| **Gmail** | Communication | Surfaces urgent follow-ups and revenue-related threads. |
| **GitHub** | Development | Flags stale PRs, critical issues, and infra failures. |
| **Notion** | Operations | Reminds you of overdue tasks and changing priorities. |
| **Health Check** | Monitoring | Instant alerts if your website or API goes DOWN. |
| **Git/File** | Local | Tracks activity in your local codebase or project folders. |

---

## 🛠️ Developer Technical Manual

### 🗄️ Database Schema (SQLite)
Heartbeat uses a multi-tenant SQLite database to maintain privacy and performance.

```sql
-- Core User Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT,
    preferences TEXT
);

-- Connector Configurations (Encrypted JSON)
CREATE TABLE connector_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    connector_type TEXT, -- 'slack', 'gmail', etc.
    config_json TEXT,    -- API keys/tokens
    is_active INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Executive Digests
CREATE TABLE digests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    content TEXT,        -- The 🔴/🟡/✅ summary
    source_type TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### 🛣️ API Reference (FastAPI)
The backend exposes a clean REST API for extensions and dashboards.

- `POST /register`: Create a new local user and seed mock data.
- `POST /token`: Authenticate and receive a Bearer token.
- `GET /digests`: Fetch the latest 50 intelligence briefs.
- `POST /heartbeat/trigger`: Manually trigger a 6-layer scan.

### 🧠 Classifier Logic (Scoring)
The "Brain" (`classifier.py`) calculates severity based on these tunable weights:
- **Keywords (Crash/Failure/Down):** +3.0 Score
- **Keywords (Delay/Overdue):** +2.0 Score
- **Multi-Source Intensity:** Escalates to `CRITICAL` instantly.
- **Age (>24h):** +1.0 Score

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.9+
- Node.js 18+ (for Dashboard/Extension)
- API Keys (Gemini, Slack, GitHub, etc. — configurable in `.env`)

### 2. Backend Setup
```bash
# Clone the repo
git clone https://github.com/sid0803/heartbeat-system
cd heartbeat-system

# Install dependencies
pip install -r requirements.txt

# Run the server
python server/main.py
```

### 3. Dashboard & Extension Setup
```bash
cd dashboard
npm install
npm run build
```

### 4. Loading the Chrome Extension
1. Open Chrome and navigate to `chrome://extensions`.
2. Toggle **Developer mode** (top right).
3. Click **Load unpacked** and select the `heartbeat-system/dashboard/dist` folder.
4. Pin the **Heartbeat** icon to your toolbar.

---

## 🔒 Privacy & Security

**Your Data, Your Machine.** 
- **Local First:** The SQLite database and all API scanning logic run locally.
- **AI Choice:** You can configure the system to use Gemini (Free Tier), Claude, or OpenAI.
- **Credential Storage:** API tokens are stored in your local `.env` and SQLite database, never uploaded to a third-party server.

---

## 🗺️ Shared Roadmap
- [ ] **Discord Connector:** Monitor community sentiment.
- [ ] **Telegram Integration:** Delivery layer for mobile notifications.
- [ ] **Jira/Linear Support:** Deeper project management intelligence.
- [ ] **Voice Briefing:** Audio summary of your day via ElevenLabs.

---

## ❓ FAQ & Troubleshooting

**Q: Why is my dashboard empty?**
A: You need to trigger the first scan! Either run `python heartbeat.py` or click the "Trigger Loop" button in the extension/dashboard.

**Q: Does this cost anything?**
A: Heartbeat is open-source. Using the Gemini Free Tier or local models (Ollama) makes the intelligence engine completely free.

**Q: Can I add my own connector?**
A: Yes! Simply subclass `BaseConnector` in `heartbeat_app/connectors/base.py` and implement the `fetch_data` method.

---

🔗 [github.com/sid0803/heartbeat-system](https://github.com/sid0803/heartbeat-system) · **Intelligence for Everyone. Built by AI.**
