from typing import List, Dict, Any
import anthropic # Assuming the user will install this

class Summarizer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.feedback_file = "heartbeat/config/feedback.txt"
        self.client = None
        if api_key and api_key != "sk-ant-api03-your-anthropic-key":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("⚠️  'anthropic' library not found. Running in MOCK mode.")

    def _get_founder_preferences(self) -> str:
        """Read founder's specific style preferences from a local file."""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r') as f:
                return f.read().strip()
        return "Keep it short and professional."

    def summarize(self, events: List[Dict[str, Any]], is_daily: bool = False) -> str:
        """Use Claude to generate a professional, non-technical digest."""
        if not events and not is_daily:
            return "🟢 All systems running smoothly. No new updates."

        pref = self._get_founder_preferences()
        
        if is_daily:
            prompt = f"You are a Chief of Staff. Generate a 'BIG PICTURE' Daily Executive Summary for the Founder. " \
                     f"User Preferences: {pref}\n" \
                     f"Summarize the following digests from the last 24 hours into a cohesive story of progress and alerts.\n"
        else:
            prompt = "You are a professional assistant for a non-technical founder. " \
                     f"User Preferences: {pref}\n" \
                     "Summarize the following events into a clear, calm, and decision-oriented digest. " \
                     "Use max 5-7 bullet points. No technical jargon. " \
                     "Format: \n🟢 Status summary\n🔴 Issues\n📌 Recommended Action\n\nEvents:\n"
        
        for event in events:
            if isinstance(event, dict):
                prompt += f"- [{event.get('severity', 'INFO')}] {event.get('source')}: {event.get('content')}\n"
            else:
                prompt += f"- {event}\n"

        # Try real API if client exists
        if self.client:
            try:
                print(f"🧠 Generating {'DAILY' if is_daily else 'QUICK'} summary with Claude (Applying Feedback)...")
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                print(f"⚠️  AI Error: {e}. Falling back to mock summary.")

        # Mock fallback
        if is_daily:
            return "📅 **DAILY EXECUTIVE SUMMARY (MOCK)**\n" \
                   "🟢 **Yesterday's Progress**: The team successfully integrated the new payment flow.\n" \
                   "🟡 **Attention**: One client message remains open from 4pm.\n" \
                   "💪 **Goal for Today**: Finalize beta testing."
        
        return "🟢 All systems checked.\n🔴 One client concern on Slack.\n📌 Action: Check the 'deadline' message."
