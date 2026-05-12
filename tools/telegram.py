import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def send_telegram_message(text: str) -> dict:
    """
    Send a message to the configured Telegram chat.
    text should be HTML-formatted (parse_mode=HTML).
    Returns {"ok": bool, "description": str}.
    """
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=15,
    )
    data = resp.json()
    if not data.get("ok"):
        return {"ok": False, "description": data.get("description", "Unknown error")}
    return {"ok": True, "description": "Message sent successfully"}
