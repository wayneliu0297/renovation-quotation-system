"""The 8 concrete renovation categories.

Each subclass of :class:`CostModel` represents one trade. Keeping them as
separate classes (rather than a single class with a ``type`` field) lets each
category override behaviour independently -- e.g. a category could apply a
different multiplier rule or add trade-specific validation later.
"""

from __future__ import annotations

from .cost_model import CostModel


class Demolition(CostModel):
    code = "demolition"
    display_name = "Demolition & Disposal"

    def description(self) -> str:
        return "Tear-out of existing structures and debris removal."


class Plumbing(CostModel):
    code = "plumbing"
    display_name = "Plumbing"

    def description(self) -> str:
        return "Water supply, drainage and pipework."


class Electrical(CostModel):
    code = "electrical"
    display_name = "Electrical"

    def description(self) -> str:
        return "Wiring, circuits, outlets and lighting."


class Carpentry(CostModel):
    code = "carpentry"
    display_name = "Carpentry & Partitions"

    def description(self) -> str:
        return "Built-in cabinetry, partitions and woodwork."


class Flooring(CostModel):
    code = "flooring"
    display_name = "Flooring"

    def description(self) -> str:
        return "Floor preparation and finished surfaces."


class Painting(CostModel):
    code = "painting"
    display_name = "Painting & Walls"

    def description(self) -> str:
        return "Surface prep, primer and paint for walls and ceilings."


class Bathroom(CostModel):
    code = "bathroom"
    display_name = "Bathroom"

    def description(self) -> str:
        return "Waterproofing, tiling and sanitary fittings."


class Kitchen(CostModel):
    code = "kitchen"
    display_name = "Kitchen"

    def description(self) -> str:
        return "Cabinets, countertops and kitchen fittings."


#: Registry of every category class, keyed by its ``code``.
CATEGORY_CLASSES: dict[str, type[CostModel]] = {
    cls.code: cls
    for cls in (
        Demolition,
        Plumbing,
        Electrical,
        Carpentry,
        Flooring,
        Painting,
        Bathroom,
        Kitchen,
    )
}

#: Preferred display order for output documents / UI.
CATEGORY_ORDER: list[str] = [
    "demolition",
    "plumbing",
    "electrical",
    "carpentry",
    "flooring",
    "painting",
    "bathroom",
    "kitchen",
]


def make_category(code: str) -> CostModel:
    """Instantiate an empty category by its code."""
    try:
        return CATEGORY_CLASSES[code]()
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unknown category code: {code!r}") from exc
