# Project Brief: FIFA Ranking vs. World Cup Outcomes

## Motivating observation
The 2026 World Cup is claimed to be the first tournament in which the four highest FIFA-ranked teams entering the tournament all reached the semi-finals. If FIFA rankings were a strong predictor of match outcomes, that alignment would be the expected default, not a first. This project asks: **how predictive are pre-tournament FIFA rankings, actually?**

The claim itself is unverified as of this writing and is the first empirical question the analysis must answer, not a premise.

## Primary questions
1. **Baseline strategy.** Across every World Cup for which FIFA rankings exist, if you always bet on the higher-ranked team in every match (using the ranking release immediately before that tournament), what fraction of matches would you have won?
2. **Semi-finalist alignment.** For each tournament, how many of the four pre-tournament top-ranked teams reached the semi-finals? Is 2026 actually the first 4-of-4?
3. **Ranking-gap sensitivity.** Sweep a threshold `X` over `|rank_A − rank_B|`. For matches where the gap is `≤ X`, treat the pick as a coin flip (50/50). For matches where the gap is `> X`, bet the higher-ranked team. Plot strategy win rate as a function of `X`. Identify:
   - the `X` that maximizes overall win rate,
   - the gap at which "bet higher rank" stops beating a coin flip in the observed data (the noise floor),
   - a confidence band around each point (sample sizes will be small).

## Methodology decisions (locked)
- **Match universe:** World Cup tournament matches only. Group stage + knockouts, all tournaments from the first WC held after FIFA rankings began (August 1993 → first eligible tournament is 1994).
- **Ranking snapshot:** The last FIFA ranking release strictly before each tournament's opening match. One snapshot per tournament, reused for every match in it.
- **Draws:** For the primary "bet higher rank" strategy, draws count as a loss. The strategy simulator must accept a `draw_policy` parameter (`loss` | `exclude` | `half`) so alternatives can be explored without rewriting.
- **Knockout ties:** Match winner is whoever advances (extra-time or penalty-shootout winner counts).
- **"Higher ranked":** Lower rank number = higher rank. Ties on rank number are broken by ranking points; if points are also tied, the match is excluded from the strategy denominator and reported separately.

## Methodology decisions (locked in v1)
- **Data source.** Kaggle for both matches and rankings.
  - Matches: "International football results from 1872 to present" (Mart Jürisoo) — filter to `tournament == "FIFA World Cup"`.
  - Rankings: pick one well-maintained FIFA-rankings dataset on Kaggle and validate against FIFA.com for a handful of tournament-eve snapshots before trusting the join.
  - Both must include ranking *points*, not just position — points are joined onto every match for future gap-in-points analyses.
- **Rankings methodology change (Aug 2018).** Not treated as a regime split. Rankings are treated as atomic per-tournament: whatever FIFA published that year is what a bettor would have used. The methodology change is a documented caveat, and any eventual finding that "rankings are more/less predictive after 2018" is reported as an observation, not baked into the pipeline.
- **2026 tournament format.** Combined with prior tournaments in the primary analysis. The 48-team / 104-match format (vs. 32-team / 64-match for 1998–2022) is a documented caveat. If a signal appears that looks format-driven, we can slice it out later; the pipeline doesn't pre-split it.

## Sample size — set expectations honestly
- Tournaments in scope: **1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026** — nine tournaments.
- Matches per tournament: 52 (1994), 64 (1998–2022, seven tournaments), 104 (2026). Total ≈ **604 matches**.
- Group-stage draw rate in modern WCs is roughly 20–25%. Under the "draws = loss" policy, the theoretical ceiling on the baseline strategy's win rate is well below 100% — closer to ~75–80% even with a perfect ranking predictor.
- For the threshold sweep, each `X` bucket will have far fewer matches. Confidence intervals will overlap for many values of `X`. Any "optimal `X`" claim must come with an interval, not a point estimate.

## Complexity the user should see before we build

### 1. The 2026 claim is unverified
Do not encode it as a premise. First analysis is to check it against data for every tournament in scope.

### 2. FIFA rankings changed methodology in August 2018
The 1994–2018 rankings and the 2022–2026 rankings are computed differently. A "gap of 10" pre-2018 does not mean the same thing as "gap of 10" post-2018. The threshold sweep specifically may need to be run separately on each era, or the rank gap normalized (e.g., by ranking-points gap instead of position gap).

### 3. Ranking position vs. ranking points
Position is ordinal — the gap between #1 and #2 can be tiny or huge in underlying points. A points-based gap analysis is likely more informative than a position-based one, and the codebase should carry both.

### 4. Host bias
World Cup hosts systematically outperform their ranking (France 1998, South Korea 2002, Germany 2006, South Africa 2010, Russia 2018). Under "bet higher rank," host matches against higher-ranked teams are a known adverse subset. Worth reporting host-match performance as its own slice.

### 5. Group vs. knockout stage
Knockouts are pre-filtered — weaker teams are already eliminated, so gaps between remaining teams are smaller and results are noisier. Group-stage matches are where rank-gap variance is largest. Report both slices; the aggregate can mislead.

### 6. Draws suppress the ceiling
With draws counted as losses, the baseline strategy cannot exceed roughly `1 − P(draw)`. If ~22% of matches draw, the ceiling is ~78%. A reported "62% win rate" should be compared to that ceiling, not to 100%.

### 7. Team-name normalization is the boring hard part
"USA" / "United States" / "US"; "South Korea" / "Korea Republic" / "KOR"; "Ivory Coast" / "Côte d'Ivoire"; historic entities (Yugoslavia → Serbia and Montenegro → Serbia; Czechoslovakia → Czech Republic). Joining rankings to matches will fail silently on unnormalized names. Expect this to be ~30–40% of the data-prep work.

### 8. Ranking release cadence
FIFA publishes rankings roughly monthly, but not on a fixed day. "The release immediately before the tournament" needs a defined rule and a per-tournament sanity check that the snapshot date is actually pre-kickoff.

### 9. The "coin flip window" is a modeling choice, not a truth
Treating the small-gap window as 50/50 assumes rankings carry no signal there. The stronger analysis is to *measure* the observed win rate inside the window and see if it's actually distinguishable from 50%. The threshold sweep should report both: "what the strategy would have earned" and "what the ground-truth win rate was" per bucket.

### 10. What "bet" means
This is a match-level bet on a binary outcome, not a bookmaker moneyline. There are no odds and no expected-value calculation — just win rate. If the user later wants EV, they'll need historical odds (a much harder dataset to source).

### 11. Not modeled (call out, don't fake)
Squad injuries, form curves, weather, altitude, travel distance, referee bias, tactical matchups, VAR era effects. If the strategy underperforms the ranking's raw signal, some of this residual is *why*. The project doesn't attempt to explain it — it just measures rankings-vs.-outcomes.

## What "done" looks like for v1
- Reproducible data pipeline: run one script, get `data/processed/wc_matches_with_ranks.parquet` (or equivalent).
- A notebook that answers question 1 (baseline win rate) and question 2 (semi-finalist alignment, including the 2026 claim) with sourced numbers.
- A notebook that produces the threshold-sweep plot for question 3, with confidence intervals and slices for group vs. knockout, host vs. non-host, and pre-2018 vs. post-2018.
- The strategy simulator in `src/` is parameterized on `draw_policy` and `gap_metric` (position vs. points) so alternative framings are a function call away.
