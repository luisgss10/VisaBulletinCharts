"""Shared pytest fixtures."""

from datetime import date
import pytest


@pytest.fixture
def sample_rows():
    """Minimal scraper output covering a 'C' and a real date."""
    return [
        {"bulletin_date": date(2024, 1, 1), "final_action": "01AUG22", "filing": "01FEB23"},
        {"bulletin_date": date(2024, 2, 1), "final_action": "C",       "filing": "C"},
        {"bulletin_date": date(2024, 3, 1), "final_action": "08SEP22", "filing": "01FEB23"},
    ]
