"""Tests for the raw CSV loaders."""

from __future__ import annotations

import pandas as pd
import pytest

from fifa import ingest


def test_load_results_parses_types(results_fixture):
    df = ingest.load_results(results_fixture)
    assert list(df.columns[: len(ingest.RESULTS_COLUMNS)]) == list(ingest.RESULTS_COLUMNS)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["neutral"].dtype == bool
    # TRUE/FALSE strings coerced correctly.
    row_neutral = df.loc[df["home_team"] == "Egypt", "neutral"].iloc[0]
    row_not_neutral = df.loc[df["home_team"] == "Russia", "neutral"].iloc[0]
    assert row_neutral is True or row_neutral == True  # noqa: E712
    assert row_not_neutral == False  # noqa: E712
    # Scores are nullable integers.
    assert str(df["home_score"].dtype) == "Int64"


def test_load_shootouts_parses_dates(shootouts_fixture):
    df = ingest.load_shootouts(shootouts_fixture)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert set(ingest.SHOOTOUTS_COLUMNS).issubset(df.columns)
    assert df.iloc[0]["winner"] == "Russia"


def test_load_former_names_parses_dates(former_names_fixture):
    df = ingest.load_former_names(former_names_fixture)
    assert pd.api.types.is_datetime64_any_dtype(df["start_date"])
    assert "Serbia and Montenegro" in set(df["former"])


def test_missing_file_raises_actionable_error(tmp_path):
    with pytest.raises(ingest.DataFileMissingError) as exc:
        ingest.load_results(tmp_path / "nope.csv")
    assert "data/raw" in str(exc.value)


def test_missing_column_raises_value_error(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("date,home_team\n2018-06-14,Russia\n")
    with pytest.raises(ValueError) as exc:
        ingest.load_results(bad)
    assert "missing expected column" in str(exc.value)
