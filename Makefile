VENV    := .venv
PYTHON  := python3
PIP     := $(VENV)/bin/pip
PYTEST  := $(VENV)/bin/pytest
RUN     := $(VENV)/bin/python main.py

# ── Default target ────────────────────────────────────────────────────────────
.DEFAULT_GOAL := help

.PHONY: help setup clean test run reinstall

help:
	@echo ""
	@echo "  make setup      Create venv and install all dependencies"
	@echo "  make reinstall  Wipe venv and reinstall from scratch"
	@echo "  make test       Run the test suite"
	@echo "  make coverage   Run tests with coverage report"
	@echo "  make run        Run the scraper with default settings"
	@echo "  make run-custom START=01/2020 END=12/2025 PD=31/05/2023"
	@echo "  make clean      Remove the virtual environment"
	@echo ""

# ── Environment ───────────────────────────────────────────────────────────────
setup:
	@if [ ! -d "$(VENV)" ]; then \
		echo "[make] Creating virtual environment …"; \
		$(PYTHON) -m venv $(VENV); \
	else \
		echo "[make] Virtual environment already exists — skipping creation"; \
	fi
	@echo "[make] Upgrading pip …"
	@$(PIP) install --quiet --upgrade pip
	@echo "[make] Installing project dependencies …"
	@$(PIP) install --quiet -e ".[dev]"
	@echo "[make] Done — environment ready"

reinstall:
	@echo "[make] Wiping existing virtual environment …"
	rm -rf $(VENV)
	$(MAKE) setup

clean:
	@echo "[make] Removing virtual environment …"
	rm -rf $(VENV)

# ── Tests ─────────────────────────────────────────────────────────────────────
test: setup
	$(PYTEST)

coverage: setup
	$(PYTEST) --cov=visa_bulletin --cov-report=term-missing

# ── Run ───────────────────────────────────────────────────────────────────────
run: setup
	$(RUN)

run-custom: setup
	$(RUN) --start $(START) --end $(END) --priority-date $(PD)
