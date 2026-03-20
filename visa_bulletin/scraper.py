"""
Scrapes the US State Department Visa Bulletin pages and extracts
EB-3 Mexico cutoff dates (Final Action + Filing).
"""

from datetime import date

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from visa_bulletin.config import (
    BULLETIN_URL_TEMPLATE,
    BULLETIN_DATE_FMT,
    EB_TABLE_HEADERS,
    TARGET_ROW,
    TARGET_COLUMN,
    CURRENT_MARKER,
    REQUEST_TIMEOUT,
)


def _bulletin_url(bulletin_date: date) -> str:
    """Build the travel.state.gov URL for a given bulletin month."""
    fiscal_year = bulletin_date.year + 1 if bulletin_date.month >= 10 else bulletin_date.year
    return BULLETIN_URL_TEMPLATE.format(
        fiscal_year=fiscal_year,
        month=bulletin_date.strftime("%B").lower(),
        year=bulletin_date.year,
    )


def _iter_months(start: date, end: date):
    """Yield the first day of each month from start to end inclusive."""
    current = start.replace(day=1)
    while current <= end:
        yield current
        current += relativedelta(months=1)


def _parse_eb3_mexico(html: bytes) -> tuple[str, str] | None:
    """
    Return (final_action, filing) strings for EB-3 Mexico from the page HTML.
    Returns None if the table is not found.

    The bulletin contains up to two Employment-Based tables:
      - Table 1: Final Action Dates
      - Table 2: Dates for Filing  (not always present)
    """
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []

    for table in soup.find_all("table"):
        rows = [
            [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            for row in table.find_all("tr")
            if row.find_all(["th", "td"])
        ]
        if not rows or rows[0][0] not in EB_TABLE_HEADERS:
            continue

        header = rows[0]
        # Pad header to match widest data row (some pages have malformed tables)
        max_cols = max(len(r) for r in rows)
        while len(header) < max_cols:
            header.append("")

        try:
            col = header.index(TARGET_COLUMN)
        except ValueError:
            continue

        for row in rows[1:]:
            if row and row[0] == TARGET_ROW and col < len(row):
                found.append(row[col])
                break

    if not found:
        return None

    final_action = found[0]
    filing       = found[1] if len(found) > 1 else found[0]
    return final_action, filing


def scrape_range(start: date, end: date) -> list[dict]:
    """
    Scrape every bulletin from start to end (inclusive).

    Returns a list of dicts:
        {"bulletin_date": date, "final_action": str, "filing": str}

    "C" means Current for that month. Failed pages are skipped with a warning.
    """
    results: list[dict] = []

    for bulletin_date in _iter_months(start, end):
        url  = _bulletin_url(bulletin_date)
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)

        if resp.status_code != 200:
            print(f"  ⚠  {bulletin_date:%Y-%m}  HTTP {resp.status_code} — skipping")
            continue

        parsed = _parse_eb3_mexico(resp.content)
        if parsed is None:
            print(f"  ⚠  {bulletin_date:%Y-%m}  EB-3 Mexico not found — skipping")
            continue

        final_action, filing = parsed
        results.append({
            "bulletin_date": bulletin_date,
            "final_action":  final_action,
            "filing":        filing,
        })
        print(f"  ✓  {bulletin_date:%Y-%m}  final={final_action}  filing={filing}")

    return results
