"""CostModel: the abstract base class for every renovation category."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .line_item import LineItem


class CostModel(ABC):
    """Base class for a renovation category (painting, plumbing, ...).

    A category owns a list of :class:`LineItem` rows and knows how the global
    difficulty multiplier should be applied to it. Subclasses declare their
    identity (``code`` / ``display_name``) and whether they participate in the
    difficulty multiplier.
    """

    #: Short machine code, e.g. "paint". Set by each subclass.
    code: str = ""
    #: Human-facing category name, e.g. "Painting & Walls".
    display_name: str = ""
    #: Whether the global difficulty multiplier applies to this category.
    #: Some categories (e.g. appliances) are quoted at flat cost.
    applies_difficulty: bool = True

    def __init__(self, items: Iterable[LineItem] | None = None) -> None:
        self.items: list[LineItem] = list(items) if items else []

    # -- item management ---------------------------------------------------
    def add_item(self, item: LineItem) -> None:
        self.items.append(item)

    def add(self, name: str, quantity: float, unit: str, unit_price: float) -> LineItem:
        """Convenience factory that builds and appends a LineItem."""
        item = LineItem(name=name, quantity=quantity, unit=unit, unit_price=unit_price)
        self.items.append(item)
        return item

    # -- costing -----------------------------------------------------------
    @property
    def base_subtotal(self) -> float:
        """Sum of line items before any multiplier."""
        return sum(item.base_cost for item in self.items)

    def effective_multiplier(self, difficulty: float) -> float:
        """The multiplier actually used for this category.

        Categories that opt out of difficulty (``applies_difficulty=False``)
        always return ``1.0``. Subclasses may override for custom behaviour.
        """
        return difficulty if self.applies_difficulty else 1.0

    def subtotal(self, difficulty: float = 1.0) -> float:
        """Category subtotal after applying the difficulty multiplier."""
        return self.base_subtotal * self.effective_multiplier(difficulty)

    # -- description -------------------------------------------------------
    @abstractmethod
    def description(self) -> str:
        """A one-line summary of what this category covers."""
        raise NotImplementedError

    def as_dict(self, difficulty: float = 1.0) -> dict:
        return {
            "code": self.code,
            "display_name": self.display_name,
            "description": self.description(),
            "applies_difficulty": self.applies_difficulty,
            "multiplier": self.effective_multiplier(difficulty),
            "base_subtotal": self.base_subtotal,
            "subtotal": self.subtotal(difficulty),
            "items": [item.as_dict() for item in self.items],
        }

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<{type(self).__name__} items={len(self.items)} base={self.base_subtotal:.0f}>"
