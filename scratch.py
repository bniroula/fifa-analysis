"""Scratch file for debugging ingest functions in the VS Code / Kiro debugger.

How to use:
  1. Open src/fifa/ingest.py and click in the gutter to set a breakpoint inside
     the function you want to inspect (e.g. load_rankings_json).
  2. Open this file, press F5 (or Run > Start Debugging) and pick
     "Python Debugger: Debug scratch.py" if prompted.
  3. Execution pauses at your breakpoint. Inspect variables in the panel on the
     left, step with F10 (over) / F11 (into), continue with F5.

This file is a throwaway harness -- edit the calls below freely. Not imported
by the package or tests.
"""

from __future__ import annotations

from pathlib import Path

from fifa import config
from fifa.ingest import load_rankings_json

# The two World Cups whose rankings come from JSON, not the Kaggle CSV.
JSON_2022 = config.RAW_DIR / "2022-rankings.json"
JSON_2026 = config.RAW_DIR / "2026-rankings.json"


def main() -> None:
    # Call the function under development. Set a breakpoint inside
    # load_rankings_json (in ingest.py) to step through it here.
    df = load_rankings_json(config.FIFA_RANKING_JSON_2022, "2022-10-06")

    # Quick look at the result once it returns something.
    print("returned:", type(df).__name__)
    if df is not None:
        print("shape:", df.shape)
        print("columns:", df.columns.tolist())
        print(df.head(10).to_string())


if __name__ == "__main__":
    main()
