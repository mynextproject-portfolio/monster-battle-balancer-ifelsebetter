"""
Tests for battle simulator module.
"""

import pytest
from models.monster import Monster
from battle import simulate_battle, parse_damage_dice, roll_damage, MAX_ROUNDS, run_monte_carlo, run_battle, BattleResult, is_fun_matchup, FUN_THRESHOLD_PCT


class TestDamageParsing:
    def test_parse_damage_dice_valid(self):
        assert parse_damage_dice("1d6+2") == (1, 6, 2)
        assert parse_damage_dice("2d8") == (2, 8, 0)
        assert parse_damage_dice("1d10-1") == (1, 10, -1)

    def test_parse_damage_dice_invalid(self):
        with pytest.raises(ValueError):
            parse_damage_dice("invalid")


class TestBattleSimulation:
    @pytest.fixture
    def goblin(self):
        return Monster({
            "name": "Goblin",
            "hit_points": 7,
            "armor_class": [{"value": 15}],
            "strength": 8,
            "actions": [{"name": "Scimitar", "attack_bonus": 4, "damage": [{"damage_dice": "1d6+2"}]}]
        })

    @pytest.fixture
    def orc(self):
        return Monster({
            "name": "Orc",
            "hit_points": 15,
            "armor_class": [{"value": 13}],
            "strength": 16,
            "actions": [{"name": "Greataxe", "attack_bonus": 5, "damage": [{"damage_dice": "1d12+3"}]}]
        })

    def test_reproducibility(self, goblin, orc):
        winner1 = simulate_battle(goblin, orc, seed=42)
        winner2 = simulate_battle(goblin, orc, seed=42)
        assert winner1.name == winner2.name

    def test_hp_not_mutated(self, goblin, orc):
        simulate_battle(goblin, orc, seed=10)
        assert goblin.hp == 7
        assert orc.hp == 15

    def test_no_attack_monster_loses(self, goblin):
        no_atk = Monster({
            "name": "Blob",
            "hit_points": 100,
            "armor_class": [{"value": 10}],
            "strength": 5,
            "actions": []
        })
        assert simulate_battle(no_atk, goblin, seed=1).name == "Goblin"
        assert simulate_battle(goblin, no_atk, seed=1).name == "Goblin"

    def test_both_no_attack(self):
        blob1 = Monster({"name": "Blob1", "hit_points": 100, "armor_class": [{"value": 10}], "strength": 5, "actions": []})
        blob2 = Monster({"name": "Blob2", "hit_points": 50, "armor_class": [{"value": 10}], "strength": 5, "actions": []})
        assert simulate_battle(blob1, blob2, seed=1).name == "Blob1"


class TestMonteCarlo:
    @pytest.fixture
    def goblin(self):
        return Monster({
            "name": "Goblin",
            "hit_points": 7,
            "armor_class": [{"value": 15}],
            "strength": 8,
            "actions": [{"name": "Scimitar", "attack_bonus": 4, "damage": [{"damage_dice": "1d6+2"}]}]
        })

    @pytest.fixture
    def orc(self):
        return Monster({
            "name": "Orc",
            "hit_points": 15,
            "armor_class": [{"value": 13}],
            "strength": 16,
            "actions": [{"name": "Greataxe", "attack_bonus": 5, "damage": [{"damage_dice": "1d12+3"}]}]
        })

    def test_percentages_sum_to_100(self, goblin, orc):
        m1_pct, m2_pct = run_monte_carlo(goblin, orc, num_simulations=1000)
        assert abs((m1_pct + m2_pct) - 100.0) < 0.01

    def test_percentages_are_stable(self, goblin, orc):
        """Same inputs always produce the same percentages (seeded per-sim)."""
        pct_a = run_monte_carlo(goblin, orc, num_simulations=1000)
        pct_b = run_monte_carlo(goblin, orc, num_simulations=1000)
        assert pct_a == pct_b

    def test_stronger_monster_wins_more(self):
        """A high-HP high-attack monster should beat a weak one most of the time."""
        weak = Monster({
            "name": "Weak",
            "hit_points": 5,
            "armor_class": [{"value": 10}],
            "strength": 6,
            "actions": [{"name": "Slap", "attack_bonus": 1, "damage": [{"damage_dice": "1d4"}]}]
        })
        strong = Monster({
            "name": "Strong",
            "hit_points": 50,
            "armor_class": [{"value": 18}],
            "strength": 20,
            "actions": [{"name": "Sword", "attack_bonus": 8, "damage": [{"damage_dice": "2d10+5"}]}]
        })
        m1_pct, m2_pct = run_monte_carlo(weak, strong, num_simulations=1000)
        assert m2_pct > 90  # Strong should dominate


class TestRunBattle:
    @pytest.fixture
    def goblin(self):
        return Monster({
            "name": "Goblin",
            "hit_points": 7,
            "armor_class": [{"value": 15}],
            "strength": 8,
            "actions": [{"name": "Scimitar", "attack_bonus": 4, "damage": [{"damage_dice": "1d6+2"}]}]
        })

    @pytest.fixture
    def orc(self):
        return Monster({
            "name": "Orc",
            "hit_points": 15,
            "armor_class": [{"value": 13}],
            "strength": 16,
            "actions": [{"name": "Greataxe", "attack_bonus": 5, "damage": [{"damage_dice": "1d12+3"}]}]
        })

    def test_returns_battle_result(self, goblin, orc):
        result = run_battle(goblin, orc, num_simulations=100)
        assert isinstance(result, BattleResult)

    def test_result_has_winner(self, goblin, orc):
        result = run_battle(goblin, orc, num_simulations=100)
        assert result.winner.name in ("Goblin", "Orc")

    def test_result_percentages_sum_to_100(self, goblin, orc):
        result = run_battle(goblin, orc, num_simulations=100)
        assert abs((result.monster1_win_pct + result.monster2_win_pct) - 100.0) < 0.01


class TestIsFunMatchup:
    def test_balanced_fight_is_fun(self):
        """A 60/40 matchup is a real contest."""
        assert is_fun_matchup(60.0, 40.0) is True

    def test_even_fight_is_fun(self):
        """A 50/50 matchup is the most fun."""
        assert is_fun_matchup(50.0, 50.0) is True

    def test_borderline_fight_is_fun(self):
        """Exactly at the 20% threshold — still fun."""
        assert is_fun_matchup(80.0, 20.0) is True
        assert is_fun_matchup(20.0, 80.0) is True

    def test_stomp_is_boring(self):
        """A 95/5 matchup is a stomp — boring."""
        assert is_fun_matchup(95.0, 5.0) is False

    def test_just_below_threshold_is_boring(self):
        """Just under 20% for the underdog — boring."""
        assert is_fun_matchup(80.1, 19.9) is False

    def test_run_battle_includes_is_fun(self):
        """run_battle populates the is_fun field."""
        strong = Monster({
            "name": "Strong",
            "hit_points": 50,
            "armor_class": [{"value": 18}],
            "strength": 20,
            "actions": [{"name": "Sword", "attack_bonus": 8, "damage": [{"damage_dice": "2d10+5"}]}]
        })
        weak = Monster({
            "name": "Weak",
            "hit_points": 5,
            "armor_class": [{"value": 10}],
            "strength": 6,
            "actions": [{"name": "Slap", "attack_bonus": 1, "damage": [{"damage_dice": "1d4"}]}]
        })
        result = run_battle(strong, weak, num_simulations=100)
        assert isinstance(result.is_fun, bool)
        # Strong vs Weak should be a stomp
        assert result.is_fun is False
