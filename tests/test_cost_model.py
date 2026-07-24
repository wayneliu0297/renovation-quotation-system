"""Tests for the cost model and quotation aggregation."""

from pytest import approx

from renovation_quote.calculators.quotation import Quotation
from renovation_quote.models.categories import Painting, make_category
from renovation_quote.models.difficulty import Condition, DifficultyMultiplier


def test_line_item_base_cost():
    cat = Painting()
    item = cat.add("Repaint", quantity=10, unit="ping", unit_price=700)
    assert item.base_cost == 7000
    assert cat.base_subtotal == 7000


def test_subtotal_applies_multiplier():
    cat = Painting()
    cat.add("Repaint", 10, "ping", 700)
    assert cat.subtotal(1.2) == 7000 * 1.2


def test_make_category_by_code():
    cat = make_category("kitchen")
    assert cat.code == "kitchen"
    assert cat.display_name == "Kitchen"


def test_quotation_totals():
    difficulty = DifficultyMultiplier(
        floor=5, has_elevator=False, building_age=40, condition=Condition.POOR
    )
    quote = Quotation(project_name="T", difficulty=difficulty, supervision_rate=0.10)

    demo = make_category("demolition")
    demo.add("Tear-out", 10, "m", 1000)  # 10,000 base
    quote.add_category(demo)

    m = difficulty.value
    expected_trade = 10000 * m
    assert quote.trade_subtotal == approx(expected_trade)
    assert quote.supervision_fee == approx(expected_trade * 0.10)
    assert quote.grand_total == approx(expected_trade * 1.10)


def test_empty_category_is_not_added():
    quote = Quotation()
    quote.add_category(Painting())  # no items
    assert quote.categories == []
