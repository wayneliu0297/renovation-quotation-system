"""Generate a synthetic dataset of renovation quotes for analysis / modeling.

Every row is produced by the *same* OOP costing engine the app uses
(:class:`Quotation` + the category classes). Per-project noise is added to line
item quantities and unit prices, so the top-level survey features (area, floor,
age, condition) explain most — but not all — of the variance in the final
price. That leaves genuine signal for a machine-learning model to learn, plus a
realistic error floor to talk about.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..calculators.quotation import Quotation
from ..calculators.rental_yield import RentalYieldCalculator
from ..models.categories import (
    Bathroom,
    Carpentry,
    Demolition,
    Electrical,
    Flooring,
    Kitchen,
    Painting,
    Plumbing,
)
from ..models.difficulty import Condition, DifficultyMultiplier

# category class -> [(item name, quantity-per-ping, unit, base unit price TWD)]
# Quantities scale with floor area; prices are plausible market baselines.
_TEMPLATES = {
    Demolition: [
        ("Partition tear-out", 0.35, "m", 850),
        ("Debris removal", 0.08, "truck", 4500),
    ],
    Plumbing: [
        ("Water supply re-pipe", 0.03, "set", 28000),
        ("Drainage rework", 0.18, "point", 2200),
    ],
    Electrical: [
        ("Circuit rewiring", 0.03, "set", 42000),
        ("Outlets & switches", 0.80, "point", 650),
        ("Light fittings", 0.28, "piece", 1800),
    ],
    Carpentry: [
        ("Built-in cabinetry", 0.08, "set", 26000),
        ("Light partition", 0.30, "ping", 3800),
    ],
    Flooring: [
        ("Floor supply & lay", 0.95, "ping", 3200),
        ("Levelling", 0.95, "ping", 450),
    ],
    Painting: [
        ("Wall & ceiling paint", 3.20, "ping", 720),
        ("Crack filling", 3.20, "ping", 180),
    ],
    Bathroom: [
        ("Waterproofing", 0.14, "ping", 2600),
        ("Tiling", 0.14, "ping", 5200),
        ("Sanitary set", 0.035, "set", 32000),
    ],
    Kitchen: [
        ("Cabinets", 0.10, "m", 12500),
        ("Countertop", 0.10, "m", 8800),
    ],
}

# Condition levels + probability weights (normal is most common). We sample an
# index rather than the Enum members directly, because numpy would coerce the
# str-based Enum members into (mangled) numpy strings.
_CONDITIONS = list(Condition)
_CONDITION_P = [0.40, 0.30, 0.20, 0.10]


def _sample_survey(rng: np.random.Generator):
    area = float(np.round(rng.uniform(12, 50), 1))
    floor = int(rng.integers(1, 16))
    # Elevators are more common in higher / newer buildings.
    p_elevator = 0.25 + 0.50 * (floor >= 6)
    has_elevator = bool(rng.random() < p_elevator)
    building_age = int(rng.integers(3, 55))
    condition = _CONDITIONS[int(rng.choice(len(_CONDITIONS), p=_CONDITION_P))]
    return area, floor, has_elevator, building_age, condition


def _build_quotation(area, floor, has_elevator, building_age, condition, rng):
    difficulty = DifficultyMultiplier(
        floor=floor,
        has_elevator=has_elevator,
        building_age=building_age,
        condition=condition,
    )
    quote = Quotation(project_name="synthetic", difficulty=difficulty)
    project_noise = rng.lognormal(0.0, 0.06)  # site-wide swing
    for cls, items in _TEMPLATES.items():
        category = cls()
        for name, qty_per_ping, unit, price in items:
            qty = qty_per_ping * area * rng.lognormal(0.0, 0.15) * project_noise
            unit_price = price * rng.lognormal(0.0, 0.08)
            category.add(name, round(qty, 2), unit, round(unit_price))
        quote.add_category(category)
    return quote, difficulty


def generate_dataset(n: int = 800, seed: int = 42) -> pd.DataFrame:
    """Return a DataFrame of ``n`` synthetic renovation quotes.

    Columns: the survey features, the difficulty multiplier, per-category costs,
    the pricing totals, and rental-yield metrics. Deterministic given ``seed``.
    """
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    for _ in range(n):
        area, floor, has_elevator, building_age, condition = _sample_survey(rng)
        quote, difficulty = _build_quotation(
            area, floor, has_elevator, building_age, condition, rng
        )

        monthly_rent = area * rng.normal(950, 90) + rng.normal(0, 1500)
        monthly_rent = max(8000.0, float(np.round(monthly_rent, -2)))
        rental = RentalYieldCalculator(
            monthly_rent=monthly_rent,
            renovation_cost=quote.grand_total,
            occupancy_rate=0.95,
        )

        row: dict = {
            "area_ping": area,
            "floor": floor,
            "has_elevator": has_elevator,
            "building_age": building_age,
            "condition": condition.value,
            "difficulty_multiplier": difficulty.value,
        }
        for category in quote.category_breakdown():
            row[f"cost_{category['code']}"] = round(category["subtotal"])
        row["trade_subtotal"] = round(quote.trade_subtotal)
        row["supervision_fee"] = round(quote.supervision_fee)
        row["grand_total"] = round(quote.grand_total)
        row["monthly_rent"] = round(monthly_rent)
        row["net_yield"] = round(rental.net_yield, 4)
        row["payback_months"] = round(rental.payback_months, 1)
        rows.append(row)

    return pd.DataFrame(rows)
