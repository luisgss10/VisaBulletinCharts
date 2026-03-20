"""
Visualises EB-3 Mexico cutoff history and prints a summary
relative to a personal priority date.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot(df: pd.DataFrame, priority_date: pd.Timestamp) -> None:
    """Draw cutoff date history and mark the user's priority date."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df.index, df["final_action"], label="Table A – Final Action",
            linestyle="--", color="green")
    ax.plot(df.index, df["filing"],       label="Table B – Filing Dates",
            linestyle="--", color="blue")
    ax.axhline(y=priority_date, color="red", linestyle=":",
               label=f"My priority date: {priority_date:%d-%b-%Y}")

    last = df.index[-1]
    for series, color in [(df["final_action"], "green"), (df["filing"], "blue")]:
        ax.annotate(
            series.iloc[-1].strftime("%d%b%y"),
            xy=(last, series.iloc[-1]),
            xytext=(8, 0), textcoords="offset points",
            color=color, fontsize=9, va="top",
        )
    ax.annotate(
        priority_date.strftime("%d%b%y"),
        xy=(last, priority_date),
        xytext=(8, 0), textcoords="offset points",
        color="red", fontsize=9, va="top",
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45, ha="right")

    ax.set_title("EB-3 Mexico — Final Action & Filing Dates vs Bulletin Date")
    ax.set_xlabel("Bulletin date")
    ax.set_ylabel("Cutoff date")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.show()


def print_summary(df: pd.DataFrame, priority_date: pd.Timestamp) -> None:
    """Print a text summary of the latest bulletin entry."""
    latest = df.iloc[-1]

    def _fmt(ts):  return ts.strftime("%d-%b-%Y").upper()
    def _mo(days): return abs(int(days / 30.5))

    print()
    print("=" * 60)
    print("Table A – Final Action Dates")
    print("=" * 60)
    print(f"  Latest cutoff : {_fmt(latest['final_action'])}")
    print(f"  Days behind   : {abs(latest['final_delta'])}")
    print(f"  Months behind : {_mo(latest['final_delta'])}")

    print()
    print("=" * 60)
    print("Table B – Filing Dates")
    print("=" * 60)
    print(f"  Latest cutoff : {_fmt(latest['filing'])}")
    print(f"  Days behind   : {abs(latest['filing_delta'])}")
    print(f"  Months behind : {_mo(latest['filing_delta'])}")

    days_to_file = (priority_date - latest["final_action"]).days
    print()
    print("=" * 60)
    print(f"My priority date : {_fmt(priority_date)}")
    print("=" * 60)
    print(f"  Days until Final Action reaches my date  : {days_to_file}")
    print(f"  Months until Final Action reaches my date: {int(days_to_file / 30.5)}")
