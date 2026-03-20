#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup.sh  —  Bootstrap the visa-bulletin development environment
#
# Usage:
#   bash scripts/setup.sh          # create venv + install deps
#   bash scripts/setup.sh --clean  # delete venv first, then reinstall
# ---------------------------------------------------------------------------
set -euo pipefail

VENV_DIR=".venv"
PYTHON="${PYTHON:-python3}"

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[setup]${NC} $*"; }
warning() { echo -e "${YELLOW}[setup]${NC} $*"; }

# ── --clean flag ──────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--clean" ]]; then
    warning "Removing existing virtual environment …"
    rm -rf "$VENV_DIR"
fi

# ── Python version check ──────────────────────────────────────────────────────
PY_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED="3.11"
if [[ "$(printf '%s\n' "$REQUIRED" "$PY_VERSION" | sort -V | head -1)" != "$REQUIRED" ]]; then
    echo "Error: Python $REQUIRED+ required (found $PY_VERSION)" >&2
    exit 1
fi
info "Python $PY_VERSION detected"

# ── Virtual environment ───────────────────────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating virtual environment in $VENV_DIR …"
    "$PYTHON" -m venv "$VENV_DIR"
else
    info "Virtual environment already exists — skipping creation"
fi

# ── Activate ──────────────────────────────────────────────────────────────────
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# ── Upgrade pip ───────────────────────────────────────────────────────────────
info "Upgrading pip …"
pip install --quiet --upgrade pip

# ── Install project + dev extras ─────────────────────────────────────────────
info "Installing project dependencies …"
pip install --quiet -e ".[dev]"

# ── .env file ─────────────────────────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        info "Creating .env from .env.example …"
        cp .env.example .env
    else
        warning ".env.example not found — skipping .env creation"
    fi
else
    info ".env already exists — skipping"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
info "Setup complete!"
echo ""
echo "  Activate the environment:"
echo "    source $VENV_DIR/bin/activate"
echo ""
echo "  Run the scraper:"
echo "    python main.py"
echo "    python main.py --start 01/2020 --end 12/2024 --priority-date 31/05/2023"
echo ""
echo "  Run tests:"
echo "    pytest"
echo ""
