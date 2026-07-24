"""Tests for the rental-yield calculator."""

from renovation_quote.calculators.rental_yield import RentalYieldCalculator


def test_effective_rent_uses_occupancy():
    calc = RentalYieldCalculator(monthly_rent=30000, renovation_cost=600000, occupancy_rate=0.95)
    assert calc.effective_monthly_rent == 30000 * 0.95


def test_net_profit_deducts_management():
    calc = RentalYieldCalculator(
        monthly_rent=30000, renovation_cost=600000, occupancy_rate=1.0, management_rate=0.10
    )
    assert calc.monthly_net_profit == 30000 * 0.90


def test_total_investment_includes_property_value():
    calc = RentalYieldCalculator(monthly_rent=30000, renovation_cost=600000, property_value=4000000)
    assert calc.total_investment == 4600000


def test_payback_months():
    calc = RentalYieldCalculator(
        monthly_rent=10000, renovation_cost=270000, occupancy_rate=1.0, management_rate=0.10
    )
    # net profit = 9000/mo -> 270000/9000 = 30 months
    assert calc.payback_months == 30


def test_payback_infinite_when_no_profit():
    calc = RentalYieldCalculator(monthly_rent=0, renovation_cost=100000)
    assert calc.payback_months == float("inf")


def test_yield_zero_when_no_investment():
    calc = RentalYieldCalculator(monthly_rent=30000, renovation_cost=0, property_value=0)
    assert calc.gross_yield == 0.0
    assert calc.net_yield == 0.0
