import os
from typing import List, Dict, Any


# ─────────────────────────────────────────────
#  Prompt builder (shared across all providers)
# ─────────────────────────────────────────────
def _build_prompt(events: List[Dict[str, Any]], is_daily: bool, preferences: str) -> str:
    if is_daily:
        prompt = (
            "You are a Chief of Staff. Generate a 'BIG PICTURE' Daily Executive Summary for the Founder.\n"
            f"User Preferences: {preferences}\n"
            "Summarise the following digests from the last 24 hours into a cohesive story of progress and alerts.\n\n"
        )
    else:
        prompt = (
            "You are a professional assistant for a non-technical founder.\n"
            f"User Preferences: {preferences}\n"
            "Summarise the following events into a clear, calm, and decision-oriented digest.\n"
            "Use max 5-7 bullet points. No technical jargon.\n\n"
            "Format exactly like this:\n"
            "🟢 System Status: <one-line overall health>\n"
            "🔴 Critical Items: <bullet list of issues>\n"
            "📌 Recommended Actions: <numbered action list>\n"
            "⏱️ Next Check-in: <when the founder should look again>\n\n"
            "Events:\n"
        )
    for event in events:
        if isinstance(event, dict):
            age = f" | {event['age_hours']}h old" if event.get("age_hours") else ""
            action = f" → {event['suggested_action']}" if event.get("suggested_action") else ""
            prompt += f"- [{event.get('severity','INFO')}] {event.get('source')}: {event.get('content')}{age}{action}\n"
        else:
            prompt += f"- {event}\n"
    return prompt


class Summarizer:
    """
    Multi-provider AI summariser.

    Provider priority (first available key wins):
        1. Google Gemini   (GEMINI_API_KEY)     – free tier, default
        2. Anthropic Claude (ANTHROPIC_API_KEY) – paid, high quality
        3. OpenAI           (OPENAI_API_KEY)    – paid, widely used

    The active provider can be forced via settings.yaml  →  ai.provider: gemini | anthropic | openai
    Falls back to a rich mock digest when no key is available.
    """

    def __init__(self, gemini_key: str = None, anthropic_key: str = None,
                 openai_key: str = None, provider: str = "auto"):
        self.feedback_file = "heartbeat/config/feedback.txt"
        self.provider = provider.lower()  # "auto" | "gemini" | "anthropic" | "openai"

        # Normalise – treat placeholder strings as absent
        self._gemini_key    = gemini_key    if gemini_key    and "your-key" not in gemini_key    else None
        self._anthropic_key = anthropic_key if anthropic_key and "your-key" not in anthropic_key else None
        self._openai_key    = openai_key    if openai_key    and "your-key" not in openai_key    else None

    # ── helpers ──────────────────────────────────────────────────────────────
    def _get_founder_preferences(self) -> str:
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return "Keep it short, professional, and action-focused."

    def _provider_order(self) -> List[str]:
        """Return providers in the order they should be tried."""
        if self.provider == "auto":
            return ["gemini", "anthropic", "openai"]
        # User forced a specific provider → try that first, then fallbacks
        order = [self.provider]
        for p in ["gemini", "anthropic", "openai"]:
            if p not in order:
                order.append(p)
        return order

    # ── per-provider callers ──────────────────────────────────────────────────
    def _call_gemini(self, prompt: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self._gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    def _call_anthropic(self, prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self._anthropic_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self._openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    # ── key lookup ───────────────────────────────────────────────────────────
    def _key_for(self, provider: str):
        return {"gemini": self._gemini_key,
                "anthropic": self._anthropic_key,
                "openai": self._openai_key}.get(provider)

    def _call_provider(self, provider: str, prompt: str) -> str:
        callers = {
            "gemini":    self._call_gemini,
            "anthropic": self._call_anthropic,
            "openai":    self._call_openai,
        }
        return callers[provider](prompt)

    # ── public API ────────────────────────────────────────────────────────────
    def summarize(self, events: List[Dict[str, Any]], is_daily: bool = False) -> str:
        """Generate a digest using the best available AI provider."""
        if not events and not is_daily:
            return "🟢 All systems running smoothly. No new updates."

        pref   = self._get_founder_preferences()
        prompt = _build_prompt(events, is_daily, pref)

        for provider in self._provider_order():
            if not self._key_for(provider):
                continue
            try:
                print(f"🧠 Generating {'DAILY' if is_daily else 'QUICK'} digest with {provider.upper()}...")
                result = self._call_provider(provider, prompt)
                print(f"✅ Digest generated by {provider.upper()}.")
                return result
            except ImportError:
                print(f"⚠️  '{provider}' library not installed. Trying next provider...")
            except Exception as e:
                print(f"⚠️  {provider.upper()} error: {e}. Trying next provider...")

        # ── Rich mock fallback ────────────────────────────────────────────────
        print("ℹ️  No AI keys configured. Using MOCK digest.")
        if is_daily:
            return (
                "📅 **DAILY EXECUTIVE SUMMARY (MOCK)**\n"
                "🟢 System Status: All services operational. 3 connectors active.\n"
                "🔴 Critical Items:\n"
                "   • Client ABC waiting for reply since 12 hrs\n"
                "   • 1 GitHub PR stale for 2 days\n"
                "📌 Recommended Actions:\n"
                "   1. Reply to Client ABC on Slack\n"
                "   2. Review & merge stale PR #42\n"
                "⏱️ Next Check-in: Evening standup"
            )
        return (
            "🟢 System Status: All endpoints UP. 4 events processed.\n"
            "🔴 Critical Items:\n"
            "   • Client: Project deadline concern (Slack — 3h ago)\n"
            "   • Overdue Notion task: Q2 Roadmap review\n"
            "📌 Recommended Actions:\n"
            "   1. Respond to client deadline message within 2 hours\n"
            "   2. Assign Q2 Roadmap task to team lead\n"
            "⏱️ Next Check-in: In 30 minutes"
        )

