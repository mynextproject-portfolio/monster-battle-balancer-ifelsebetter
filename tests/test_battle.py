"""
Tests for battle simulator module.
"""

import pytest
from models.monster import Monster
from battle import simulate_battle, parse_damage_dice, roll_damage, MAX_ROUNDS


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
