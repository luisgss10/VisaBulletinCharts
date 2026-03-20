"""
Turns raw scraped rows into an analysis-ready DataFrame.

Output columns (indexed by bulletin_date):
    final_action    datetime  EB-3 Mexico Final Action cutoff
    filing          datetime  EB-3 Mexico Dates for Filing cutoff
    final_delta     int       Days the cutoff lags behind the bulletin date
    filing_delta    int       Days the cutoff lags behind the bulletin date
"""

from datetime import date

import pandas as pd

from visa_bulletin.config import BULLETIN_DATE_FMT, CURRENT_MARKER


def _resolve_current(value: str, bulletin_date: date) -> str:
    """Replace 'C' (Current) with that month's date string."""
    if value.upper() == CURRENT_MARKER:
        return pd.Timestamp(bulletin_date).strftime(BULLETIN_DATE_FMT).upper()
    return value


def build_dataframe(rows: list[dict]) -> pd.DataFrame:
    """
    Convert scraper output into a tidy DataFrame indexed by bulletin_date.

    Parameters
    ----------
    rows : list[dict]
        Each dict: {"bulletin_date": date, "final_action": str, "filing": str}
    """
    df = pd.DataFrame(rows).set_index("bulletin_date")
    df.index = pd.to_datetime(df.index)

    for col in ("final_action", "filing"):
        df[col] = df.apply(
            lambda row, c=col: _resolve_current(row[c], row.name), axis=1
        )
        df[col] = pd.to_datetime(df[col], format=BULLETIN_DATE_FMT)

    df["final_delta"]  = (df["final_action"] - df.index).dt.days
    df["filing_delta"] = (df["filing"]        - df.index).dt.days

    return df
