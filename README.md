# Shu Han's AI TLDR Bot

A daily AI news digest that reads your newsletter emails, picks the top 5 stories, and sends them to Telegram.

## How it works

1. Fetches yesterday's emails from a Gmail label (`Newsletters/Tech`)
2. Sends them to Claude, which extracts stories and ranks by cross-newsletter frequency
3. Posts a formatted digest to a Telegram chat

If no emails are found (weekends), it sends a short "no digest today" message instead.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Gmail OAuth

- Create a project in [Google Cloud Console](https://console.cloud.google.com)
- Enable the Gmail API and create OAuth credentials
- Download `credentials.json` to the project root
- Run once locally to authenticate — this generates `token.json`:

```bash
python run.py --dry-run
```

### 3. Environment variables

Create a `.env` file:

```
ANTHROPIC_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 4. Gmail label

Emails must be labeled `Newsletters/Tech` in Gmail for the bot to find them.

## Usage

```bash
# Send the real digest
python run.py

# Preview without sending to Telegram
python run.py --dry-run
```

## GitHub Actions

The bot runs daily at 7am PT via `.github/workflows/digest.yml`.

Add these secrets to your repo (**Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat ID |
| `GMAIL_CREDENTIALS_JSON` | Contents of `credentials.json` |
| `GMAIL_TOKEN_JSON` | Contents of `token.json` |

## Project structure

```
run.py          # Entry point
agent.py        # Agentic loop logic
prompts.py      # Prompt templates and tool definitions
tools/
  gmail.py      # Gmail fetching
  telegram.py   # Telegram sending
```
