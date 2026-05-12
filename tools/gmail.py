import os
import base64
import datetime
from email import message_from_bytes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")
CREDS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")


def _get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _decode_body(payload) -> str:
    """Recursively extract plain text from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    if payload.get("mimeType") == "text/html":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        result = _decode_body(part)
        if result:
            return result
    return ""


def fetch_newsletter_emails(label: str = "Newsletters/Tech", date: str | None = None) -> list[dict]:
    """
    Fetch emails from the given Gmail label sent on `date` (YYYY-MM-DD).
    Defaults to yesterday if date is None.
    Returns list of {subject, sender, date, body}.
    """
    if date is None:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date = yesterday.strftime("%Y/%m/%d")
        date_after = date
        next_day = (yesterday + datetime.timedelta(days=1)).strftime("%Y/%m/%d")
        date_before = next_day
    else:
        d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        date_after = d.strftime("%Y/%m/%d")
        date_before = (d + datetime.timedelta(days=1)).strftime("%Y/%m/%d")

    service = _get_service()

    query = f"label:{label.replace('/', '-')} after:{date_after} before:{date_before}"
    result = service.users().messages().list(userId="me", q=query, maxResults=50).execute()
    messages = result.get("messages", [])

    emails = []
    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        body = _decode_body(msg["payload"])

        emails.append({
            "subject": headers.get("Subject", "(no subject)"),
            "sender": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "body": body,
        })

    return emails
