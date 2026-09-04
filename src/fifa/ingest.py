"""Raw CSV loaders for the martj42 international-results dataset.

These functions are the single place that knows where the raw files live and
what their columns are. They parse dates, enforce dtypes, validate the schema,
and fail loudly with an actionable message if a file is missing. Everything
downstream (WC assembly, notebooks) imports from here rather than calling
pandas.read_csv directly.
"""

from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from fifa import config

# Expected columns per raw file. Loaders validate against these so a schema
# drift in a re-download surfaces immediately instead of silently later.
RESULTS_COLUMNS: tuple[str, ...] = (
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
    "city",
    "country",
    "neutral",
)
SHOOTOUTS_COLUMNS: tuple[str, ...] = (
    "date",
    "home_team",
    "away_team",
    "winner",
    "first_shooter",
)
FORMER_NAMES_COLUMNS: tuple[str, ...] = (
    "current",
    "former",
    "start_date",
    "end_date",
)
FIFA_RANKING_COLUMNS: tuple[str, ...] = (
    "rank",
    "country_full",
    "country_abrv",
    "confederation",
    "rank_date",
)


class DataFileMissingError(FileNotFoundError):
    """Raised when a required raw data file is not present."""


def _require(path: Path) -> None:
    if not path.exists():
        raise DataFileMissingError(
            f"Required data file not found: {path}\n"
            f"Expected raw CSVs directly under {config.RAW_DIR}.\n"
            "Download the martj42 'International football results from 1872 to "
            "present' dataset and flatten it into data/raw/, e.g.:\n"
            "  uv run kaggle datasets download -d "
            "martj42/international-football-results-from-1872-to-present "
            "-p data/raw --unzip\n"
            "then move any nested CSVs up into data/raw/."
        )


def _validate_columns(df: pd.DataFrame, expected: tuple[str, ...], source: str) -> None:
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"{source} is missing expected column(s): {missing}. "
            f"Found columns: {list(df.columns)}"
        )


def load_results(path: Path | None = None) -> pd.DataFrame:
    """Load results.csv.

    Returns all international matches (not just World Cup). `date` is parsed to
    datetime; `neutral` is coerced to a real boolean; scores are nullable ints.
    """
    path = path or config.RESULTS_CSV
    _require(path)
    df = pd.read_csv(path, dtype={"home_team": "string", "away_team": "string"})
    _validate_columns(df, RESULTS_COLUMNS, path.name)
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["neutral"] = _to_bool(df["neutral"])
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce").astype("Int64")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce").astype("Int64")
    for col in ("tournament", "city", "country"):
        df[col] = df[col].astype("string")
    return df


def load_shootouts(path: Path | None = None) -> pd.DataFrame:
    """Load shootouts.csv (penalty-shootout winners for tied knockout matches)."""
    path = path or config.SHOOTOUTS_CSV
    _require(path)
    df = pd.read_csv(
        path,
        dtype={
            "home_team": "string",
            "away_team": "string",
            "winner": "string",
            "first_shooter": "string",
        },
    )
    _validate_columns(df, SHOOTOUTS_COLUMNS, path.name)
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    return df


def load_former_names(path: Path | None = None) -> pd.DataFrame:
    """Load former_names.csv (historic country-name lineage with valid date ranges).

    Not used in the v1 results increment, but exposed now because it is the
    backbone of the deferred team-name normalization work.
    """
    path = path or config.FORMER_NAMES_CSV
    _require(path)
    df = pd.read_csv(path, dtype={"current": "string", "former": "string"})
    _validate_columns(df, FORMER_NAMES_COLUMNS, path.name)
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    return df


def load_rankings(path: Path | None = None) -> pd.DataFrame:
    """Load fifa_ranking.csv (weekly FIFA/Coca-Cola World Ranking snapshots).

    Rankings begin Aug 1993. `rank_date` is parsed to datetime; `rank`,
    `previous_points`, and `rank_change` are nullable ints; team names and
    confederation are strings; every points/average column is a float.
    """
    path = config.FIFA_RANKING_CSV
    df = pd.read_csv(
        path,
        dtype={
            "country_full": "string",
            "country_abrv": "string",
            "confederation": "string",
        },
    )
    _validate_columns(df, FIFA_RANKING_COLUMNS, path.name)
    # Keep only the declared columns; the raw file carries extras we don't use.
    df = df[list(FIFA_RANKING_COLUMNS)]
    df["rank_date"] = pd.to_datetime(df["rank_date"], errors="raise")
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    return df


def load_rankings_json(path: Path, date: str) -> pd.DataFrame:
    """ Load rankings for 2022 and 2026 world cup. Datasets for these two world cups
    are missing in the Kaggle dataset.
    """
    rankings = json.load(open(path))
    rankings_df = pd.json_normalize(rankings["Results"])
    rankings_df = pd.DataFrame({
        "rank": rankings_df["Rank"].astype("Int64"),
        "country_full": rankings_df["TeamName"].str[0].str["Description"].astype("string"),
        "country_abrv": rankings_df["IdCountry"].astype("string"),
        "confederation": rankings_df["ConfederationName"].astype("string"),
        "rank_date": pd.Timestamp(date)
    })

    return rankings_df

def _to_bool(series: pd.Series) -> pd.Series:
    """Coerce the results `neutral` column to a clean boolean.

    The raw file stores TRUE/FALSE strings; pandas may read them as strings or
    booleans depending on version, so normalize explicitly.
    """
    if series.dtype == bool:
        return series
    mapping = {
        "TRUE": True,
        "FALSE": False,
        "True": True,
        "False": False,
        "true": True,
        "false": False,
    }
    return series.map(lambda v: mapping.get(str(v).strip(), False)).astype(bool)
