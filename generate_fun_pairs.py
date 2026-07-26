#!/usr/bin/env python3
"""
Script to scan all monster matchups, find fun fights (20%-80% win rate range),
and write the deliverable fun_pairs.csv at the repository root.
"""

import csv
import os
from dnd_api import fetch_all_monsters
from battle import find_all_fun_matchups


def generate_fun_pairs_csv(output_file: str = "fun_pairs.csv"):
    print("Fetching monsters...")
    monsters = fetch_all_monsters()
    print(f"Loaded {len(monsters)} monsters.")

    print("Finding all fun matchups...")
    fun_matchups = find_all_fun_matchups(monsters, num_simulations=5000, fast_screen_sims=200)
    print(f"Found {len(fun_matchups)} fun matchups!")

    # Sort fun matchups by balance (closest to 50/50 first)
    fun_matchups.sort(key=lambda m: abs(m["monster1_win_pct"] - 50.0))

    output_path = os.path.abspath(output_file)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["monster1", "monster2", "monster1_win_pct", "monster2_win_pct"])
        for match in fun_matchups:
            writer.writerow([
                match["monster1"],
                match["monster2"],
                f"{match['monster1_win_pct']:.1f}%",
                f"{match['monster2_win_pct']:.1f}%",
            ])

    print(f"Saved {len(fun_matchups)} fun pairs to {output_path}")


if __name__ == "__main__":
    generate_fun_pairs_csv()
