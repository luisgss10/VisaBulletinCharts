"""Tests for the analysis module."""

from datetime import date
import pandas as pd
import pytest

from visa_bulletin.analysis import build_dataframe


class TestBuildDataframe:
    def test_shape(self, sample_rows):
        df = build_dataframe(sample_rows)
        assert len(df) == 3
        assert set(df.columns) == {"final_action", "filing", "final_delta", "filing_delta"}

    def test_index_is_datetime(self, sample_rows):
        df = build_dataframe(sample_rows)
        assert pd.api.types.is_datetime64_any_dtype(df.index)

    def test_current_resolved(self, sample_rows):
        """Row with 'C' should be resolved to the bulletin's own month date."""
        df = build_dataframe(sample_rows)
        feb = df.loc["2024-02-01"]
        assert feb["final_action"] == pd.Timestamp("2024-02-01")
        assert feb["filing"]       == pd.Timestamp("2024-02-01")

    def test_real_date_parsed(self, sample_rows):
        df = build_dataframe(sample_rows)
        jan = df.loc["2024-01-01"]
        assert jan["final_action"] == pd.Timestamp("2022-08-01")

    def test_delta_is_non_positive(self, sample_rows):
        """Cutoff dates should never be after the bulletin date."""
        df = build_dataframe(sample_rows)
        assert (df["final_delta"]  <= 0).all()
        assert (df["filing_delta"] <= 0).all()

    def test_delta_value(self, sample_rows):
        df = build_dataframe(sample_rows)
        # 2024-01-01 minus 2022-08-01 = -518 days
        assert df.loc["2024-01-01", "final_delta"] == -518
