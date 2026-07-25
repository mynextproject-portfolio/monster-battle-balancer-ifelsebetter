"""
Battle simulator for D&D monster fights.

Rules:
- Monsters take turns attacking (monster1 goes first).
- Each turn: roll 1d20 + attack_bonus vs target's AC. Hit → roll damage dice.
- First monster to 0 HP loses.
- If a monster has no attack, it can't deal damage — opponent wins immediately.
- If neither can attack, the monster with more HP wins (monster1 as tiebreaker).
- Max 100 rounds to guarantee termination.  If reached, higher remaining HP wins.
"""

import random
import re
from typing import Optional, Tuple

from models.monster import Monster

# Hard cap on rounds so a fight always terminates.
MAX_ROUNDS = 100


def parse_damage_dice(damage_dice: str) -> Tuple[int, int, int]:
    """Parse a damage string like '1d6+2' into (num_dice, die_size, bonus).

    Supports formats: '1d6+2', '2d8', '1d10-1', '1d6'
    Returns (num_dice, die_size, bonus).

    Raises:
        ValueError: If the string doesn't match the expected pattern.
    """
    match = re.match(r"^(\d+)d(\d+)([+-]\d+)?$", damage_dice.strip())
    if not match:
        raise ValueError(f"Cannot parse damage dice: '{damage_dice}'")

    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    bonus = int(match.group(3)) if match.group(3) else 0
    return num_dice, die_size, bonus


def roll_damage(damage_dice: str, rng: random.Random) -> int:
    """Roll damage from a dice string (e.g. '1d6+2') using the given RNG.

    Returns at least 1 damage on any successful hit (floor of 1).
    """
    num_dice, die_size, bonus = parse_damage_dice(damage_dice)
    total = sum(rng.randint(1, die_size) for _ in range(num_dice)) + bonus
    return max(1, total)  # Minimum 1 damage on a hit


def simulate_battle(
    monster1: Monster, monster2: Monster, seed: Optional[int] = None
) -> Monster:
    """Simulate a single fight between two monsters and return the winner.

    Uses local HP copies — the Monster objects are never mutated.
    A seeded RNG makes every fight reproducible: same seed → same outcome.

    Args:
        monster1: First combatant (attacks first each round).
        monster2: Second combatant.
        seed: Optional RNG seed for reproducibility.

    Returns:
        The winning Monster object.
    """
    rng = random.Random(seed)

    m1_can_attack = monster1.attack_bonus is not None and monster1.damage_dice is not None
    m2_can_attack = monster2.attack_bonus is not None and monster2.damage_dice is not None

    # Short-circuit: if a monster can't attack, it can never win.
    if not m1_can_attack and not m2_can_attack:
        # Neither can fight — higher HP wins, monster1 as tiebreaker.
        return monster1 if monster1.hp >= monster2.hp else monster2
    if not m1_can_attack:
        return monster2
    if not m2_can_attack:
        return monster1

    # Local HP copies — never mutate the original Monster objects.
    m1_hp = monster1.hp
    m2_hp = monster2.hp

    for _ in range(MAX_ROUNDS):
        # Monster 1 attacks Monster 2
        attack_roll = rng.randint(1, 20) + monster1.attack_bonus
        if attack_roll >= monster2.ac:
            m2_hp -= roll_damage(monster1.damage_dice, rng)
            if m2_hp <= 0:
                return monster1

        # Monster 2 attacks Monster 1
        attack_roll = rng.randint(1, 20) + monster2.attack_bonus
        if attack_roll >= monster1.ac:
            m1_hp -= roll_damage(monster2.damage_dice, rng)
            if m1_hp <= 0:
                return monster2

    # Round cap reached — higher remaining HP wins.
    return monster1 if m1_hp >= m2_hp else monster2
