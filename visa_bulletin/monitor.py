"""
Visa Bulletin Monitor

Checks the "Upcoming Visa Bulletin" section on the State Dept index page.
Sends an email notification when a genuinely new bulletin link appears.

Usage (called by GitHub Actions):
    python -m visa_bulletin.monitor

Required environment variables (set as GitHub Actions secrets):
    SMTP_HOST       — e.g. smtp.gmail.com
    SMTP_PORT       — e.g. 587
    SMTP_USER       — sender Gmail address
    SMTP_PASSWORD   — Gmail App Password
    NOTIFY_EMAIL    — recipient address
"""

from __future__ import annotations

import json
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Constants ─────────────────────────────────────────────────────────────────

INDEX_URL = (
    "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"
)

# Matches: /visa-bulletin/2026/visa-bulletin-for-april-2026.html
BULLETIN_PATH_RE = re.compile(
    r"/visa-bulletin-for-[a-z]+-\d{4}\.html$",
    re.IGNORECASE,
)

# Matches: "April 2026", "January 2025", etc.
BULLETIN_TITLE_RE = re.compile(
    r"^[A-Z][a-z]+ \d{4}$",
)

STATE_FILE = Path(__file__).parent.parent / "last_bulletin.json"

REQUEST_TIMEOUT = 15  # seconds

BASE_URL = "https://travel.state.gov"


# ── Scraping ──────────────────────────────────────────────────────────────────


def _fetch_index() -> bytes:
    resp = requests.get(INDEX_URL, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.content


def _extract_upcoming(html: bytes) -> dict[str, str] | None:
    """
    Parse the index page and return {"title": ..., "url": ...} for the upcoming
    bulletin, or None if the section is absent / shows only a placeholder.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the heading whose text contains "Upcoming Visa Bulletin"
    heading = soup.find(
        lambda tag: tag.name in {"h2", "h3", "h4", "h5", "strong", "b", "p"}
        and "upcoming visa bulletin" in tag.get_text(strip=True).lower(),
    )
    if heading is None:
        return None

    # Search for an <a> tag inside or immediately after the heading's parent block
    container = heading.find_parent(["div", "section", "article", "li", "td"]) or heading
    link = container.find("a", href=BULLETIN_PATH_RE)
    if link is None:
        return None

    # Month and year may be in separate child elements (e.g. <br> between them)
    parts = [s.strip() for s in link.strings if s.strip()]
    title = " ".join(parts)
    if not BULLETIN_TITLE_RE.match(title):
        return None

    href = link["href"]
    if not href.startswith("http"):
        href = BASE_URL + href

    return {"title": title, "url": href}


# ── State persistence ─────────────────────────────────────────────────────────


def _load_last() -> dict[str, str] | None:
    if not STATE_FILE.exists():
        return None
    try:
        data = json.loads(STATE_FILE.read_text())
        if isinstance(data, dict) and "title" in data and "url" in data:
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _save_last(bulletin: dict[str, str]) -> None:
    STATE_FILE.write_text(json.dumps(bulletin, indent=2) + "\n")


# ── Email ─────────────────────────────────────────────────────────────────────


def _send_email(bulletin: dict[str, str]) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    recipient = os.environ["NOTIFY_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = f"New Visa Bulletin Available: {bulletin['title']}"
    msg["From"] = user
    msg["To"] = recipient
    msg.set_content(
        f"A new Visa Bulletin has been posted:\n\n"
        f"  {bulletin['title']}\n"
        f"  {bulletin['url']}\n\n"
        f"Visit the bulletin to check updated priority dates.\n"
    )

    with smtplib.SMTP(host, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)

    print(f"Email sent to {recipient} for bulletin: {bulletin['title']}")


# ── Main ──────────────────────────────────────────────────────────────────────


def check() -> bool:
    """
    Run one check cycle.

    Returns True if a new bulletin was detected (state updated, email sent),
    False otherwise.
    """
    print(f"Fetching {INDEX_URL} …")
    html = _fetch_index()

    upcoming = _extract_upcoming(html)
    if upcoming is None:
        print("No real upcoming bulletin found (placeholder or section absent).")
        return False

    print(f"Upcoming bulletin: {upcoming['title']}  {upcoming['url']}")

    last = _load_last()
    if last is not None and last["url"] == upcoming["url"]:
        print("Already notified for this bulletin — nothing to do.")
        return False

    print("New bulletin detected — sending notification …")
    _send_email(upcoming)
    _save_last(upcoming)
    return True


def main() -> None:
    try:
        new = check()
    except requests.RequestException as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyError as exc:
        print(f"Missing environment variable: {exc}", file=sys.stderr)
        sys.exit(1)

    # Exit code 0 always — CI should not fail just because no new bulletin
    sys.exit(0)


if __name__ == "__main__":
    main()
