# Visa Bulletin — EB-3 Mexico tracker

Scrapes the US State Department's monthly Visa Bulletins and plots the
**EB-3 Mexico** Final Action and Filing cutoff dates over time, relative
to a personal priority date.

Also monitors the State Dept index page for new bulletins and sends an
**email notification** when one appears.

## Quick start

```bash
git clone <repo-url>
cd VisaBulletinCharts
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
| `--start` | `MM/YYYY` | `01/2023` |
| `--end` | `MM/YYYY` | `03/2026` |
| `--priority-date` | `DD/MM/YYYY` | `31/05/2023` |

## Bulletin monitor

`visa_bulletin/monitor.py` checks the "Upcoming Visa Bulletin" section on
the State Dept index page and sends an email when a genuinely new bulletin
appears (ignores "Coming Soon" placeholders).

**Run manually:**

```bash
SMTP_HOST=smtp.gmail.com \
SMTP_PORT=587 \
SMTP_USER=you@gmail.com \
SMTP_PASSWORD="your-app-password" \
NOTIFY_EMAIL=recipient@example.com \
python -m visa_bulletin.monitor
```

**How state is persisted:** the last detected bulletin is saved to
`last_bulletin.json` at the repo root. The GitHub Actions workflow commits
this file back automatically after each new detection.

### GitHub Actions — automated monitoring

The workflow at `.github/workflows/monitor.yml` runs daily at 2 pm PST
and can also be triggered manually from the Actions tab.

**Required repository secrets** (Settings → Secrets and variables → Actions):

| Secret | Description |
|---|---|
| `SMTP_HOST` | SMTP server, e.g. `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port, e.g. `587` |
| `SMTP_USER` | Sender email address |
| `SMTP_PASSWORD` | Gmail App Password (16-char) |
| `NOTIFY_EMAIL` | Recipient email address |

For Gmail, generate an App Password under Google Account → Security →
2-Step Verification → App passwords.

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
VisaBulletinCharts/
├── main.py                      # CLI entry point (chart + summary)
├── pyproject.toml               # packaging + dependencies
├── last_bulletin.json           # persisted state for the monitor
├── README.md
│
├── visa_bulletin/               # source package
│   ├── __init__.py
│   ├── __main__.py              # enables: python -m visa_bulletin
│   ├── config.py                # defaults and constants
│   ├── scraper.py               # fetch + parse bulletin pages (EB-3 Mexico)
│   ├── analysis.py              # build DataFrame, compute deltas
│   ├── plot.py                  # chart + text summary
│   └── monitor.py               # upcoming bulletin monitor + email notifier
│
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── test_scraper.py
│   └── test_analysis.py
│
├── scripts/
│   └── setup.sh                 # one-command environment bootstrap
│
└── .github/
    └── workflows/
        └── monitor.yml          # scheduled GitHub Actions monitor
```

## How it works

### Chart (main.py)

1. `scraper.py` — iterates over each month in the requested range, builds
   the State Department URL, fetches the page, and extracts the EB-3 Mexico
   row from the Employment-Based table(s). Returns raw strings like `"01AUG22"`
   or `"C"` (Current).

2. `analysis.py` — resolves `"C"` to the bulletin's own month date, parses
   all dates to `datetime`, and computes how many days each cutoff lags behind
   its bulletin date.

3. `plot.py` — draws the two cutoff lines and a horizontal marker for your
   priority date, then prints a numeric summary.

### Monitor (monitor.py)

1. Fetches the bulletin index page and locates the "Upcoming Visa Bulletin"
   section.
2. Validates that a real bulletin link is present (URL and title must match
   expected patterns — rejects "Coming Soon" placeholders).
3. Compares the detected bulletin URL against `last_bulletin.json`.
4. If new: sends an SMTP email notification and updates `last_bulletin.json`.
