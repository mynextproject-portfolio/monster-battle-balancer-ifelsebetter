# Finding Every Fun Matchup — Approach

## Goal

Scan the full D&D 5e monster set, simulate every possible pair, classify each as **fun** (20%–80% underdog win rate) or **boring** (stomp), and produce a ranked list of all fun matchups sorted by closeness to 50/50.

---

## The Scale Problem

The D&D 5e API exposes **~330 monsters**. The number of unique pairs is:

```
C(330, 2) = 330 × 329 / 2 = 54,285 pairs
```

At our current default of **5,000 simulations per pair**, that is:

> **54,285 × 5,000 = ~271 million individual battles**

A single Monte Carlo run of 5,000 sims for one pair takes roughly **0.05–0.15s** in Python (depending on monster complexity / fight length). At ~0.1s per pair:

> **54,285 × 0.1s ≈ 5,429s ≈ 90 minutes**

That is too slow for an interactive run, but feasible as a **batch job** with the right optimizations.

---

## Making It Feasible

### 1. Cache All Monster Data Up-Front

Currently `get_monster_details()` makes an HTTP request per monster. For a full scan:

- Fetch all ~330 monsters **once** at startup and store them as `Monster` objects in memory.
- This turns 54,285 × 2 API calls into just ~330 calls (~30s total).
- Persist the cache to disk (JSON) so subsequent runs skip the network entirely.

### 2. Pre-Filter Obvious Non-Combatants

Not every monster can fight. Monsters with **no attack** (`attack_bonus is None` or `damage_dice is None`) auto-lose against anything that can attack. These pairs are guaranteed stomps.

- Filter these out before simulating — reduces the working set (e.g. ~300 combatants → ~44,850 pairs instead of 54,285).

### 3. Use a Two-Phase Simulation Strategy

Running 5,000 sims per pair for all ~45K pairs is the bottleneck. We can use **adaptive simulation counts**:

**Phase 1 — Quick Screen (200 sims per pair)**
- Run a small number of sims to get a rough win percentage.
- If the underdog's win rate is **below 10% or above 90%**, classify immediately as boring — no need for more sims.
- This eliminates the majority of obvious stomps cheaply.
- Cost: 45,000 × 200 = ~9M sims → ~3–5 minutes.

**Phase 2 — Full Precision (5,000 sims) for Borderline Pairs**
- For pairs where the rough win% falls between 10%–90% (potential fun fights), run the full 5,000 sims to get stable percentages.
- Expected to be ~40–50% of pairs → ~18K–22K pairs × 5,000 = ~100M sims → ~30–40 minutes.

**Total estimated time: ~35–45 minutes** (down from 90).

### 4. Parallelize with multiprocessing

Each pair simulation is fully independent (no shared state). Use Python's `multiprocessing.Pool`:

- On a 4-core machine: **~10–12 minutes total**.
- On an 8-core machine: **~6–8 minutes total**.

The `simulate_battle` function already uses local RNG (no globals), so it is safe for parallel execution.

### 5. Scope the Set (Optional)

If even the optimized run is too slow for iteration, we can scope:

- **By Challenge Rating (CR):** Only pair monsters within ±2 CR of each other. Wildly different CRs almost always produce stomps.
- **By tier:** Group monsters into tiers (CR 0–4, 5–10, 11–16, 17+) and only compare within-tier.
- This can reduce pairs by 60–80% without losing meaningful matchups.

---

## Output Format

The final output will be a **JSON file** (`fun_matchups.json`) at the repo root:

```json
{
  "generated_at": "2026-07-26T12:00:00Z",
  "total_pairs_evaluated": 44850,
  "fun_matchups": [
    {
      "monster1": "Goblin",
      "monster2": "Skeleton",
      "monster1_win_pct": 51.2,
      "monster2_win_pct": 48.8,
      "balance_score": 2.4
    }
  ],
  "stomp_count": 27800,
  "fun_count": 17050
}
```

- **`fun_matchups`**: Sorted by `balance_score` (distance from 50/50), lowest first.
- **`balance_score`**: `abs(monster1_win_pct - 50)` — lower = more balanced = more fun.

---

## Implementation Outline

| Step | What | Where |
|------|-------|-------|
| 1 | Build a `fetch_all_monsters()` function that caches to disk | `dnd_api.py` |
| 2 | Build `find_all_fun_matchups()` with two-phase simulation | `battle.py` |
| 3 | Add `multiprocessing` parallelization | `battle.py` |
| 4 | Create a CLI script `scan_matchups.py` that runs the scan and writes JSON | repo root |
| 5 | Add progress output (pairs evaluated, estimated time remaining) | `scan_matchups.py` |
| 6 | Tests for the scan logic (using small monster sets) | `tests/test_battle.py` |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limiting during bulk fetch | Cache to disk; only fetch once |
| Some monsters have unusual mechanics not modeled (spells, multi-attack) | Accept current simulation model; note limitations in output |
| Phase 1 screen at 200 sims could mis-classify borderline pairs | Use 10%/90% as wide safety margin — real threshold is 20%/80% |
| Long total runtime blocks development | Run as background batch job; parallelize |

---

## Summary

The naive approach (54K pairs × 5K sims each) takes ~90 minutes. By **caching monster data, pre-filtering non-combatants, using two-phase adaptive simulation, and parallelizing**, we can bring this down to **~10 minutes on a 4-core machine** while still producing stable, trustworthy win percentages for every meaningful matchup.
