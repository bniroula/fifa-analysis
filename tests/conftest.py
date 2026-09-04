"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def results_fixture() -> Path:
    return FIXTURES / "results_sample.csv"


@pytest.fixture
def shootouts_fixture() -> Path:
    return FIXTURES / "shootouts_sample.csv"


@pytest.fixture
def former_names_fixture() -> Path:
    return FIXTURES / "former_names_sample.csv"
