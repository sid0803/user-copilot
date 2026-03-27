# 💓 User Copilot

An intelligent monitoring and summarization tool for **non-technical founders**. Stay informed across your entire business stack — no logs, no dashboards, no Slack marathon.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 The Problem

Founders feel "blind" to project health. **Heartbeat** fixes this by translating technical events into a 2-minute executive digest, delivered every 30 minutes to your desktop, Slack, or email.

---

## 🏗️ 5-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 0 │  Heartbeat Engine           (scheduler + activity)   │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1 │  Data Connectors            Slack · Gmail · GitHub   │
│          │                             Notion · Git · Health     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2 │  Event Engine               Enrich · Score · Dedup   │
│          │                             (type, severity, age)     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3 │  AI Summarizer (your choice)                         │
│          │  ┌──────────┐  ┌───────────┐  ┌─────────┐           │
│          │  │  Gemini  │  │ Anthropic │  │  OpenAI │           │
│          │  │  (free)  │  │  Claude   │  │ GPT-4o  │           │
│          │  └──────────┘  └───────────┘  └─────────┘           │
│          │  → auto mode tries Gemini first, then falls back     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4 │  Delivery Layer             Desktop · Slack · Email  │
└─────────────────────────────────────────────────────────────────┘
                        ↓
          💓 Digest in your preferred channel
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| **7 Connectors** | Slack, Gmail, GitHub, Notion, Git, Health checks, File scan |
| **3 AI Providers** | Gemini (free) · Anthropic Claude · OpenAI GPT-4o — switchable |
| **Smart Triage** | Urgency decay: stale events auto-escalate after 4 hours |
| **3 Delivery Modes** | Desktop notification · Slack webhook · HTML email |
| **Daily 8AM Summary** | Big-picture executive digest of the last 24 hours |
| **Mock Mode** | Works fully without any API keys — great for demos |
| **Feedback Loop** | Edit `heartbeat/config/feedback.txt` to personalise digests |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env — add at least one AI key (Gemini is free!)
```

Get a free Gemini key at → **https://aistudio.google.com/** (no credit card)

### 3. Set your AI provider in `heartbeat/config/settings.yaml`
```yaml
ai:
  provider: "auto"   # auto | gemini | anthropic | openai
```

### 4. Run a test (works without any keys — uses mock data)
```bash
python test_heartbeat.py
```

### 5. Start the monitoring loop
```bash
python main.py
```

---

## 🔌 Connector Setup

| Connector | Needs | How |
|---|---|---|
| **Slack** | `SLACK_TOKEN` | Create Slack App → OAuth & Permissions → `channels:history` |
| **Gmail** | `gmail_credentials.json` | Google Cloud → Gmail API → Download credentials |
| **GitHub** | `GITHUB_TOKEN` | Settings → Developer Settings → Personal Access Tokens |
| **Notion** | `NOTION_TOKEN` + `database_id` | notion.so/my-integrations + share DB with integration |
| **Health** | Endpoint URLs | Add URLs to `settings.yaml → connectors.health.endpoints` |
| **Git / Files** | Local path | Set `settings.yaml → connectors.git.repo_path` |

> All connectors fall back to **rich mock data** when credentials are absent.

---

## 📬 Delivery Modes

Set `delivery.preferred` in `settings.yaml`:

| Value | What happens |
|---|---|
| `desktop` | Cross-platform desktop notification (default) |
| `slack` | Sends digest to your Slack via webhook |
| `email` | HTML email via SMTP (use Gmail App Password) |
| `all` | Sends to all three simultaneously |

---

## 🛡️ Reliability & Security

- **Local First** — all scanning runs on your machine. Nothing leaves without your keys.
- **Activity-Aware** — skips cycles when system idle > 30 min (saves API costs).
- **Graceful Degradation** — every layer has a fallback; the system never crashes silently.

---

## 🗺️ Roadmap

- [x] Cross-platform activity detection
- [x] Full codebase mapping
- [x] Daily 8AM executive summaries
- [x] Multi-provider AI (Gemini / Claude / GPT-4o)
- [x] Gmail, GitHub, Notion connectors
- [x] Email digest delivery
- [ ] Voice command status queries
- [ ] Weekly CEO Performance report

---

**Made for Founders. Built by humans. Powered by AI.**

> 🔗 [github.com/sid0803/user-copilot](https://github.com/sid0803/user-copilot)

