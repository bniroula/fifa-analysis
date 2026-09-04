"""Single source of truth for tournament metadata and data paths.

Everything structural about the analysis universe lives here so the rest of
the codebase never hard-codes years, hosts, or paths inline. See docs/PROJECT.md
and CLAUDE.md for the locked methodology this reflects.

Note on "hand-encoded facts": CLAUDE.md forbids hand-encoding *analytical* facts
(match results, rankings, the 2026 semi-finalist claim) -- those must come from
data. The values below are *structural tournament metadata* (which years are in
scope, who hosted, how many knockout matches each format has). They are required
to even define the analysis and are documented here as a reviewable constant.
Host names use the spelling found in the martj42 results dataset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# --- Paths -----------------------------------------------------------------

# repo_root/src/fifa/config.py -> repo_root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = REPO_ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"

RESULTS_CSV: Path = RAW_DIR / "results.csv"
SHOOTOUTS_CSV: Path = RAW_DIR / "shootouts.csv"
FORMER_NAMES_CSV: Path = RAW_DIR / "former_names.csv"
FIFA_RANKING_CSV: Path = RAW_DIR / "fifa_ranking.csv"
FIFA_RANKING_JSON_2022 = RAW_DIR / "2022-rankings.json"
FIFA_RANKING_JSON_2026 = RAW_DIR / "2026-rankings.json"

# The exact tournament label used in results.csv `tournament` column.
# NOTE: this must be an exact match, not a substring -- "FIFA World Cup
# qualification" rows must be excluded.
WC_TOURNAMENT_LABEL: str = "FIFA World Cup"


# --- Tournaments -----------------------------------------------------------


@dataclass(frozen=True)
class Tournament:
    """Structural metadata for one in-scope World Cup.

    Attributes:
        year: tournament year.
        hosts: host nation(s), spelled as in the results dataset. Co-hosted
            tournaments (2002, 2026) list every host.
        knockout_matches: number of knockout-stage matches for this format.
            Derived from the tournament bracket, not from the data. Used to
            split group vs knockout via the "last N matches by date" rule
            (group stage always finishes before knockout begins -- verified
            for every in-scope tournament).
        total_matches: expected total match count. Used as a data-integrity
            check, not to drive logic.
    """

    year: int
    hosts: tuple[str, ...]
    knockout_matches: int
    total_matches: int

    @property
    def group_matches(self) -> int:
        return self.total_matches - self.knockout_matches


# In scope: first World Cup after FIFA rankings began (Aug 1993) is 1994,
# through 2026. Nine tournaments, ~604 matches total.
#
# Knockout-match counts by format:
#   24 teams (1994):        R16(8)+QF(4)+SF(2)+3rd(1)+F(1)            = 16
#   32 teams (1998-2022):   R16(8)+QF(4)+SF(2)+3rd(1)+F(1)            = 16
#   48 teams (2026):        R32(16)+R16(8)+QF(4)+SF(2)+3rd(1)+F(1)    = 32
TOURNAMENTS: tuple[Tournament, ...] = (
    Tournament(1994, ("United States",), knockout_matches=16, total_matches=52),
    Tournament(1998, ("France",), knockout_matches=16, total_matches=64),
    Tournament(2002, ("South Korea", "Japan"), knockout_matches=16, total_matches=64),
    Tournament(2006, ("Germany",), knockout_matches=16, total_matches=64),
    Tournament(2010, ("South Africa",), knockout_matches=16, total_matches=64),
    Tournament(2014, ("Brazil",), knockout_matches=16, total_matches=64),
    Tournament(2018, ("Russia",), knockout_matches=16, total_matches=64),
    Tournament(2022, ("Qatar",), knockout_matches=16, total_matches=64),
    Tournament(
        2026,
        ("United States", "Canada", "Mexico"),
        knockout_matches=32,
        total_matches=104,
    ),
)

TOURNAMENT_YEARS: tuple[int, ...] = tuple(t.year for t in TOURNAMENTS)

# Fast lookups keyed by year.
BY_YEAR: dict[int, Tournament] = {t.year: t for t in TOURNAMENTS}


def hosts_for(year: int) -> frozenset[str]:
    """Return the set of host nations for a tournament year (empty if unknown)."""
    t = BY_YEAR.get(year)
    return frozenset(t.hosts) if t is not None else frozenset()
