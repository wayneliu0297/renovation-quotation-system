"""Quotation: aggregates categories into a final priced proposal."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models.cost_model import CostModel
from ..models.difficulty import DifficultyMultiplier

#: Default project-supervision fee, applied on top of the trade subtotal.
DEFAULT_SUPERVISION_RATE = 0.10


@dataclass
class Quotation:
    """A full renovation quote for one property.

    Attributes:
        project_name: Label shown on the proposal.
        categories: The renovation categories included in this quote.
        difficulty: The difficulty multiplier applied to eligible categories.
        supervision_rate: Site-supervision / management fee (fraction).
    """

    project_name: str = "Untitled Project"
    categories: list[CostModel] = field(default_factory=list)
    difficulty: DifficultyMultiplier = field(default_factory=DifficultyMultiplier)
    supervision_rate: float = DEFAULT_SUPERVISION_RATE

    # -- assembly ----------------------------------------------------------
    def add_category(self, category: CostModel) -> None:
        if category.items:
            self.categories.append(category)

    @property
    def difficulty_value(self) -> float:
        return float(self.difficulty)

    # -- totals ------------------------------------------------------------
    @property
    def trade_subtotal(self) -> float:
        """Sum of all category subtotals after the difficulty multiplier."""
        d = self.difficulty_value
        return sum(cat.subtotal(d) for cat in self.categories)

    @property
    def supervision_fee(self) -> float:
        return self.trade_subtotal * self.supervision_rate

    @property
    def grand_total(self) -> float:
        return self.trade_subtotal + self.supervision_fee

    # -- serialization -----------------------------------------------------
    def category_breakdown(self) -> list[dict]:
        d = self.difficulty_value
        return [cat.as_dict(d) for cat in self.categories]

    def as_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "difficulty": self.difficulty.breakdown(),
            "supervision_rate": self.supervision_rate,
            "trade_subtotal": self.trade_subtotal,
            "supervision_fee": self.supervision_fee,
            "grand_total": self.grand_total,
            "categories": self.category_breakdown(),
        }
