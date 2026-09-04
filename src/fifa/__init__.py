"""FIFA Ranking vs. World Cup Outcomes -- analysis package.

v1 increment: results loader only. Rankings, name normalization, snapshot
selection, and the strategy simulator are deferred (see docs/PROJECT.md).
"""

from __future__ import annotations

from fifa import config

__all__ = ["config", "main"]


def main() -> None:
    """Smoke-test entry point: print the in-scope tournaments."""
    print(f"fifa package -- {len(config.TOURNAMENTS)} tournaments in scope:")
    for t in config.TOURNAMENTS:
        hosts = ", ".join(t.hosts)
        print(
            f"  {t.year}: hosts={hosts} | "
            f"{t.total_matches} matches "
            f"({t.group_matches} group + {t.knockout_matches} knockout)"
        )
