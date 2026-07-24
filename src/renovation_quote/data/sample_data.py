"""Fake sample data for the demo. Not tied to any real company or project."""

from __future__ import annotations

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


def sample_categories() -> list:
    """Build the 8 categories pre-filled with representative line items."""
    demolition = Demolition()
    demolition.add("Existing partition tear-out", 12, "m", 850)
    demolition.add("Debris removal & haulage", 3, "truck", 4500)

    plumbing = Plumbing()
    plumbing.add("Water supply re-pipe", 1, "set", 28000)
    plumbing.add("Drainage rework", 6, "point", 2200)

    electrical = Electrical()
    electrical.add("Circuit rewiring", 1, "set", 42000)
    electrical.add("Outlets & switches", 24, "point", 650)
    electrical.add("Ceiling light fittings", 8, "piece", 1800)

    carpentry = Carpentry()
    carpentry.add("Built-in wardrobe", 2, "set", 26000)
    carpentry.add("Light partition wall", 9, "ping", 3800)

    flooring = Flooring()
    flooring.add("SPC flooring supply & lay", 28, "ping", 3200)
    flooring.add("Floor levelling", 28, "ping", 450)

    painting = Painting()
    painting.add("Wall & ceiling repaint", 96, "ping", 720)
    painting.add("Crack filling & priming", 96, "ping", 180)

    bathroom = Bathroom()
    bathroom.add("Waterproofing", 4, "ping", 2600)
    bathroom.add("Wall & floor tiling", 4, "ping", 5200)
    bathroom.add("Sanitary fittings set", 1, "set", 32000)

    kitchen = Kitchen()
    kitchen.add("Base & wall cabinets", 3, "m", 12500)
    kitchen.add("Countertop (quartz)", 3, "m", 8800)

    return [
        demolition,
        plumbing,
        electrical,
        carpentry,
        flooring,
        painting,
        bathroom,
        kitchen,
    ]


def sample_quotation() -> Quotation:
    """A complete, ready-to-render sample quote."""
    difficulty = DifficultyMultiplier(
        floor=5,
        has_elevator=False,
        building_age=38,
        condition=Condition.POOR,
    )
    quote = Quotation(
        project_name="Demo Unit — 3F Walk-up Renovation",
        difficulty=difficulty,
        supervision_rate=0.10,
    )
    for category in sample_categories():
        quote.add_category(category)
    return quote


def sample_rental_yield(renovation_cost: float) -> RentalYieldCalculator:
    """A sample rental-yield scenario for the demo unit."""
    return RentalYieldCalculator(
        monthly_rent=32000,
        renovation_cost=renovation_cost,
        property_value=0.0,
        occupancy_rate=0.95,
        management_rate=0.10,
    )
