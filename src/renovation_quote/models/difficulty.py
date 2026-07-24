"""DifficultyMultiplier: turns building survey inputs into a 1.0x-1.5x factor."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

#: Hard bounds required by the spec.
MIN_MULTIPLIER = 1.0
MAX_MULTIPLIER = 1.5


class Condition(str, Enum):
    """Overall structural condition of the unit."""

    NORMAL = "normal"
    AGING = "aging"
    POOR = "poor"
    SEVERE = "severe"


#: Additive weight contributed by each condition level.
_CONDITION_WEIGHT = {
    Condition.NORMAL: 0.00,
    Condition.AGING: 0.05,
    Condition.POOR: 0.10,
    Condition.SEVERE: 0.15,
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class DifficultyMultiplier:
    """Compute a project-wide difficulty multiplier.

    The multiplier starts at 1.0 and accumulates small additive penalties for
    factors that genuinely make a renovation harder, then is clamped to the
    [1.0, 1.5] range.

    Attributes:
        floor: Floor the unit is on (1 = ground floor).
        has_elevator: Whether the building has an elevator.
        building_age: Age of the building in years.
        condition: Structural condition of the unit.
    """

    floor: int = 1
    has_elevator: bool = True
    building_age: int = 0
    condition: Condition = Condition.NORMAL

    # -- individual factors ------------------------------------------------
    @property
    def floor_factor(self) -> float:
        """Walk-up penalty: only meaningful with no elevator on high floors."""
        if self.has_elevator or self.floor < 4:
            return 0.0
        return (self.floor - 3) * 0.05

    @property
    def age_factor(self) -> float:
        return 0.10 if self.building_age > 30 else 0.0

    @property
    def condition_factor(self) -> float:
        condition = self.condition
        if not isinstance(condition, Condition):
            condition = Condition(condition)
        return _CONDITION_WEIGHT[condition]

    # -- result ------------------------------------------------------------
    @property
    def value(self) -> float:
        raw = 1.0 + self.floor_factor + self.age_factor + self.condition_factor
        return round(_clamp(raw, MIN_MULTIPLIER, MAX_MULTIPLIER), 3)

    def breakdown(self) -> dict:
        return {
            "floor_factor": self.floor_factor,
            "age_factor": self.age_factor,
            "condition_factor": self.condition_factor,
            "multiplier": self.value,
        }

    def __float__(self) -> float:
        return self.value
