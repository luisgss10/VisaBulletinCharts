"""
Visa Bulletin scraper — EB-3 Mexico cutoff date tracker.

Usage
-----
    python main.py
    python main.py --start 01/2016 --end 12/2025 --priority-date 31/05/2023
"""

import argparse
from datetime import date, datetime

import pandas as pd

from visa_bulletin.config   import DEFAULT_START, DEFAULT_END, DEFAULT_PRIORITY_DATE
from visa_bulletin.scraper  import scrape_range
from visa_bulletin.analysis import build_dataframe
from visa_bulletin.plot     import plot, print_summary


def _parse_month(value: str) -> date:
    """Parse 'MM/YYYY' into the first day of that month."""
    month, year = value.split("/")
    return date(int(year), int(month), 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track EB-3 Mexico visa bulletin cutoff dates over time.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--start",
        default=DEFAULT_START.strftime("%m/%Y"),
        metavar="MM/YYYY",
        help="First bulletin month to scrape",
    )
    parser.add_argument(
        "--end",
        default=DEFAULT_END.strftime("%m/%Y"),
        metavar="MM/YYYY",
        help="Last bulletin month to scrape",
    )
    parser.add_argument(
        "--priority-date",
        default=DEFAULT_PRIORITY_DATE,
        metavar="DD/MM/YYYY",
        help="Your EB-3 priority date",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    start         = _parse_month(args.start)
    end           = _parse_month(args.end)
    priority_date = pd.Timestamp(
        datetime.strptime(args.priority_date, "%d/%m/%Y")
    )

    print(f"Scraping bulletins from {start:%B %Y} to {end:%B %Y} …\n")
    rows = scrape_range(start, end)

    if not rows:
        print("No data retrieved — check your network connection and date range.")
        return

    df = build_dataframe(rows)
    print_summary(df, priority_date)
    plot(df, priority_date)


if __name__ == "__main__":
    main()
