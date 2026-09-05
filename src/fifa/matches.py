"""World Cup match assembly.

Turns the raw results + shootouts tables into a clean, analysis-ready World Cup
match table: filtered to the tournament proper, restricted to the in-scope
tournaments (1994-2026), stage-labeled (group vs knockout), with a resolved
winner that honours penalty shootouts for tied knockout matches, and a host-match
flag.

Stage-labeling approach
------------------------
results.csv has no round/stage column, so we split group vs knockout using the
structural fact that in every in-scope World Cup the group stage finishes
entirely before the knockout stage begins (verified: e.g. 2018 group ends
Jun 28, knockout starts Jun 30). Within each tournament we sort matches
chronologically and label the last `knockout_matches` (from config, derived
from the bracket format) as knockout; the rest are group.

Limitations: this relies on (a) the group-before-knockout chronology, which
holds for 1994-2026, and (b) the per-format knockout counts in config being
correct. It is not a general solution for arbitrary tournament formats, and it
would misclassify if a future dataset interleaved group and knockout dates.
A data-integrity check (`check_match_counts`) surfaces any count mismatch.
"""

from __future__ import annotations

import pandas as pd

from fifa import config
from fifa import ingest

# Output column order for the assembled table.
OUTPUT_COLUMNS: tuple[str, ...] = (
    "date",
    "year",
    "stage",
    "team_a",
    "team_b",
    "team_a_score",
    "team_b_score",
    "outcome",
    "winner",
    "decided_by_shootout",
    "is_host_match",
    "city",
    "country",
)

STAGE_GROUP = "group"
STAGE_KNOCKOUT = "knockout"

OUTCOME_TEAM_A = "team_a_win"
OUTCOME_TEAM_B = "team_b_win"
OUTCOME_DRAW = "draw"


def wc_matches(
    results: pd.DataFrame | None = None,
    shootouts: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Assemble the clean in-scope World Cup match table.

    Args:
        results: optional pre-loaded results frame (defaults to ingest.load_results()).
        shootouts: optional pre-loaded shootouts frame (defaults to ingest.load_shootouts()).

    Returns:
        DataFrame with OUTPUT_COLUMNS, sorted by date then teams, one row per
        World Cup match for tournaments 1994-2026.
    """
    if results is None:
        results = ingest.load_results()
    if shootouts is None:
        shootouts = ingest.load_shootouts()

    wc = results[results["tournament"] == config.WC_TOURNAMENT_LABEL].copy()
    wc["year"] = wc["date"].dt.year
    # Restrict to the locked analysis universe (1994-2026).
    wc = wc[wc["year"].isin(config.TOURNAMENT_YEARS)].copy()

    wc = _label_stage(wc)
    wc = _resolve_winner(wc, shootouts)
    wc["is_host_match"] = wc.apply(
        lambda r: (r["team_a"] in config.hosts_for(int(r["year"])))
        or (r["team_b"] in config.hosts_for(int(r["year"]))),
        axis=1,
    )

    wc = wc.sort_values(["date", "team_a", "team_b"]).reset_index(drop=True)
    return wc[list(OUTPUT_COLUMNS)]


def _label_stage(wc: pd.DataFrame) -> pd.DataFrame:
    """Add a `stage` column via the last-N-by-date rule, per tournament."""
    wc = wc.copy()
    wc["stage"] = pd.Series(pd.NA, index=wc.index, dtype="string")
    for year, group in wc.groupby("year"):
        tournament = config.BY_YEAR[int(year)]
        # Stable chronological order; ties broken by teams for determinism.
        ordered = group.sort_values(["date", "team_a", "team_b"]).index
        n_knockout = tournament.knockout_matches
        knockout_idx = ordered[-n_knockout:]
        wc.loc[ordered, "stage"] = STAGE_GROUP
        wc.loc[knockout_idx, "stage"] = STAGE_KNOCKOUT
    return wc


def _resolve_winner(wc: pd.DataFrame, shootouts: pd.DataFrame) -> pd.DataFrame:
    """Add `outcome`, `winner`, and `decided_by_shootout`.

    Decisive matches: winner is the higher-scoring side. Tied matches: if a
    shootout entry exists for (date, team_a, team_b), the shootout winner
    advances and is recorded as the winner (decided_by_shootout=True), and
    `outcome` reflects that advancing side rather than staying `draw`; otherwise
    it is a true draw (winner is NA, outcome is `draw`).
    """
    wc = wc.copy()

    a = wc["team_a_score"]
    b = wc["team_b_score"]
    wc["outcome"] = OUTCOME_DRAW
    wc.loc[a > b, "outcome"] = OUTCOME_TEAM_A
    wc.loc[b > a, "outcome"] = OUTCOME_TEAM_B

    shootout_lookup = shootouts[["date", "team_a", "team_b", "winner"]].rename(
        columns={"winner": "shootout_winner"}
    )
    wc = wc.merge(shootout_lookup, on=["date", "team_a", "team_b"], how="left")

    wc["decided_by_shootout"] = False
    wc["winner"] = pd.Series(pd.NA, index=wc.index, dtype="string")
    wc.loc[wc["outcome"] == OUTCOME_TEAM_A, "winner"] = wc["team_a"]
    wc.loc[wc["outcome"] == OUTCOME_TEAM_B, "winner"] = wc["team_b"]

    tied_with_shootout = (wc["outcome"] == OUTCOME_DRAW) & wc["shootout_winner"].notna()
    wc.loc[tied_with_shootout, "winner"] = wc.loc[tied_with_shootout, "shootout_winner"]
    wc.loc[tied_with_shootout, "decided_by_shootout"] = True
    # Reflect the shootout result in `outcome` too: a tie the higher scorer didn't
    # win outright is decided by who advanced on penalties.
    wc.loc[tied_with_shootout & (wc["shootout_winner"] == wc["team_a"]), "outcome"] = OUTCOME_TEAM_A
    wc.loc[tied_with_shootout & (wc["shootout_winner"] == wc["team_b"]), "outcome"] = OUTCOME_TEAM_B

    return wc.drop(columns=["shootout_winner"])


def check_match_counts(wc: pd.DataFrame | None = None) -> pd.DataFrame:
    """Data-integrity report: actual vs expected match counts per tournament.

    Returns a DataFrame indexed by year with actual/expected totals, the
    group/knockout split, and a boolean `ok` flag. Handy in the notebook and
    tests to catch schema drift or a mis-set knockout count.
    """
    if wc is None:
        wc = wc_matches()
    rows = []
    counts = wc.groupby("year").size()
    stage_counts = wc.groupby(["year", "stage"]).size().unstack(fill_value=0)
    for t in config.TOURNAMENTS:
        actual = int(counts.get(t.year, 0))
        n_group = int(stage_counts.get(STAGE_GROUP, {}).get(t.year, 0)) if STAGE_GROUP in stage_counts else 0
        n_knockout = int(stage_counts.get(STAGE_KNOCKOUT, {}).get(t.year, 0)) if STAGE_KNOCKOUT in stage_counts else 0
        rows.append(
            {
                "year": t.year,
                "actual_total": actual,
                "expected_total": t.total_matches,
                "group": n_group,
                "knockout": n_knockout,
                "expected_knockout": t.knockout_matches,
                "ok": actual == t.total_matches and n_knockout == t.knockout_matches,
            }
        )
    return pd.DataFrame(rows).set_index("year")


def latest_year(wc: pd.DataFrame | None = None) -> int:
    """Return the most recent World Cup year present in the assembled data."""
    if wc is None:
        wc = wc_matches()
    return int(wc["year"].max())
