"""Tests for the synthetic dataset generator."""

from pandas.testing import assert_frame_equal

from renovation_quote.data.synthetic import generate_dataset

EXPECTED_COLUMNS = {
    "area_ping",
    "floor",
    "has_elevator",
    "building_age",
    "condition",
    "difficulty_multiplier",
    "grand_total",
    "monthly_rent",
    "net_yield",
    "payback_months",
}


def test_shape_and_columns():
    df = generate_dataset(n=60, seed=1)
    assert len(df) == 60
    assert EXPECTED_COLUMNS.issubset(df.columns)


def test_no_missing_values():
    df = generate_dataset(n=60, seed=1)
    assert df.isna().sum().sum() == 0


def test_totals_are_positive():
    df = generate_dataset(n=60, seed=1)
    assert (df["grand_total"] > 0).all()
    assert (df["trade_subtotal"] <= df["grand_total"]).all()


def test_deterministic_given_seed():
    assert_frame_equal(generate_dataset(n=40, seed=7), generate_dataset(n=40, seed=7))
