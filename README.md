# FIFA Ranking vs. World Cup Outcomes

Do pre-tournament FIFA rankings actually predict who wins World Cup matches — and at what point does a ranking gap stop meaning anything?

This repo is an empirical study of that question. It builds a clean, reproducible dataset of every World Cup match paired with each team's FIFA ranking as of the release right before that tournament, then measures how well "always bet the higher-ranked team" would have done.

## The motivating question

The 2026 World Cup was claimed to be the first tournament where the four highest-ranked teams entering the tournament all reached the semi-finals. If rankings were a strong predictor, that alignment would be unremarkable — so why would it be a first? That tension is the starting point. The 2026 claim is treated as something to verify from data, not a premise.

Three questions drive the analysis:

1. **Baseline strategy** — across every World Cup since FIFA rankings began (1994 onward), if you always picked the higher-ranked team, what fraction of matches would you win?
2. **Semi-finalist alignment** — for each tournament, how many of the four top-ranked teams actually reached the semi-finals? Is 2026 really the first 4-of-4?
3. **Ranking-gap sensitivity** — as you sweep a threshold over the rank gap between two teams, where does betting the favorite stop beating a coin flip? That crossover is the "noise floor" of the ranking signal.

Full brief, locked methodology, and the honest list of complications live in [`docs/PROJECT.md`](docs/PROJECT.md).

## Approach in brief

- **Scope:** World Cup tournament matches only (1994–2026, ~604 matches). No qualifiers, friendlies, or confederation tournaments.
- **Ranking snapshot:** the last FIFA ranking published before each tournament's opening match, reused for every match in that tournament.
- **Winner:** for knockout ties, whoever advances (extra time or penalty shootout) is the winner.
- **Draws:** counted as a loss for the default strategy, but the design keeps this pluggable so other treatments (exclude, half-credit) can be explored.
- **Rankings carried:** both ranking *position* and ranking *points* are joined onto every match, for both teams.

## Data sources

Raw data is downloaded into `data/raw/` and is not hand-edited. The loaders in `src/fifa/ingest.py` are the single place that knows where files live and what their columns are.

- **Matches / shootouts / former names** — Kaggle: martj42, "International football results from 1872 to present". Filtered to `tournament == "FIFA World Cup"`.
- **Rankings 1993–2018** — Kaggle `fifa_ranking.csv` (weekly snapshots).
- **Rankings 2022 & 2026** — FIFA ranking JSON exports (`data/raw/2022-rankings.json`, `2026-rankings.json`), since those tournaments aren't covered by the Kaggle CSV.