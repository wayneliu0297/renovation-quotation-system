"""LineItem: a single priced row inside a renovation category."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LineItem:
    """One quotable item, e.g. "Interior wall painting, 45 ping".

    Attributes:
        name: Human-readable description of the work.
        quantity: How many units.
        unit: Unit of measure (ping, m, set, piece ...).
        unit_price: Price per unit in TWD (before any multiplier).
    """

    name: str
    quantity: float
    unit: str
    unit_price: float

    @property
    def base_cost(self) -> float:
        """Cost before difficulty / category multipliers are applied."""
        return self.quantity * self.unit_price

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "unit_price": self.unit_price,
            "base_cost": self.base_cost,
        }
