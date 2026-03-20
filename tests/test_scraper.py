"""Tests for the scraper module."""

from datetime import date
from unittest.mock import patch, Mock

import pytest

from visa_bulletin.scraper import _bulletin_url, _iter_months, _parse_eb3_mexico


class TestBulletinUrl:
    def test_regular_month(self):
        url = _bulletin_url(date(2024, 4, 1))
        assert "visa-bulletin-for-april-2024" in url
        assert "/2024/" in url

    def test_october_uses_next_fiscal_year(self):
        url = _bulletin_url(date(2024, 10, 1))
        assert "/2025/" in url

    def test_december_uses_next_fiscal_year(self):
        url = _bulletin_url(date(2023, 12, 1))
        assert "/2024/" in url

    def test_january_stays_same_year(self):
        url = _bulletin_url(date(2024, 1, 1))
        assert "/2024/" in url


class TestIterMonths:
    def test_single_month(self):
        months = list(_iter_months(date(2024, 1, 1), date(2024, 1, 1)))
        assert months == [date(2024, 1, 1)]

    def test_range_count(self):
        months = list(_iter_months(date(2024, 1, 1), date(2024, 3, 1)))
        assert len(months) == 3

    def test_start_after_end_is_empty(self):
        months = list(_iter_months(date(2024, 6, 1), date(2024, 1, 1)))
        assert months == []


class TestParseEb3Mexico:
    def _make_html(self, final_action: str, filing: str | None = None) -> bytes:
        """Build minimal bulletin HTML with one or two EB tables."""
        table = lambda value: f"""
        <table>
          <tr><th>Employment-based</th><th>CHINA</th><th>INDIA</th><th>MEXICO</th><th>ROW</th></tr>
          <tr><td>1st</td><td>C</td><td>C</td><td>C</td><td>C</td></tr>
          <tr><td>2nd</td><td>C</td><td>C</td><td>C</td><td>C</td></tr>
          <tr><td>3rd</td><td>C</td><td>C</td><td>{value}</td><td>C</td></tr>
        </table>"""
        html = table(final_action)
        if filing is not None:
            html += table(filing)
        return html.encode()

    def test_single_table_returns_same_value_for_both(self):
        result = _parse_eb3_mexico(self._make_html("01AUG22"))
        assert result == ("01AUG22", "01AUG22")

    def test_two_tables_assigns_correctly(self):
        result = _parse_eb3_mexico(self._make_html("01AUG22", "01FEB23"))
        assert result == ("01AUG22", "01FEB23")

    def test_current_marker_preserved(self):
        result = _parse_eb3_mexico(self._make_html("C", "C"))
        assert result == ("C", "C")

    def test_no_eb_table_returns_none(self):
        html = b"<table><tr><td>Nothing here</td></tr></table>"
        assert _parse_eb3_mexico(html) is None

    def test_missing_mexico_column_returns_none(self):
        html = b"""
        <table>
          <tr><th>Employment-based</th><th>CHINA</th><th>INDIA</th></tr>
          <tr><td>3rd</td><td>C</td><td>C</td></tr>
        </table>"""
        assert _parse_eb3_mexico(html) is None
