# Visa Bulletin — EB-3 Mexico tracker

Scrapes the US State Department's monthly Visa Bulletins and plots the
**EB-3 Mexico** Final Action and Filing cutoff dates over time, relative
to a personal priority date.

## Quick start

```bash
git clone <repo-url>
cd visa_bulletin
bash scripts/setup.sh
source .venv/bin/activate
python main.py
```

## Usage

```bash
python main.py
python main.py --start 01/2016 --end 12/2025 --priority-date 31/05/2023
```

| Argument | Format | Default |
|---|---|---|
| `--start` | `MM/YYYY` | `01/2016` |
| `--end` | `MM/YYYY` | `12/2025` |
| `--priority-date` | `DD/MM/YYYY` | `31/05/2023` |

## Development

```bash
# Reinstall from scratch
bash scripts/setup.sh --clean

# Run tests
pytest

# Run tests with coverage
pytest --cov=visa_bulletin
```

## Project layout

```
visa_bulletin/
├── main.py                      # CLI entry point
├── pyproject.toml               # packaging + dependencies
├── .env.example                 # environment variable template
├── .gitignore
├── README.md
│
├── visa_bulletin/               # source package
│   ├── __init__.py
│   ├── __main__.py              # enables: python -m visa_bulletin
│   ├── config.py                # defaults and constants
│   ├── scraper.py               # fetch + parse bulletin pages
│   ├── analysis.py              # build DataFrame, compute deltas
│   └── plot.py                  # chart + text summary
│
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── test_scraper.py
│   └── test_analysis.py
│
└── scripts/
    └── setup.sh                 # one-command environment bootstrap
```

## How it works

1. `scraper.py` — iterates over each month in the requested range, builds
   the State Department URL, fetches the page, and extracts the EB-3 Mexico
   row from the Employment-Based table(s). Returns raw strings like `"01AUG22"`
   or `"C"` (Current).

2. `analysis.py` — resolves `"C"` to the bulletin's own month date, parses
   all dates to `datetime`, and computes how many days each cutoff lags behind
   its bulletin date.

3. `plot.py` — draws the two cutoff lines and a horizontal marker for your
   priority date, then prints a numeric summary.
