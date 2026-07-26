from typing import Dict, Any, Optional


class Monster:
    """Represents a D&D monster with its raw display attributes.

    This class validates required fields during initialization so that
    invalid API data fails fast with a clear error message.
    """

    def __init__(self, data: Dict[str, Any]):
        """Initialize a Monster from API response data.

        Validates required fields immediately (fail-fast error handling).

        Args:
            data: Dictionary containing monster data from the API

        Raises:
            ValueError: If required fields are missing or invalid
        """
        self._data = data

        # Basic attributes (with defaults)
        self.index = data.get("index", "")
        self.name = data.get("name", "Unknown")
        self.image_url = data.get("full_image_url")

        # Validate and extract required fields (fail fast)
        self._validate_and_extract_required_fields()

        # Parse attack data (optional — not all monsters attack)
        self._extract_attack()

    def _validate_and_extract_required_fields(self) -> None:
        """Validate and extract required fields from API data.

        Raises:
            ValueError: If any required field is missing or invalid
        """
        # Hit points (required)
        if "hit_points" not in self._data:
            raise ValueError(f"Monster '{self.name}' missing required 'hit_points' data")
        self._hp = self._data["hit_points"]

        # Armor class (required)
        armor_class = self._data.get("armor_class", [])
        if not armor_class or len(armor_class) == 0:
            raise ValueError(f"Monster '{self.name}' missing required 'armor_class' data")
        ac_value = armor_class[0].get("value")
        if ac_value is None:
            raise ValueError(f"Monster '{self.name}' has invalid 'armor_class' structure")
        self._ac = ac_value

        # Strength (required)
        if "strength" not in self._data:
            raise ValueError(f"Monster '{self.name}' missing required 'strength' data")
        self._strength = self._data["strength"]

    def _extract_attack(self) -> None:
        """Extract the first real attack's to-hit bonus and damage dice.

        Filters the actions list down to entries that have an attack_bonus
        (skipping Multiattack, special abilities, and other non-attack actions).
        Picks the first real attack found.
        """
        self._attack_bonus: Optional[int] = None
        self._damage_dice: Optional[str] = None

        actions = self._data.get("actions", [])
        for action in actions:
            # A real attack has an attack_bonus key with a numeric value
            if "attack_bonus" not in action or action["attack_bonus"] is None:
                continue

            self._attack_bonus = action["attack_bonus"]

            # Extract damage_dice from the damage list
            damage_list = action.get("damage", [])
            if damage_list:
                self._damage_dice = self._extract_damage_dice(damage_list[0])

            break  # Use the first real attack

    @staticmethod
    def _extract_damage_dice(damage_entry: Dict[str, Any]) -> Optional[str]:
        """Extract damage_dice from a damage entry.

        Handles two API formats:
        - Simple: {"damage_dice": "1d6+2", "damage_type": {...}}
        - Versatile (choose): {"choose": 1, "from": {"options": [{"damage_dice": "1d8+3"}, ...]}}

        Args:
            damage_entry: A single entry from the action's damage list

        Returns:
            The damage dice string (e.g. '1d6+2') or None
        """
        # Simple format: damage_dice directly on the entry
        if "damage_dice" in damage_entry:
            return damage_entry["damage_dice"]

        # Versatile/choose format: pick the first option
        from_data = damage_entry.get("from", {})
        options = from_data.get("options", [])
        if options and "damage_dice" in options[0]:
            return options[0]["damage_dice"]

        return None

    # Properties - lightweight accessors returning the validated values

    @property
    def hp(self) -> int:
        """Return the monster's hit points."""
        return self._hp

    @property
    def ac(self) -> int:
        """Return the monster's armor class (Defense)."""
        return self._ac

    @property
    def strength(self) -> int:
        """Return the monster's Strength score."""
        return self._strength

    @property
    def attack_bonus(self) -> Optional[int]:
        """Return the monster's first attack's to-hit bonus, or None."""
        return self._attack_bonus

    @property
    def damage_dice(self) -> Optional[str]:
        """Return the monster's first attack's damage dice (e.g. '1d6+2'), or None."""
        return self._damage_dice

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Monster(name='{self.name}', hp={self.hp}, ac={self.ac})"

