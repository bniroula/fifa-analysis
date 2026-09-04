# FIFA Ranking vs. World Cup Outcomes — Steering

## What this project is
An empirical study of whether pre-tournament FIFA rankings predict World Cup match outcomes, and where in the ranking gap that signal disappears.

Full brief and methodology decisions live in `docs/PROJECT.md`. Read that before starting substantive work.

## Locked decisions (do not silently revisit)
- **Match scope:** World Cup tournament matches only. No qualifiers, no friendlies, no confederation tournaments.
- **Draws:** Default counted as a loss for the "bet the higher-ranked team" strategy. Implementation must keep this pluggable — user will explore other treatments (exclude, half-credit) later.
- **Knockout ties:** Winner after extra time or penalties is the winner.
- **Ranking snapshot:** Use the FIFA ranking release immediately preceding tournament kickoff for that year's tournament. Same snapshot applies to every match in that tournament (no mid-tournament re-ranking).
- **Data source:** Kaggle for both matches and rankings. Spot-check a handful of tournament-eve snapshots against FIFA.com before trusting the join.
- **Eras:** Pre-2018 and post-2018 rankings are combined into one dataset. Rationale: the ranking is treated as atomic per-tournament — whatever FIFA published that year is what a bettor would have used. The 2018 methodology change is noted as a caveat, not a split.
- **Ranking fields carried:** Both ranking *position* and ranking *points* are joined onto every match, for both teams. Position drives the default strategy; points enable future gap analyses without a re-import.
- **2026 tournament format:** Combined with prior tournaments in the primary analysis. The 48-team / 104-match format is noted as a caveat.

## Open decisions
None currently — proceed to implementation.

## Repo layout
```
data/raw/         # gitignored — downloaded source data, never edited by hand
data/processed/   # cleaned, joined tables produced by src/ scripts
notebooks/        # exploratory analysis, one .ipynb per question
src/              # reusable Python modules (loaders, joiners, strategy simulator)
tests/            # unit tests for src/
docs/             # project brief, methodology notes, decision log
```

## Working style
- Python + Jupyter for exploration; reusable logic goes in `src/` with tests.
- Raw data is downloaded via a script, never committed. Processed data may be committed if small.
- Every analytical claim in a notebook must be traceable to a cell that produces it — no hand-typed numbers in markdown.
- Don't fabricate or hand-encode historical facts (rankings, results, the 2026 semi-finalists claim). Load them from data.
