BODY_CHAR_LIMIT = 6000

NO_DIGEST_MESSAGE = "📭 No AI digest today — newsletters don't publish on weekends."

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
<b>🤖📰 Shu Han's AI TLDR — {date}</b>

<b>1. [Story headline]</b>
[One sentence summary of what the story is about.]
<a href="[article URL]">Read →</a>

<b>2. ...</b>
...

<i>Curated from [N] unique newsletter sources</i>

Rules:
- Every story MUST include a working article link — do not include a story if you cannot find its URL.
- Keep summaries to one sentence, punchy and informative.
- Do not include newsletter self-promotion, job boards, or sponsor content.
- If fewer than 5 real stories are found, include however many there are.
"""
