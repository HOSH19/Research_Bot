import json
import datetime
import anthropic

from prompts import BODY_CHAR_LIMIT, NO_DIGEST_MESSAGE, TASK_PROMPT, TOOL_DEFINITIONS
from tools.gmail import fetch_newsletter_emails
from tools.telegram import send_telegram_message


def _fetch_recent_emails() -> tuple[list, datetime.date]:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    emails = fetch_newsletter_emails(date=yesterday.strftime("%Y-%m-%d"))
    for email in emails:
        if len(email.get("body", "")) > BODY_CHAR_LIMIT:
            email["body"] = email["body"][:BODY_CHAR_LIMIT]
    return emails, yesterday


def _build_prompt(emails: list, date: datetime.date) -> str:
    return TASK_PROMPT.format(
        date=date.strftime("%B %-d, %Y"),
        emails_json=json.dumps(emails, ensure_ascii=False),
    )


def _handle_tool_call(block, dry_run: bool) -> str:
    text = block.input.get("text", "")
    if dry_run:
        print("\n--- DRY RUN: Telegram message ---\n")
        print(text)
        print("\n--- END ---\n")
    else:
        send_telegram_message(**block.input)
    return text


def _run_agentic_loop(client: anthropic.Anthropic, prompt: str, dry_run: bool) -> str:
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return ""

        for block in response.content:
            if block.type == "tool_use":
                return _handle_tool_call(block, dry_run)


def run_agent(dry_run: bool = False) -> str:
    client = anthropic.Anthropic()
    emails, fetch_date = _fetch_recent_emails()

    if not emails:
        if dry_run:
            print("\n--- DRY RUN: Telegram message ---\n")
            print(NO_DIGEST_MESSAGE)
            print("\n--- END ---\n")
            return NO_DIGEST_MESSAGE
        send_telegram_message(text=NO_DIGEST_MESSAGE)
        return NO_DIGEST_MESSAGE

    prompt = _build_prompt(emails, fetch_date)
    return _run_agentic_loop(client, prompt, dry_run)
