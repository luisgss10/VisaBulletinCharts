"""
Central configuration — defaults and constants.
Override any of these via CLI flags or environment variables.
"""

from datetime import date

# ── Scrape range defaults ─────────────────────────────────────────────────────
DEFAULT_START = date(2023, 1, 1)
DEFAULT_END   = date(2026, 3, 1)

# ── Your priority date ────────────────────────────────────────────────────────
DEFAULT_PRIORITY_DATE = "31/05/2023"   # DD/MM/YYYY

# ── Bulletin URL template ─────────────────────────────────────────────────────
# {fiscal_year}, {month}, {year} are filled in by the scraper
BULLETIN_URL_TEMPLATE = (
    "https://travel.state.gov/content/travel/en/legal/visa-law0/"
    "visa-bulletin/{fiscal_year}/visa-bulletin-for-{month}-{year}.html"
)

# ── Scraper settings ──────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15   # seconds

# ── Table identifiers ─────────────────────────────────────────────────────────
EB_TABLE_HEADERS  = {"Employment-based", "Employment-Based"}
TARGET_ROW        = "3rd"
TARGET_COLUMN     = "MEXICO"
CURRENT_MARKER    = "C"

# ── Date format used in bulletin cells, e.g. "22NOV22" ───────────────────────
BULLETIN_DATE_FMT = "%d%b%y"
