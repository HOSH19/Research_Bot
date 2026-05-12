import json
import datetime
import anthropic

from tools.gmail import fetch_newsletter_emails
from tools.telegram import send_telegram_message

TOOL_DEFINITIONS = [
    {
        "name": "send_telegram_message",
        "description": (
            "Send the final digest message to Telegram. "
            "Use HTML formatting: <b>bold</b>, <a href='URL'>link text</a>. "
            "Call this exactly once after you have selected and formatted the top 5 stories."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "HTML-formatted message to send.",
                }
            },
            "required": ["text"],
        },
    },
]

TASK_PROMPT = """\
You are a research assistant that curates a daily AI news digest.

Below are all newsletter emails from {date}:

{emails_json}

Your job:
1. Read through every email body and extract every article/story mentioned — capture the headline and its URL. \
Prefer the canonical article URL over newsletter tracking/redirect URLs when you can identify it.
2. Count how many different newsletters mention the same story (cross-mention score).
3. Pick the TOP 5 stories, balancing:
   - Cross-mention frequency (mentioned in more newsletters = higher signal)
   - Overall importance and novelty to the AI/ML field
4. Call send_telegram_message with ONE formatted message.

Message format (use HTML):
<b>🗞 AI Digest — {date}</b>

<b>1. [Story headline]</b>
[One sentence summary of what the story is about.]
<a href="[article URL]">Read →</a>

<b>2. ...</b>
...

<i>Curated from [N] newsletters</i>

Rules:
- Every story MUST include a working article link — do not include a story if you cannot find its URL.
- Keep summaries to one sentence, punchy and informative.
- Do not include newsletter self-promotion, job boards, or sponsor content.
- If fewer than 5 real stories are found, include however many there are.
"""


def _fetch_recent_emails() -> tuple[list, datetime.date]:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    emails = fetch_newsletter_emails(date=yesterday.strftime("%Y-%m-%d"))
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
            model="claude-sonnet-4-6",
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


NO_DIGEST_MESSAGE = (
    "📭 No AI digest today — newsletters don't publish on weekends."
)


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
